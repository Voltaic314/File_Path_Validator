import pytest
from FPV.Helpers.sharefile import ShareFile


def test_sharefile_invalid_characters():
    # List of invalid characters for ShareFile
    invalid_characters = ':;*?"<>~'

    for char in invalid_characters:
        with pytest.raises(ValueError) as excinfo:
            ShareFile(f"valid/path/to/file{char}.txt").check_if_valid()
        assert f'Invalid character "{char}" found in:' in str(excinfo.value)
