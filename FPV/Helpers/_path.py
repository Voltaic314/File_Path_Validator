class Path:
    """Manages path state and provides stack-like operations."""

    def __init__(self, initial_path: str, sep: str = "/", relative: bool = True, file_added: bool = False):
        self.parts = initial_path.strip(sep).split(sep) if initial_path else []
        self.sep = sep
        self.relative = relative
        self.file_added = file_added
        self.actions_queue = []  # Store actions with priorities
        self.logs = {"actions": [], "issues": []}  # Unified logs for actions and validation issues

    def get_full_path(self) -> str:
        """Generate and return the cleaned path after applying all actions."""
        self.apply_actions()  # Apply pending actions before returning the path
        full_path = self.sep.join(self.parts)
        if self.relative:
            return f"{self.sep}{full_path}" if full_path else self.sep
        return full_path
    
    def get_path_length(self) -> int:
        """Get the length of the path."""
        return len('/'.join(self.parts))

    def add_part(self, part: str, is_file: bool = False):
        """Add a new part to the path."""
        if self.file_added:
            raise ValueError("Cannot add more parts after a file has been added.")
        self.parts.append(part)
        if is_file:
            self.file_added = True

    def remove_part(self, index: int):
        """Remove a part by its index."""
        if 0 <= index < len(self.parts):
            removed_part = self.parts.pop(index)
            if index == len(self.parts) and self.file_added:  # Removed the last part
                self.file_added = False
            return removed_part
        else:
            raise IndexError("Invalid index for path parts.")

    def set_part(self, index: int, part: str):
        """Replace a part at a specific index."""
        if 0 <= index < len(self.parts):
            self.parts[index] = part
        else:
            raise IndexError("Invalid index for path parts.")

    def add_action(self, action: dict, priority: int):
        """
        Add an action to the queue with a priority and log it for audit trail.
        
        Args:
            action (dict): The action details, including type, category, subtype, details, and reason.
            priority (int): Priority of the action (lower values are higher priority).
        """
        # Ensure action contains required fields
        required_fields = ["type", "category", "subtype", "details", "reason"]
        for field in required_fields:
            if field not in action:
                raise ValueError(f"Missing required field '{field}' in action log.")

        # Add priority to the action dictionary
        action["priority"] = priority

        # Add the action to the queue and sort by priority
        self.actions_queue.append(action)
        self.actions_queue.sort(key=lambda x: x["priority"])

        # Log the action for audit purposes
        self.logs["actions"].append(action)

    def apply_actions(self):
        """Apply all actions in the queue, sorted by priority."""
        # Sort the actions by priority before applying them
        self.actions_queue.sort(key=lambda x: x.get("priority", float("inf")))
        
        while self.actions_queue:
            action = self.actions_queue.pop(0)
            self.apply_action(action)

    def apply_action(self, action: dict):
        """Apply a single action to modify the path."""
        action_type = action.get("type")
        details = action.get("details", {})
        index = details.get("index")
        old_value = details.get("original")
        new_value = details.get("new_value")

        if action_type == "MODIFY" and index is not None:
            self.set_part(index, new_value)
        elif action_type == "REMOVE" and index is not None:
            self.remove_part(index)
        elif action_type == "ADD":
            self.add_part(new_value)

        # Log the action after applying it
        self.logs["actions"].append(action)

    def add_issue(self, issue: dict):
        """
        Log a validation issue for audit trail.
        
        Args:
            issue (dict): The issue details, including type, category, details, and reason.
        """
        # Ensure issue contains required fields
        required_fields = ["type", "category", "details", "reason"]
        for field in required_fields:
            if field not in issue:
                raise ValueError(f"Missing required field '{field}' in issue log.")

        # Add the issue to the logs
        self.logs["issues"].append(issue)


    def get_logs(self) -> dict:
        """Retrieve all logs."""
        return self.logs
