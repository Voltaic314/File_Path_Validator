import pytest
from FPV.Helpers.box import FPV_Box

def test_box_restricted_names():
    """Test that restricted file names for Box trigger validation errors."""
    restricted_names = {
        "outlook.pst", "quickbooks.qbb", "google_docs.gdoc", 
        "google_sheets.gsheet", "google_slides.gslides", "mac_package.pkg"
    }
    
    for name in restricted_names:
        with pytest.raises(ValueError) as excinfo:
            FPV_Box(f"{name}/folder/test.txt").validate()
        assert f'Restricted name "{name}" found in path.' in str(excinfo.value)

def test_box_path_length_exceeds_limit():
    """Test that paths exceeding Box's max length of 255 characters trigger errors."""
    long_path = "a" * 256  # Exceeds 255 characters
    with pytest.raises(ValueError) as excinfo:
        FPV_Box(f"{long_path}/file.txt").validate()
    assert "The specified path is too long. Maximum allowed is 255 characters." in str(excinfo.value)

def test_box_clean_whitespace_around_parts():
    """Test that the clean method removes whitespace around parts."""
    path_with_whitespace = "folder1 / folder2 / file.txt"
    box_validator = FPV_Box(path_with_whitespace)
    cleaned_path = box_validator.clean()
    assert cleaned_path == "/folder1/folder2/file.txt"

def test_box_clean_path():
    """Test the clean method, ensuring the path becomes Box-compliant."""
    path = "outlook.pst/folder/ test file .txt "
    box_validator = FPV_Box(path)
    cleaned_path = box_validator.clean()

    # Check that restricted names are removed
    assert "outlook.pst" not in cleaned_path

    # Ensure leading/trailing spaces and periods are removed
    assert "/ " not in cleaned_path 
    assert " .txt" not in cleaned_path
    assert not cleaned_path.endswith(".")

def test_box_no_invalid_characters():
    """Test that paths with unsupported Box characters trigger validation errors."""
    path_with_invalid_chars = "folder|name/file?.txt"
    with pytest.raises(ValueError) as excinfo:
        FPV_Box(path_with_invalid_chars).validate()
    assert "Invalid character" in str(excinfo.value)
