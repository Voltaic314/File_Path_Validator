import pytest
from FPV.Helpers._base import FPV_Base


class TestFPV_Base:
    
    def setup_method(self):
        # Setup mock values for `BaseService` attributes
        self.service = FPV_Base("mock/path/to/file.txt")
        self.service.max_length = 20
        self.service.invalid_characters = '<>:'
        self.service.restricted_names = {'restricted', 'invalid'}
        
    def test_valid_path(self):
        assert self.service.clean_and_validate_path("path_length", path=self.service.path) == "/mock/path/file.txt"

    def test_validate_path_length(self):
        # Exceeding `max_length` path should raise a ValueError
        service = FPV_Base("mock/path/with/very/long/filename.txt")
        service.max_length = 20
        with pytest.raises(ValueError) as excinfo:
            service.validate_path_length()
        assert "The specified path is too long" in str(excinfo.value)

    def test_truncate_path(self):
        # Test `truncate_path` method with a set `max_length`
        service = FPV_Base("mock/path/to/filename.txt")
        service.max_length = 20
        truncated_path = service.truncate_path(service.path)
        assert len(truncated_path) <= 20

    def test_validate_invalid_characters(self):
        # Path with invalid characters should raise a ValueError
        service = FPV_Base("invalid/path<>/file.txt")
        service.invalid_characters = '<>:'
        with pytest.raises(ValueError) as excinfo:
            service.validate_invalid_characters()
        assert "Invalid character" in str(excinfo.value)

    def test_remove_invalid_characters(self):
        service = FPV_Base("invalid<>path:/file.txt")
        service.invalid_characters = '<>:'
        cleaned_path = service.remove_invalid_characters(service.path)
        assert cleaned_path == "invalidpath/file.txt"

    def test_validate_restricted_names(self):
        # Test restricted name validation
        service = FPV_Base("mock/restricted/file.txt")
        service.restricted_names = {"restricted"}
        with pytest.raises(ValueError) as excinfo:
            service.validate_restricted_names()
        assert 'Restricted name "restricted" found' in str(excinfo.value)

    def test_remove_restricted_names(self):
        service = FPV_Base("mock/restricted/file.txt")
        service.restricted_names = {"restricted"}
        cleaned_path = service.remove_restricted_names(service.path)
        assert cleaned_path == "mock/file.txt"

    def test_validate_trailing_periods(self):
        # Validate that trailing periods in parts raise an error
        service = FPV_Base("mock/path./file.")
        with pytest.raises(ValueError) as excinfo:
            service.validate_if_part_ends_with_period()
        assert 'cannot end with a period' in str(excinfo.value)

    def test_remove_trailing_periods(self):
        service = FPV_Base("mock/path./file.")
        cleaned_path = service.remove_trailing_periods(service.path)
        assert cleaned_path == "mock/path/file"

    def test_validate_if_whitespace_around_parts(self):
        # Test leading/trailing whitespace validation
        service = FPV_Base("  mock/path/to/file  ")
        with pytest.raises(ValueError) as excinfo:
            service.validate_if_whitespace_around_parts()
        assert "Leading or trailing spaces are not allowed" in str(excinfo.value)

    def test_remove_whitespace_around_parts(self):
        service = FPV_Base("  mock / path / to / file  ")
        cleaned_path = service.remove_whitespace_around_parts(service.path)
        assert cleaned_path == "mock/path/to/file"

    def test_validate_empty_parts(self):
        # Test empty part validation in path
        service = FPV_Base("mock//to//file.txt")
        with pytest.raises(ValueError) as excinfo:
            service.validate_empty_parts()
        assert "Empty parts are not allowed" in str(excinfo.value)

    def test_remove_empty_parts(self):
        service = FPV_Base("mock//to//file.txt")
        cleaned_path = service.remove_empty_parts(service.path)
        assert cleaned_path == "mock/to/file.txt"
