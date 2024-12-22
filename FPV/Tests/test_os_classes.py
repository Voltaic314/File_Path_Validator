from FPV import FPV_MacOS


def test_process_leading_periods():
    """Test the process_leading_periods method for MacOS."""
    # Mock path with leading periods in folder names
    mock_path = "/.hidden_folder/.another_hidden_folder/file.txt"
    
    # Instantiate FPV_MacOS object
    validator = FPV_MacOS(mock_path, auto_validate=False, auto_clean=False, relative=True, file_added=True)

    # Validate the path
    issues = validator.validate(raise_error=False)

    # Check that issues are correctly identified for leading periods
    assert len(issues) == 2  # Two leading period issues for folders
    assert any(issue["category"] == "LEADING_PERIOD" for issue in issues)
    assert issues[0]["details"]["part"] == ".hidden_folder"
    assert issues[1]["details"]["part"] == ".another_hidden_folder"

    # Clean the path
    cleaned_path = validator.clean()

    # Check the cleaned path
    assert cleaned_path == "/hidden_folder/another_hidden_folder/file.txt"

    # Revalidate the cleaned path
    issues_after_clean = validator.validate(raise_error=False)

    # Ensure no issues remain after cleaning
    assert len(issues_after_clean) == 0
