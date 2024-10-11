import pytest
from FPV.Helpers._base_service import BaseService

class TestBaseService:

    def test_valid_path(self):
        service = BaseService("valid/path/to/file.txt")
        assert service.check_if_valid() is True
        assert service.get_cleaned_path() == "/valid/path/to/file.txt"

    def test_path_with_invalid_character(self):
        service = BaseService("invalid/path/to/file<>.txt")
        with pytest.raises(ValueError) as excinfo:
            service.check_if_valid()
        assert "Invalid character" in str(excinfo.value)

    def test_path_with_leading_trailing_spaces(self):
        service = BaseService("  invalid/path/to/file.txt  ")
        with pytest.raises(ValueError) as excinfo:
            service.check_if_valid()
        assert "Leading or trailing spaces found" in str(excinfo.value)

    def test_folder_name_ending_with_period(self):
        service = BaseService("folder_name.")
        with pytest.raises(ValueError) as excinfo:
            service.check_if_valid()
        assert 'Folder names cannot end with a period' in str(excinfo.value)

    def test_path_with_leading_space(self):
        service = BaseService(" leading_space/file.txt")
        with pytest.raises(ValueError) as excinfo:
            service.check_if_valid()
        assert 'Leading spaces are not allowed' in str(excinfo.value)

    def test_filename_without_extension(self):
        service = BaseService("folder_name/filename_without_extension")
        with pytest.raises(ValueError) as excinfo:
            service.check_if_valid()
        assert 'Filename must contain an extension' in str(excinfo.value)

    def test_get_cleaned_path(self):
        service = BaseService("   some/path/  ")
        assert service.get_cleaned_path() == "/some/path"
