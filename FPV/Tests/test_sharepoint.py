import pytest
from FPV.Helpers.sharepoint import SharePoint

def test_sharepoint_restricted_names():
    reserved_names = {
        ".lock", "CON", "PRN", "AUX", "NUL", 
        "COM0", "COM1", "COM2", "COM3", "COM4", 
        "COM5", "COM6", "COM7", "COM8", "COM9", 
        "LPT0", "LPT1", "LPT2", "LPT3", "LPT4", 
        "LPT5", "LPT6", "LPT7", "LPT8", "LPT9", 
        "_vti_", "desktop.ini"
    }
    
    for name in reserved_names:
        with pytest.raises(ValueError) as excinfo:
            SharePoint(f"{name}/folder/test.txt").check_if_valid()
        assert f'Restricted name found in path: "{name}"' in str(excinfo.value)

def test_sharepoint_restricted_prefix():
    prefix = "~$"
    with pytest.raises(ValueError) as excinfo:
        SharePoint(f"{prefix}temp/file.txt").check_if_valid()
    assert f'Restricted prefix found in path: "{prefix}temp"' in str(excinfo.value)

def test_sharepoint_restricted_root_folder():
    restricted_root_folder = "forms"
    with pytest.raises(ValueError) as excinfo:
        SharePoint(f"{restricted_root_folder}/folder/test.txt").check_if_valid()
    assert f'Restricted root level folder name found in path: "{restricted_root_folder}". Please make sure the first part of the path is not "{restricted_root_folder}"' in str(excinfo.value)

def test_sharepoint_path_length_exceeds_limit():
    long_path = "a" * 256  # Create a path longer than 255 characters
    with pytest.raises(ValueError) as excinfo:
        SharePoint(f"{long_path}/file.txt").check_if_valid()
    assert "The specified path is too long." in str(excinfo.value)
