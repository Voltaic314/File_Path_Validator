import pytest
from FPV.Helpers.egnyte import FPV_Egnyte


def test_process_restricted_suffixes_validate():
    egnyte = FPV_Egnyte("C:/folder/file.tmp", sep="/", auto_validate=False)
    part = {"part": "example.tmp", "index": 1}
    egnyte.process_restricted_suffixes(part, action="validate")
    current_issues_for_part = egnyte._path_helper.get_issues_for_part(part["index"])
    issue_categories = [issue["category"] for issue in current_issues_for_part]
    assert "SUFFIX" in issue_categories


def test_process_restricted_suffixes_clean():
    egnyte = FPV_Egnyte("C:/folder/file.tmp", sep="/", auto_validate=False)
    part = {"part": "example.tmp", "index": 1}
    egnyte.process_restricted_suffixes(part, action="clean")
    pending_actions = egnyte._path_helper.get_pending_actions_for_part(part["index"])
    action_categories = [action["category"] for action in pending_actions]
    assert "SUFFIX" in action_categories


def test_process_restricted_prefixes_validate():
    egnyte = FPV_Egnyte("C:/folder/._example", sep="/", auto_validate=False)
    part = {"part": "._example", "index": 1}
    egnyte.process_restricted_prefixes(part, action="validate")
    current_issues_for_part = egnyte._path_helper.get_issues_for_part(part["index"])
    issue_categories = [issue["category"] for issue in current_issues_for_part]
    assert "PREFIX" in issue_categories


def test_process_restricted_prefixes_clean():
    egnyte = FPV_Egnyte("C:/folder/._example", sep="/", auto_validate=False)
    part = {"part": "._example", "index": 1}
    egnyte.process_restricted_prefixes(part, action="clean")
    pending_actions = egnyte._path_helper.get_pending_actions_for_part(part["index"])
    action_categories = [action["category"] for action in pending_actions]
    assert "PREFIX" in action_categories


def test_process_temp_patterns_validate():
    egnyte = FPV_Egnyte("C:/folder/atmp3829", sep="/", auto_validate=False)
    part = {"part": "atmp3829", "index": 2}
    egnyte.process_temp_patterns(part, action="validate")
    current_issues_for_part = egnyte._path_helper.get_issues_for_part(part["index"])
    issue_categories = [issue["category"] for issue in current_issues_for_part]
    assert "TEMP_PATTERN" in issue_categories


def test_process_temp_patterns_clean():
    egnyte = FPV_Egnyte("C:/folder/atmp3829", sep="/", auto_validate=False)
    part = {"part": "atmp3829", "index": 2}
    egnyte.process_temp_patterns(part, action="clean")
    pending_actions = egnyte._path_helper.get_pending_actions_for_part(part["index"])
    action_categories = [action["category"] for action in pending_actions]
    assert "TEMP_PATTERN" in action_categories


def test_process_part_length_validate():
    egnyte = FPV_Egnyte("C:/folder/" + "a" * 300, sep="/", auto_validate=False)
    long_part = "a" * 300
    part = {"part": long_part, "index": 2}
    egnyte.process_part_length(part, action="validate")
    current_issues_for_part = egnyte._path_helper.get_issues_for_part(part["index"])
    issue_categories = [issue["category"] for issue in current_issues_for_part]
    assert "PART_LENGTH" in issue_categories


def test_process_part_length_clean():
    egnyte = FPV_Egnyte("C:/folder/" + "a" * 300, sep="/", auto_validate=False)
    long_part = "a" * 300
    part = {"part": long_part, "index": 3}
    egnyte.process_part_length(part, action="clean")
    pending_actions = egnyte._path_helper.get_pending_actions_for_part(part["index"])
    action_categories = [action["category"] for action in pending_actions]
    assert "PART_LENGTH" in action_categories
