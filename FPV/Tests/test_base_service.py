import pytest
from FPV.Helpers._base import FPV_Base
from FPV.Helpers._path import Path


# Mock subclass for FPV_Base
class MockFPV(FPV_Base):
    """Mock subclass of FPV_Base to test abstract behavior."""
    max_length = 20

    def __init__(self, path: str, **kwargs):
        super().__init__(path, **kwargs)

    def processing_methods(self):
        """Mock processing methods for the mock class."""
        return {
            "root": [lambda part, action: self.mock_process_method(part, action)],
            "folder": [lambda part, action: self.mock_process_method(part, action)],
            "file": [lambda part, action: self.mock_process_method(part, action)],
        }

    def mock_process_method(self, part, action):
        """Mock processing method."""
        if action == "validate" and "invalid" in part["part"]:
            self._path_helper.add_issue(
                {
                    "type": "issue",
                    "category": "MOCK_ISSUE",
                    "details": {"part": part["part"], "index": part["index"]},
                    "reason": f"Mock issue detected in part '{part['part']}'.",
                }
            )
        elif action == "clean":
            return part["part"].replace("invalid", "valid")
        return part["part"]


@pytest.fixture
def mock_path():
    """Create a mock path object for testing."""
    return "root/folder/invalid_file.txt"


@pytest.fixture
def mock_fpv(mock_path):
    """Create a mock FPV_Base instance for testing."""
    return MockFPV(mock_path, sep="/", auto_validate=False, auto_clean=False, relative=False, file_added=True)


def test_initialization(mock_fpv, mock_path):
    """Test initialization of FPV_Base and its mock subclass."""
    assert mock_fpv.path == mock_path.strip("/")
    assert isinstance(mock_fpv._path_helper, Path)
    assert mock_fpv.auto_validate is False
    assert mock_fpv.auto_clean is False


def test_get_logs(mock_fpv):
    """Test retrieving logs."""
    mock_fpv._path_helper.logs = {"actions": [], "issues": []}
    assert mock_fpv.get_logs() == {"actions": [], "issues": []}


def test_add_part():
    """Test adding a part to the path."""
    # Create a fresh mock path without a file added
    mock_path = "root/folder"
    mock_fpv = MockFPV(mock_path, sep="/", auto_validate=False, auto_clean=False, relative=False, file_added=False)
    mock_fpv.max_length = 100 # Set max length to a high value to avoid issues with path length

    # Add a new part
    mock_fpv.add_part("new_part", is_file=False, mode="validate")
    assert mock_fpv._path_helper.parts[-1]["part"] == "new_part"
    assert mock_fpv._path_helper.parts[-1]["is_file"] is False

    # Add a file to ensure is_file behavior is respected
    mock_fpv.add_part("new_file.txt", is_file=True, mode="validate")
    assert mock_fpv._path_helper.parts[-1]["part"] == "new_file.txt"
    assert mock_fpv._path_helper.parts[-1]["is_file"] is True

    # Adding another part now should raise an error since a file is already added
    with pytest.raises(ValueError, match="Cannot add more parts after a file has been added."):
        mock_fpv.add_part("should_fail")


def test_remove_part(mock_fpv):
    """Test removing a part from the path."""
    initial_length = len(mock_fpv._path_helper.parts)
    mock_fpv.remove_part(2, mode="validate")  # Removing "invalid_file.txt"
    assert len(mock_fpv._path_helper.parts) == initial_length - 1
    assert not any(part["part"] == "invalid_file.txt" for part in mock_fpv._path_helper.parts)


def test_clean(mock_fpv):
    """Test cleaning the path."""
    cleaned_path = mock_fpv.clean(validate_after_clean=True)
    assert "invalid" not in cleaned_path
    assert "valid_file.txt" in cleaned_path


def test_validate(mock_fpv):
    """Test validating the path."""
    with pytest.raises(ValueError) as excinfo:
        mock_fpv.validate(raise_error=True)
    issues = mock_fpv.get_logs()["issues"]
    assert len(issues) > 0
    assert "MOCK_ISSUE" in issues[0]["category"]
    assert "invalid_file.txt" in issues[0]["details"]["part"]


def test_process_invalid_characters(mock_fpv):
    """Test processing invalid characters."""
    part = {"index": 0, "part": "inva?lid", "is_file": False}
    mock_fpv.invalid_characters = "?*"
    cleaned_part = mock_fpv.process_invalid_characters(part, action="clean")
    assert cleaned_part == "invalid"
    mock_fpv.process_invalid_characters(part, action="validate")
    issues = mock_fpv.get_logs()["issues"]
    assert len(issues) > 0
    assert "INVALID_CHAR" in issues[0]["category"]


def test_process_path_length(mock_fpv):
    """Test processing path length."""
    mock_fpv.max_length = 10
    part = {"index": 1, "part": "very_long_part", "is_file": False}
    mock_fpv.process_path_length(part, action="validate")
    issues = mock_fpv.get_logs()["issues"]
    assert len(issues) > 0
    assert "PATH_LENGTH" in issues[0]["category"]
    assert issues[0]["details"]["index"] == 1


def test_processing_methods(mock_fpv):
    """Test processing methods delegation."""
    root_part = {"index": 0, "part": "root", "is_file": False}
    mock_fpv.processing_methods()["root"][0](root_part, "validate")
    issues = mock_fpv.get_logs()["issues"]
    assert len(issues) == 0  # No issues with valid root


def test_clean_with_processing_methods(mock_fpv):
    """Test cleaning with processing methods applied."""
    cleaned_path = mock_fpv.clean(validate_after_clean=False)
    assert "invalid" not in cleaned_path
    assert "valid_file.txt" in cleaned_path
