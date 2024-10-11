import pytest
from FPV.Helpers.dropbox import Dropbox

def test_path_with_restricted_names():
    restricted_names = {
        ".lock", "CON", "PRN", "AUX", "NUL", 
        "COM0", "COM1", "COM2", "COM3", "COM4", 
        "COM5", "COM6", "COM7", "COM8", "COM9", 
        "LPT0", "LPT1", "LPT2", "LPT3", "LPT4", 
        "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    }

    for name in restricted_names:
        dropbox = Dropbox(f"{name}/file.txt")
        with pytest.raises(ValueError) as excinfo:
            dropbox.check_if_valid()
        assert f'Restricted name found in path: "{name}"' in str(excinfo.value)

def test_path_length_exceeds_limit():
    filename_without_ext = "a"  # A simple character to construct a long path
    long_path = (filename_without_ext * (260 // len(filename_without_ext))) + ".pdf"  # Creates a path longer than 260 characters
    dropbox = Dropbox(long_path)
    with pytest.raises(ValueError) as excinfo:
        dropbox.check_if_valid()
    assert "The specified path is too long." in str(excinfo.value)