import pytest
from FPV.Helpers.egnyte import Egnyte

def test_egnyte_reserved_names():
    reserved_names = {
        ".ds_store", 
        ".metadata_never_index", 
        ".thumbs.db", 
        "powerpoint temp", 
        "desktop.ini", 
    }
    
    for name in reserved_names:
        with pytest.raises(ValueError) as excinfo:
            Egnyte(f"{name}/folder/test.txt").check_if_valid()
        assert f"Restricted name found in path: \"{name}\"" in str(excinfo.value)

def test_egnyte_part_length_exceeds_limit():
    long_part = "a" * 246  # Create a part longer than 245 characters
    with pytest.raises(ValueError) as excinfo:
        Egnyte(f"{long_part}/folder/test.txt").check_if_valid()
    assert f"Path component exceeds 245 characters: \"{long_part}\"" in str(excinfo.value)

def test_egnyte_name_ends_with_restricted_suffix():
    for suffix in ['~']:
        with pytest.raises(ValueError) as excinfo:
            Egnyte(f"folder_name{suffix}/file.txt").check_if_valid()
        assert f"Name ends with restricted suffix \"{suffix}\": \"folder_name{suffix}\"" in str(excinfo.value)

def test_egnyte_name_starts_with_restricted_prefix():
    for prefix in ['._', '.~']:
        with pytest.raises(ValueError) as excinfo:
            Egnyte(f"{prefix}folder_name/file.txt").check_if_valid()
        assert f"Name starts with restricted prefix \"{prefix}\": \"{prefix}folder_name\"" in str(excinfo.value)

def test_egnyte_name_starts_with_tilde():
    with pytest.raises(ValueError) as excinfo:
        Egnyte(".~temp/file.txt").check_if_valid()
    assert 'Name starts with restricted prefix ".~"' in str(excinfo.value)