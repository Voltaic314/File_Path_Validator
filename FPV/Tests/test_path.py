import pytest
from FPV.Helpers._path import Path  # Replace with the actual import path


def test_initialization():
    path = Path(initial_path="folder1/folder2/file.txt", sep="/", relative=True, file_added=True)
    assert path.get_full_path() == "/folder1/folder2/file.txt"
    assert path.path_length == len("folder1/folder2/file.txt")


def test_add_part():
    path = Path(initial_path="folder1", sep="/", relative=True)
    path.add_part("folder2")
    path.add_part("file.txt", is_file=True)
    assert path.get_full_path() == "/folder1/folder2/file.txt"
    assert path.parts[-1]["is_file"] is True


def test_remove_part():
    path = Path(initial_path="folder1/folder2/file.txt", sep="/", relative=True, file_added=True)
    path.remove_part(1)  # Remove 'folder2'
    assert path.get_full_path() == "/folder1/file.txt"
    assert path.parts[1]["part"] == "file.txt"


def test_mark_part():
    path = Path(initial_path="folder1/folder2", sep="/", relative=True)
    path.mark_part(0, state="cleaned_status", status="complete")
    assert path.parts[0]["cleaned_status"] == "complete"


def test_add_action():
    path = Path(initial_path="folder1", sep="/", relative=True)
    action = {
        "type": "action",
        "category": "MODIFY",
        "subtype": "MODIFY",
        "details": {"index": 0, "new_value": "new_folder"},
        "reason": "Renaming folder",
    }
    path.add_action(action, priority=1)
    assert path.actions_queue[0] == action
    assert action in path.logs["actions"]


def test_apply_actions():
    path = Path(initial_path="folder1/folder2", sep="/", relative=True)
    action = {
        "type": "action",
        "category": "MODIFY",
        "subtype": "MODIFY",
        "details": {"index": 0, "new_value": "renamed_folder"},
        "reason": "Renaming folder",
    }
    path.add_action(action, priority=1)
    path.apply_actions()
    assert path.parts[0]["part"] == "renamed_folder"
    assert len(path.actions_queue) == 0


def test_add_issue():
    path = Path(initial_path="folder1", sep="/", relative=True)
    issue = {
        "type": "issue",
        "category": "INVALID_NAME",
        "details": {"index": 0},
        "reason": "Invalid folder name",
    }
    path.add_issue(issue)
    assert issue in path.logs["issues"]


def test_find_all_parts_with_specific_issues():
    path = Path(initial_path="folder1/folder2", sep="/", relative=True)
    issue = {
        "type": "issue",
        "category": "INVALID_NAME",
        "details": {"index": 0},
        "reason": "Invalid folder name",
    }
    path.add_issue(issue)
    parts_with_issues = path.find_all_parts_with_specific_issues("INVALID_NAME")
    assert parts_with_issues[0]["part"] == "folder1"


def test_remove_issue():
    path = Path(initial_path="folder1", sep="/", relative=True)
    issue = {
        "type": "issue",
        "category": "INVALID_NAME",
        "details": {"index": 0},
        "reason": "Invalid folder name",
    }
    path.add_issue(issue)
    path.remove_issue(0, "INVALID_NAME")
    assert len(path.logs["issues"]) == 0


def test_remove_all_issues():
    path = Path(initial_path="folder1/folder2", sep="/", relative=True)
    issue1 = {
        "type": "issue",
        "category": "INVALID_NAME",
        "details": {"index": 0},
        "reason": "Invalid folder name",
    }
    issue2 = {
        "type": "issue",
        "category": "INVALID_NAME",
        "details": {"index": 1},
        "reason": "Invalid folder name",
    }
    path.add_issue(issue1)
    path.add_issue(issue2)
    path.remove_all_issues("INVALID_NAME")
    assert len(path.logs["issues"]) == 0


def test_get_logs():
    path = Path(initial_path="folder1", sep="/", relative=True)
    assert isinstance(path.get_logs(), dict)


def test_get_part_type():
    path = Path(initial_path="/folder1/folder2/file.txt", sep="/", relative=False, file_added=True)
    assert path.get_part_type(path.parts[0]) == "root"
    assert path.get_part_type(path.parts[1]) == "folder"
    assert path.get_part_type(path.parts[2]) == "file"


def test_get_path_length():
    path = Path(initial_path="folder1/folder2/file.txt", sep="/", relative=True)
    assert path.get_path_length() == len("folder1/folder2/file.txt")


def test_get_index_by_part():
    path = Path(initial_path="folder1/folder2/file.txt", sep="/", relative=True)
    assert path.get_index_by_part("folder2") == 1


if __name__ == "__main__":
    pytest.main()
