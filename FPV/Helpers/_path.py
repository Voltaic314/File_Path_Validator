class Path:
    """Manages path state and provides stack-like operations."""

    def __init__(self, initial_path: str, sep: str = "/"):
        self.parts = initial_path.strip(sep).split(sep) if initial_path else []
        self.sep = sep
        self.logs = {"actions": [], "issues": []}  # Unified logs for actions and validation issues

    def get_full_path(self) -> str:
        """Return the full path as a string."""
        return self.sep.join(self.parts)

    def add_part(self, part: str):
        """Add a new part to the path."""
        self.parts.append(part)

    def remove_part(self, index: int):
        """Remove a part by its index."""
        if 0 <= index < len(self.parts):
            self.parts.pop(index)
        else:
            raise IndexError("Invalid index for path parts.")

    def set_part(self, index: int, part: str):
        """Replace a part at a specific index."""
        if 0 <= index < len(self.parts):
            self.parts[index] = part
        else:
            raise IndexError("Invalid index for path parts.")

    def apply_action(self, action: dict):
        """Apply a cleaning action to modify the path."""
        action_type = action.get("action")
        old_value = action.get("item", {}).get("name")
        new_value = action.get("details", {}).get("new_value")

        if action_type == "MODIFY":
            self.parts = [new_value if p == old_value else p for p in self.parts]
        elif action_type == "REMOVE":
            self.parts = [p for p in self.parts if p != old_value]
        elif action_type == "ADD":
            self.parts.append(new_value)

        self.logs["actions"].append(action)

    def log_issue(self, issue: dict):
        """Log a validation issue."""
        self.logs["issues"].append(issue)

    def get_logs(self) -> dict:
        """Retrieve all logs."""
        return self.logs
