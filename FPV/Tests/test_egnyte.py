import pytest
from FPV.Helpers.egnyte import FPV_Egnyte


def test_egnyte_restricted_names():
    restricted_names = {
        ".ds_store", 
        ".metadata_never_index", 
        ".thumbs.db", 
        "powerpoint temp", 
        "desktop.ini", 
        "icon\r", 
        ".data", 
        ".tmp"
    }
    for name in restricted_names:
        with pytest.raises(ValueError) as excinfo:
            FPV_Egnyte(f"{name}/folder/test.txt").validate()
        assert f'Restricted name "{name}" found in path.' in str(excinfo.value)


def test_egnyte_part_length_exceeds_limit():
    long_part = "a" * 246  # Create a part longer than 245 characters
    with pytest.raises(ValueError) as excinfo:
        FPV_Egnyte(f"{long_part}/folder/test.txt").validate()
    assert f"Path component exceeds 245 characters: '{long_part}'" in str(excinfo.value)


def test_egnyte_restricted_suffixes():
    restricted_suffixes = [
        ".", "~", "._attribs_", "._rights_", "._egn_", "_egnmeta", 
        ".tmp", "-spotlight", ".ac$", ".sv$", ".~vsdx"
    ]
    for suffix in restricted_suffixes:
        with pytest.raises(ValueError) as excinfo:
            FPV_Egnyte(f"folder_name{suffix}/file.txt").validate()
        assert f"Path component 'folder_name{suffix}' has restricted suffix: '{suffix}'" in str(excinfo.value)


def test_egnyte_restricted_prefixes():
    restricted_prefixes = ["._", ".~", "word work file", "_egn_.", ".smbdelete", ".spotlight-"]
    for prefix in restricted_prefixes:
        with pytest.raises(ValueError) as excinfo:
            FPV_Egnyte(f"{prefix}folder_name/file.txt").validate()
        assert f"Path component '{prefix}folder_name' has restricted prefix: '{prefix}'" in str(excinfo.value)


def test_egnyte_tilde_suffix_combinations():
    starts_with_tilde_endings = [".idlk", ".xlsx", ".pptx"]
    for ending in starts_with_tilde_endings:
        with pytest.raises(ValueError) as excinfo:
            FPV_Egnyte(f"~folder{ending}/file.txt").validate()
        assert f"Path component '~folder{ending}' starts with '~' and ends with '{ending}'" in str(excinfo.value)


def test_egnyte_tilde_dollar_suffix_combinations():
    starts_with_tilde_dollar_endings = [
        ".doc", ".docx", ".rtf", ".ppt", ".pptx", 
        ".xlsm", ".sldlfp", ".slddrw", ".sldprt", ".sldasm"
    ]
    for ending in starts_with_tilde_dollar_endings:
        with pytest.raises(ValueError) as excinfo:
            FPV_Egnyte(f"~$folder{ending}/file.txt").validate()
        assert f"Path component '~$folder{ending}' starts with '~$' and ends with '{ending}'" in str(excinfo.value)


def test_egnyte_temp_patterns():
    temp_patterns = [
        "atmp1234",  # AutoCAD temp pattern
        "file.sas.b73",  # SAS temp file
        "aaA38221",  # PDF temp file pattern
        "example.$$$"  # Files ending with .$$$
    ]
    for temp_name in temp_patterns:
        with pytest.raises(ValueError) as excinfo:
            FPV_Egnyte(f"{temp_name}/file.txt").validate()
        assert f"Path component '{temp_name}' matches restricted temporary file pattern." in str(excinfo.value)


def test_egnyte_clean_path():
    # Example path with mixed violations, e.g., invalid characters, restricted prefixes, suffixes, and names
    path = "._ds_store/temp_folder_name_with_.docx"
    egnyte = FPV_Egnyte(path, auto_clean=False)
    egnyte.max_length = 5000
    egnyte.part_length = 245
    cleaned_path = egnyte.clean()
    
    # Assert that the cleaned path no longer has restricted patterns
    assert ".ds_store" not in cleaned_path
    assert "|" not in cleaned_path
    assert ".tmp" not in cleaned_path
    assert cleaned_path == "/ds_store/temp_folder_name_with_.docx"
