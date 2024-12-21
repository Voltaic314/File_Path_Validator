class Path:
    """Manages path state and provides stack-like operations."""

    def __init__(self, initial_path: str, sep: str = "/", relative: bool = True, file_added: bool = False):
        self.parts = []
        self.sep = sep
        self.relative = relative
        self.file_added = file_added
        self.actions_queue = []  # Store actions with priorities
        self.logs = {"actions": [], "issues": []}  # Unified logs for actions and validation issues
        self.path_length = 0 # currently until the other parts are added, this is 0.
        self.file_added_to_parts = False
        for i, part in enumerate(initial_path.split(sep)):
            self.add_part(part, is_file=(i == len(initial_path.split(sep)) - 1) and file_added)
        self.file_added_to_parts = True if file_added else False
        self.path_length = self.get_path_length()  # Initialize the starting path length

    def get_full_path(self) -> str:
        """Generate and return the cleaned path after applying all actions."""
        self.apply_actions()  # Apply pending actions before returning the path
        full_path = self.sep.join([p["part"] for p in self.parts])
        return f"{self.sep}{full_path}" if self.relative and full_path else full_path

    def get_parts_to_clean(self) -> list:
        """Retrieve all parts that need to be cleaned."""
        return [part for part in self.parts if part["cleaned_status"] == "unseen"]
    
    def get_parts_to_check(self) -> list:
        """Retrieve all parts that need to be checked."""
        return [part for part in self.parts if part["checked_status"] == "unseen"]
    
    def get_actions_queue(self) -> list:
        """Retrieve all actions in the queue."""
        return self.actions_queue
    
    def get_issues(self, clean_mode: bool = False) -> list:
        """Retrieve all validation issues."""
        if not clean_mode:
            self.logs["issues"]
        else:
            return [issue for issue in self.logs["issues"] if issue.get("details", {}).get("index") in [part["index"] for part in self.get_parts_to_clean()]]

    def get_pending_actions_for_part(self, index: int) -> list:
        """Retrieve all pending actions for parts."""
        return [action for action in self.actions_queue if action.get("details", {}).get("index") == index]
        
    def get_issues_for_part(self, index: int) -> list:
        """Retrieve all issues for a specific part."""
        return [issue for issue in self.logs["issues"] if issue.get("details", {}).get("index") == index]

    def get_path_length(self) -> int:
        """Get the total length of the path."""
        return len(self.sep.join([p["part"] for p in self.parts]))

    def get_index_by_part(self, part: str) -> int:
        """Retrieve the index of a part by its string value."""
        for entry in self.parts:
            if entry["part"] == part:
                return entry["index"]
        raise ValueError(f"Part '{part}' not found in the path.")

    def add_part(self, part: str, is_file: bool = False):
        """Add a new part to the path."""
        if self.file_added_to_parts:
            raise ValueError("Cannot add more parts after a file has been added.")

        new_index = len(self.parts)
        self.path_length += len(part) + len(self.sep)
        if is_file:
            self.file_added_to_parts = True
        self.parts.append({"index": new_index, "part": part, "cleaned_status": "unseen", "checked_status": "unseen", "is_file": is_file})


    def remove_part(self, index: int):
        """Remove a part from the path."""
        if 0 <= index < len(self.parts):
            removed_part = self.parts.pop(index)
            for i, entry in enumerate(self.parts):
                entry["index"] = i  # Reindex parts after removal
            if index == len(self.parts) and self.file_added:
                self.file_added = False
            self.path_length -= len(removed_part["part"]) + len(self.sep)
        else:
            raise IndexError("Invalid index for path parts.")

    def mark_part(self, index: int, state: str, status: str):
        """Mark a part with a specific status for checked or cleaned states."""
        valid_states = {"cleaned_status", "checked_status"}
        valid_statuses = {"unseen", "pending", "complete", "valid", "invalid"}
        if state not in valid_states:
            raise ValueError(f"Invalid state '{state}'. Must be one of {valid_states}.")
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of {valid_statuses}.")
        if 0 <= index < len(self.parts):
            self.parts[index][state] = status
        else:
            raise IndexError("Invalid index for path parts.")

    def add_action(self, action: dict, priority: int):
        """Add an action to the queue with a priority and log it for audit trail."""
        required_fields = ["type", "category", "subtype", "details", "reason"]
        for field in required_fields:
            if field not in action:
                raise ValueError(f"Missing required field '{field}' in action log.")

        action["priority"] = priority
        self.actions_queue.append(action)
        self.actions_queue.sort(key=lambda x: x["priority"])
        self.logs["actions"].append(action)

    def apply_actions(self):
        """Apply all actions in the queue, sorted by priority."""
        self.actions_queue.sort(key=lambda x: x.get("priority", float("inf")))
        while self.actions_queue:
            action = self.actions_queue.pop(0)
            self.apply_action(action)

        # Mark parts as "complete" if no actions remain for them
        for part in self.parts:
            if not any(action["details"].get("index") == part["index"] for action in self.actions_queue):
                if part['cleaned_status'] != 'pending':
                    continue
                part["cleaned_status"] = "complete"

    def apply_action(self, action: dict):
        """Apply a single action to modify the path."""
        action_type = action.get("subtype")
        details = action.get("details", {})
        index = details.get("index")
        new_value = details.get("new_value")

        if action_type == "MODIFY" and index is not None:
            self.parts[index]["part"] = new_value
        elif action_type == "REMOVE" and index is not None:
            self.remove_part(index)
        elif action_type == "ADD":
            self.add_part(new_value)

    def add_issue(self, issue: dict):
        """Log a validation issue for audit trail."""
        required_fields = ["type", "category", "details", "reason"]
        for field in required_fields:
            if field not in issue:
                raise ValueError(f"Missing required field '{field}' in issue log.")
        issue_index = issue["details"].get("index")
        if issue_index is not None:
            self.parts[issue_index]["checked_status"] = "issue"
        self.logs["issues"].append(issue)

    def get_logs(self) -> dict:
        """Retrieve all logs."""
        return self.logs
