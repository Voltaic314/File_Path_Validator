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

    def test_path_with_leading_space(self):
        service = BaseService(" leading_space/file.txt")
        with pytest.raises(ValueError) as excinfo:
            service.check_if_valid()
        assert 'leading' in str(excinfo.value).lower()

    def test_path_with_trailing_space(self):
        service = BaseService("invalid/path/to/file.txt  ")
        with pytest.raises(ValueError) as excinfo:
            service.check_if_valid()
        assert "trailing" in str(excinfo.value).lower()

    def test_folder_name_ending_with_period(self):
        service = BaseService("folder_name./file.txt")
        print(service.path)
        print(service.path_parts)
        with pytest.raises(ValueError) as excinfo:
            service.check_if_valid()
        assert 'Folder names cannot end with a period' in str(excinfo.value)

    def test_space_in_folder_name(self):
        service = BaseService("folder name/file.txt")
        assert service.check_if_valid() is True
        service = BaseService("folder name /file.txt")
        with pytest.raises(ValueError) as excinfo:
            service.check_if_valid()
        assert 'trailing' in str(excinfo.value).lower()
        service = BaseService(" folder name/file.txt")
        with pytest.raises(ValueError) as excinfo:
            service.check_if_valid()
        assert 'leading' in str(excinfo.value).lower()

    def test_filename_without_extension(self):
        service = BaseService("folder_name/filename_without_extension")
        with pytest.raises(ValueError) as excinfo:
            service.check_if_valid()
        assert 'must contain an extension' in str(excinfo.value).lower()

    def test_get_cleaned_path(self):
        service = BaseService("   some/path/file.txt  ")
        assert service.get_cleaned_path() == "/some/path/file.txt"
    
    def test_get_cleaned_path_with_validation(self):
        # Testing cleaned path validation
        service = BaseService("   invalid<>/path/file.txt  ")
        cleaned_path = service.get_cleaned_path(raise_error=False)
        assert cleaned_path == "/invalid/path/file.txt"

    def test_truncate_filepath(self):
        path = "test/" * 300 + "file.txt"
        truncated_path = BaseService.truncate_filepath(path, max_length=255)
        assert len(truncated_path) == 255
        # testing raising an exception if the filename is too long
        with pytest.raises(ValueError) as excinfo:
            BaseService.truncate_filepath("test"*300 + ".txt", max_length=255)
        assert "Filename is too long" in str(excinfo.value)
