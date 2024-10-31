import pytest
from FPV.Helpers.onedrive import FPV_OneDrive

def test_onedrive_restricted_names():
    # OneDrive-specific restricted names to validate against
    reserved_names = {
        ".lock", "CON", "PRN", "AUX", "NUL", 
        "COM1", "COM2", "COM3", "COM4", "COM5", 
        "COM6", "COM7", "COM8", "COM9", 
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", 
        "LPT6", "LPT7", "LPT8", "LPT9", "_vti_", "desktop.ini"
    }
    
    for name in reserved_names:
        with pytest.raises(ValueError) as excinfo:
            FPV_OneDrive(f"{name}/folder/test.txt").validate()
        assert f'Restricted name "{name}" found in path.' in str(excinfo.value)

def test_onedrive_restricted_prefix():
    # Test that paths with the restricted "~$" prefix raise an error
    prefix = "~$"
    with pytest.raises(ValueError) as excinfo:
        FPV_OneDrive(f"{prefix}temp/file.txt").validate()
    assert f'Restricted prefix "{prefix}" found in path part: "{prefix}temp"' in str(excinfo.value)

def test_onedrive_restricted_root_folder():
    # Validate that "forms" cannot be the first part of the path in OneDrive
    restricted_root_folder = "forms"
    with pytest.raises(ValueError) as excinfo:
        FPV_OneDrive(f"{restricted_root_folder}/folder/test.txt").validate()
    assert f'Restricted root folder "{restricted_root_folder}" found at path root: "{restricted_root_folder}"' in str(excinfo.value)

def test_onedrive_clean_path():
    # Example path with mixed violations for OneDrive
    path = "~$temp/.lock/forms/folder/invalid#chars.txt"
    onedrive = FPV_OneDrive(path, auto_clean=False)
    cleaned_path = onedrive.clean()

    # Assertions for cleaned path to ensure it is OneDrive-compliant
    assert "~$" not in cleaned_path
    assert ".lock" not in cleaned_path
    assert "forms" not in cleaned_path.split('/')[0]  # Ensure "forms" is not at the root level
    assert "#" not in cleaned_path  # Invalid character check
    assert cleaned_path == "/temp/forms/folder/invalidchars.txt"
