import pytest
from FPV.Helpers.sharepoint import FPV_SharePoint

def test_sharepoint_restricted_names():
    restricted_names = {
        ".lock", "CON", "PRN", "AUX", "NUL", 
        "COM1", "COM2", "COM3", "COM4", "COM5", 
        "COM6", "COM7", "COM8", "COM9", 
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", 
        "LPT6", "LPT7", "LPT8", "LPT9", "_vti_", "desktop.ini"
    }
    
    for name in restricted_names:
        with pytest.raises(ValueError) as excinfo:
            FPV_SharePoint(f"{name}/folder/test.txt").validate()
        assert f'Restricted name "{name}" found in path.' in str(excinfo.value)

def test_sharepoint_restricted_prefix():
    # Test that a path part starting with the restricted prefix raises an error
    prefix = "~$"
    with pytest.raises(ValueError) as excinfo:
        FPV_SharePoint(f"{prefix}temp/file.txt").validate()
    assert f'Restricted prefix "{prefix}" found in path part: "{prefix}temp"' in str(excinfo.value)

def test_sharepoint_restricted_root_folder():
    # Test that the restricted root folder ("forms") as the first path component raises an error
    restricted_root_folder = "forms"
    with pytest.raises(ValueError) as excinfo:
        FPV_SharePoint(f"{restricted_root_folder}/folder/test.txt").validate()
    assert f'Restricted root folder "{restricted_root_folder}" found at path root: "{restricted_root_folder}"' in str(excinfo.value)

def test_sharepoint_clean_path():
    # Test that SharePoint cleaning handles specific restricted elements properly
    path = "~$temp/.lock/forms/folder"
    sharepoint = FPV_SharePoint(path, auto_clean=False)
    cleaned_path = sharepoint.clean()

    # Assert that restricted elements have been removed or adjusted
    assert "~$" not in cleaned_path
    assert ".lock" not in cleaned_path
    assert "forms" not in cleaned_path.split('/')[0]  # Ensure "forms" is not the root folder
    assert cleaned_path == "/temp/forms/folder"

def test_sharepoint_site_domain_invalid_characters():
    # Test that an invalid site domain raises an error
    invalid_site_domain = "example.com/"
    with pytest.raises(ValueError) as excinfo:
        FPV_SharePoint(f"https://{invalid_site_domain}/folder/test.txt").validate()
    assert f'Invalid character "/" found in site domain: "{invalid_site_domain}"' in str(excinfo.value)
    invalid_site_domain = "example$"
    with pytest.raises(ValueError) as excinfo:
        FPV_SharePoint(f"https://{invalid_site_domain}.sharepoint.com/folder/test.txt").validate()
    assert f'Invalid characters found in site domain: "{invalid_site_domain}"' in str(excinfo.value)

def test_sharepoint_site_domain_restricted_names():
    # Test that a site domain with a restricted name raises an error
    restricted_site_domain = "CON"
    with pytest.raises(ValueError) as excinfo:
        FPV_SharePoint(f"https://{restricted_site_domain}.sharepoint.com/folder/test.txt").validate()
    assert f'Restricted name "{restricted_site_domain}" found in site domain' in str(excinfo.value)

def test_sharepoint_site_domain_restricted_prefix():
    # Test that a site domain starting with the restricted prefix raises an error
    restricted_prefix = "~$"
    with pytest.raises(ValueError) as excinfo:
        FPV_SharePoint(f"https://{restricted_prefix}example.sharepoint.com/folder/test.txt").validate()
    assert f'Restricted prefix "{restricted_prefix}" found in site domain: "{restricted_prefix}example"' in str(excinfo.value)

# now test with whitespace around site domain
def test_sharepoint_site_domain_whitespace():
    # Test that a site domain with leading or trailing whitespace raises an error
    site_domain = " example.sharepoint.com "
    with pytest.raises(ValueError) as excinfo:
        FPV_SharePoint(f"https://{site_domain}/folder/test.txt").validate()
    assert f'Leading or trailing spaces are not allowed in: "{site_domain}"' in str(excinfo.value)
    site_domain = "example .sharepoint.com"
    with pytest.raises(ValueError) as excinfo:
        FPV_SharePoint(f"https://{site_domain}/folder/test.txt").validate()
    assert f'Leading or trailing spaces are not allowed in: "{site_domain}"' in str(excinfo.value)

def test_sharepoint_site_domain_ending_with_period():
    # Test that a site domain ending with a period raises an error
    site_domain = "example.sharepoint.com."
    with pytest.raises(ValueError) as excinfo:
        FPV_SharePoint(f"https://{site_domain}/folder/test.txt").validate()
    assert f'"{site_domain}" cannot end with a period.' in str(excinfo.value)
    site_domain = "example..sharepoint.com"
    with pytest.raises(ValueError) as excinfo:
        FPV_SharePoint(f"https://{site_domain}/folder/test.txt").validate()
    assert f'"example.." cannot end with a period.' in str(excinfo.value)

def test_sharepoint_site_domain_cleaning():
    # Test that SharePoint cleaning handles site domain restrictions properly
    site_domain = " example.sharepoint.com "
    sharepoint = FPV_SharePoint(f"https://{site_domain}/folder/test.txt", auto_clean=False)
    cleaned_path = sharepoint.clean()

    # Assert that site domain has been cleaned
    assert cleaned_path == "https://example.sharepoint.com/sites/folder/test.txt"
    assert cleaned_path == sharepoint.clean(raise_error=False)