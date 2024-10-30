import pytest
from FPV.Helpers.sharepoint import SharePoint

def test_sharepoint_restricted_names():
    restricted_names = {
        ".lock", "CON", "PRN", "AUX", "NUL", 
        "COM1", "COM2", "COM3", "COM4", "COM5", 
        "COM6", "COM7", "COM8", "COM9", 
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", 
        "LPT6", "LPT7", "LPT8", "LPT9", "_vti_", "desktop.ini"
    }
    
    for name in restricted_names:
        with pytest.raises(ValueError) as excinfo:
            SharePoint(f"{name}/folder/test.txt").validate()
        assert f'Restricted name "{name}" found in path.' in str(excinfo.value)

def test_sharepoint_restricted_prefix():
    # Test that a path part starting with the restricted prefix raises an error
    prefix = "~$"
    with pytest.raises(ValueError) as excinfo:
        SharePoint(f"{prefix}temp/file.txt").validate()
    assert f'Restricted prefix "{prefix}" found in path part: "{prefix}temp"' in str(excinfo.value)

def test_sharepoint_restricted_root_folder():
    # Test that the restricted root folder ("forms") as the first path component raises an error
    restricted_root_folder = "forms"
    with pytest.raises(ValueError) as excinfo:
        SharePoint(f"{restricted_root_folder}/folder/test.txt").validate()
    assert f'Restricted root folder "{restricted_root_folder}" found at path root: "{restricted_root_folder}"' in str(excinfo.value)

def test_sharepoint_clean_path():
    # Test that SharePoint cleaning handles specific restricted elements properly
    path = "~$temp/.lock/forms/folder"
    sharepoint = SharePoint(path, auto_clean=False)
    cleaned_path = sharepoint.clean()

    # Assert that restricted elements have been removed or adjusted
    assert "~$" not in cleaned_path
    assert ".lock" not in cleaned_path
    assert "forms" not in cleaned_path.split('/')[0]  # Ensure "forms" is not the root folder
    assert cleaned_path == "/temp/forms/folder"
