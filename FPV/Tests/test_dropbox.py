import pytest
from FPV.Helpers.dropbox import FPV_Dropbox

class TestFPV_Dropbox:

    def test_invalid_characters(self):
        # Confirm Dropbox-specific invalid characters are flagged
        dropbox = FPV_Dropbox("invalid<path|file.txt")
        with pytest.raises(ValueError, match="Invalid character"):
            dropbox.validate_invalid_characters()

    def test_path_length_exceeds_limit(self):
        # Confirm Dropbox-specific max length of 260 characters is enforced
        long_path = "a" * 261  # Exceeds Dropbox max length
        dropbox = FPV_Dropbox(long_path)
        with pytest.raises(ValueError, match="The specified path is too long"):
            dropbox.validate_path_length()

    def test_restricted_names(self):
        # Test Dropbox-specific restricted names are recognized
        dropbox = FPV_Dropbox("COM1/file.txt")
        with pytest.raises(ValueError, match='Restricted name "COM1" found in path'):
            dropbox.validate_restricted_names()
