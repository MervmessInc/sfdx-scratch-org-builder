# tests/test_sfdx_cli_utils.py
"""
Unit tests for sfdx_cli_utils.parse_output().
subprocess.run is mocked so no real sf CLI calls are made.
"""

import json
import subprocess
from unittest.mock import MagicMock

import pytest

from sf_org_manager import sfdx_cli_utils as sfdx


def _make_result(stdout="", stderr="", args=None):
    """Helper: build a fake CompletedProcess."""
    result = MagicMock(spec=subprocess.CompletedProcess)
    result.stdout = stdout
    result.stderr = stderr
    result.args = args or ["sf.cmd", "org", "list"]
    return result


# ---------------------------------------------------------------------------
# parse_output — happy paths
# ---------------------------------------------------------------------------


class TestParseOutputSuccess:
    def test_returns_parsed_json(self):
        payload = {"status": 0, "result": {"foo": "bar"}}
        fake = _make_result(stdout=json.dumps(payload))
        assert sfdx.parse_output(fake) == payload

    def test_status_0_is_preserved(self):
        payload = {"status": 0, "result": {}}
        fake = _make_result(stdout=json.dumps(payload))
        result = sfdx.parse_output(fake)
        assert result["status"] == 0

    def test_status_1_is_preserved(self):
        payload = {"status": 1, "message": "Something went wrong"}
        fake = _make_result(stdout=json.dumps(payload))
        result = sfdx.parse_output(fake)
        assert result["status"] == 1
        assert result["message"] == "Something went wrong"

    def test_nested_result_is_accessible(self):
        payload = {"status": 0, "result": {"username": "test@example.com"}}
        fake = _make_result(stdout=json.dumps(payload))
        result = sfdx.parse_output(fake)
        assert result["result"]["username"] == "test@example.com"


# ---------------------------------------------------------------------------
# parse_output — error paths
# ---------------------------------------------------------------------------


class TestParseOutputErrors:
    def test_empty_stdout_and_stderr_exits(self):
        fake = _make_result(stdout="", stderr="")
        with pytest.raises(SystemExit):
            sfdx.parse_output(fake)

    def test_stderr_only_exits(self):
        fake = _make_result(stdout="", stderr="Error: command failed")
        with pytest.raises(SystemExit):
            sfdx.parse_output(fake)

    def test_invalid_json_exits(self):
        fake = _make_result(stdout="this is not json")
        with pytest.raises(SystemExit):
            sfdx.parse_output(fake)

    def test_partial_json_exits(self):
        fake = _make_result(stdout='{"status": 0, "result":')
        with pytest.raises(SystemExit):
            sfdx.parse_output(fake)
