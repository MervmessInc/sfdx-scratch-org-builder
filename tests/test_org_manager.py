# tests/test_org_manager.py
"""
Unit tests for org_manager helper functions.
No sf CLI calls are made — all data is constructed inline.
"""

from sf_org_manager.org_manager import clean_org_data, get_orgs_map

# ---------------------------------------------------------------------------
# Sample org data fixtures
# ---------------------------------------------------------------------------


def _make_org(**kwargs):
    """Minimal valid org dict, overridable via kwargs."""
    base = {
        "username": "test@example.com",
        "alias": "my-org",
        "defaultMarker": "",
        "status": "Active",
        "expirationDate": "",
        "isDevHub": False,
    }
    base.update(kwargs)
    return base


def _make_org_list(non_scratch=None, scratch=None):
    """Build an sf CLI org list response dict."""
    return {
        "status": 0,
        "result": {
            "nonScratchOrgs": non_scratch or [],
            "scratchOrgs": scratch or [],
        },
    }


# ---------------------------------------------------------------------------
# clean_org_data
# ---------------------------------------------------------------------------


class TestCleanOrgData:
    def test_complete_org_unchanged(self):
        org = _make_org()
        result = clean_org_data(org.copy())
        assert result["alias"] == "my-org"
        assert result["status"] == "Active"

    def test_missing_alias_defaults_to_empty(self):
        org = _make_org()
        del org["alias"]
        result = clean_org_data(org)
        assert result["alias"] == ""

    def test_missing_status_defaults_to_active(self):
        org = _make_org()
        del org["status"]
        result = clean_org_data(org)
        assert result["status"] == "Active"

    def test_missing_default_marker_defaults_to_empty(self):
        org = _make_org()
        del org["defaultMarker"]
        result = clean_org_data(org)
        assert result["defaultMarker"] == ""

    def test_missing_expiration_date_defaults_to_empty(self):
        org = _make_org()
        del org["expirationDate"]
        result = clean_org_data(org)
        assert result["expirationDate"] == ""

    def test_missing_is_dev_hub_defaults_to_false(self):
        org = _make_org()
        del org["isDevHub"]
        result = clean_org_data(org)
        assert result["isDevHub"] is False

    def test_existing_values_not_overwritten(self):
        org = _make_org(alias="kept-alias", status="Inactive")
        result = clean_org_data(org)
        assert result["alias"] == "kept-alias"
        assert result["status"] == "Inactive"


# ---------------------------------------------------------------------------
# get_orgs_map
# ---------------------------------------------------------------------------


class TestGetOrgsMap:
    def test_single_non_scratch_org(self):
        org_list = _make_org_list(non_scratch=[_make_org(username="a@example.com")])
        orgs, _ns, _sc, default = get_orgs_map(org_list)
        assert len(orgs) == 1
        assert orgs[1]["username"] == "a@example.com"

    def test_indexes_are_1_based(self):
        org_list = _make_org_list(
            non_scratch=[_make_org(username="a@example.com"), _make_org(username="b@example.com")]
        )
        orgs, _ns, _sc, _ = get_orgs_map(org_list)
        assert 1 in orgs
        assert 2 in orgs
        assert 0 not in orgs

    def test_scratch_orgs_appended_after_non_scratch(self):
        org_list = _make_org_list(
            non_scratch=[_make_org(username="ns@example.com")],
            scratch=[_make_org(username="sc@example.com", expirationDate="2026-12-01")],
        )
        orgs, _ns, _sc, _ = get_orgs_map(org_list)
        assert len(orgs) == 2
        assert orgs[1]["username"] == "ns@example.com"
        assert orgs[2]["username"] == "sc@example.com"

    def test_default_username_marker_detected(self):
        org_list = _make_org_list(
            non_scratch=[
                _make_org(username="a@example.com", defaultMarker=""),
                _make_org(username="b@example.com", defaultMarker="(U)"),
            ]
        )
        _, _ns, _sc, default = get_orgs_map(org_list)
        assert default == 2

    def test_default_username_in_scratch_orgs(self):
        org_list = _make_org_list(
            non_scratch=[_make_org(username="hub@example.com", defaultMarker="(D)")],
            scratch=[_make_org(username="sc@example.com", defaultMarker="(U)")],
        )
        _, _ns, _sc, default = get_orgs_map(org_list)
        assert default == 2

    def test_empty_org_list_returns_empty_map(self):
        org_list = _make_org_list()
        orgs, _ns, _sc, default = get_orgs_map(org_list)
        assert orgs == {}
        assert default == 1  # falls back to 1 when no (U) found

    def test_salesforce_orgs_key_used_as_fallback(self):
        """sf CLI v2 may use 'salesforceOrgs' instead of 'nonScratchOrgs'."""
        org_list = {
            "status": 0,
            "result": {
                "salesforceOrgs": [_make_org(username="sf@example.com")],
                "scratchOrgs": [],
            },
        }
        orgs, _ns, _sc, _ = get_orgs_map(org_list)
        assert len(orgs) == 1
        assert orgs[1]["username"] == "sf@example.com"

    def test_missing_result_key_returns_empty(self):
        org_list = {"status": 0, "result": {}}
        orgs, _ns, _sc, default = get_orgs_map(org_list)
        assert orgs == {}
        assert default == 1
