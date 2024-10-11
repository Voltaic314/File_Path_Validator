import pytest
from FPV.Helpers._os_classes import Windows, MacOS, Linux


def test_windows_reserved_folder_names():
    reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "LPT1"]
    for name in reserved_names:
        with pytest.raises(ValueError) as excinfo:
            Windows(f"{name}/folder/test.txt").check_if_valid()
        assert f"Restricted name found in path: \"{name}\"" in str(excinfo.value)


def test_macos_reserved_folder_names():
    reserved_names = [
        ".DS_Store",
        "Icon\\r",
        "._myfile"
    ]
    
    for name in reserved_names:
        with pytest.raises(ValueError) as excinfo:
            MacOS(f"{name}/folder/test.txt").check_if_valid()
        assert f"Restricted name found in path: \"{name}\"" in str(excinfo.value)


# really no linux restrictions to be honest... 
# Something something linux master race something something
def test_linux_reserved_folder_names():
    pass 
