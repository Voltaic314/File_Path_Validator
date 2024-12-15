import pytest
from FPV.Helpers._os_classes import FPV_Windows, FPV_MacOS, FPV_Linux


class TestFPV_Windows:
    def test_reserved_folder_names(self):
        reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "LPT1"]
        for name in reserved_names:
            with pytest.raises(ValueError) as excinfo:
                FPV_Windows(f"{name}/folder/file.txt", sep='/').validate()
            assert f'Restricted name "{name}"' in str(excinfo.value)

    def test_invalid_characters(self):
        # Windows path with invalid characters should raise ValueError
        invalid_path = "invalid<>|?*:/path/file.txt"
        with pytest.raises(ValueError) as excinfo:
            FPV_Windows(invalid_path, sep='/').validate_invalid_characters()
        assert "Invalid character" in str(excinfo.value)

    def test_drive_letter_check(self):
        # Windows paths must start with a valid drive letter if `relative` is False
        with pytest.raises(ValueError) as excinfo:
            FPV_Windows("/InvalidDriveLetter/path", relative=False, sep='/').validate_drive_letter()
        assert "Invalid or missing drive letter" in str(excinfo.value)


class TestFPV_MacOS:
    def test_reserved_folder_names(self):
        reserved_names = [".DS_Store", "._myfile"]
        for name in reserved_names:
            with pytest.raises(ValueError) as excinfo:
                FPV_MacOS(f"folder/{name}").validate()
            assert f'Restricted name "{name}"' in str(excinfo.value)

    def test_whitespace_around_parts(self):
        # Path with leading or trailing whitespace should raise ValueError
        macos_path = " folder_name /file.txt "
        with pytest.raises(ValueError) as excinfo:
            FPV_MacOS(macos_path).validate_if_whitespace_around_parts()
        assert "Leading or trailing spaces are not allowed" in str(excinfo.value)


class TestFPV_Linux:
    def test_null_character(self):
        # Linux path with null character should raise ValueError
        invalid_path = "folder_name/invalid\0file.txt"
        with pytest.raises(ValueError) as excinfo:
            FPV_Linux(invalid_path).validate_null_character()
        assert 'Null character "\\0" is not allowed' in str(excinfo.value)

    def test_clean_null_character(self):
        # Path with null character should be cleaned by removing it
        linux_path = "folder_name/invalid\0file.txt"
        cleaned_path = FPV_Linux(linux_path).clean(raise_error=False)
        assert "\0" not in cleaned_path
