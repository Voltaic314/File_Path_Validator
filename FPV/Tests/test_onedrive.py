from FPV.Helpers.onedrive import FPV_OneDrive


def test_process_restricted_prefix():
    """Test processing of restricted prefixes in OneDrive paths."""
    path = "~$restricted_folder/file.txt"
    onedrive = FPV_OneDrive(path, sep="/", auto_validate=False, auto_clean=False)
    
    # Validate the path and expect an issue for restricted prefix
    issues = onedrive.validate(raise_error=False)
    restricted_prefix_issues = [issue for issue in issues if issue["category"] == "RESTRICTED_PREFIX"]
    assert len(restricted_prefix_issues) == 1
    assert restricted_prefix_issues[0]["details"]["part"] == "~$restricted_folder"

    # Clean the path and verify the prefix is removed
    cleaned_path = onedrive.clean()
    assert cleaned_path == "/restricted_folder/file.txt"
    assert "~$" not in cleaned_path