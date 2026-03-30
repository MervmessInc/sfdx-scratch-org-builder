# org_manager.py

import argparse
import json
import logging
import sys
import threading
import traceback
from pathlib import Path

import platformdirs

from . import sfdx_cli_utils as sfdx

# Config
TGREEN = "\033[1;32m"
TRED = "\033[1;31m"
ENDC = "\033[m"

_CACHE_DIR = Path(platformdirs.user_cache_dir("sf-org-manager"))
_ORG_LIST_CACHE = _CACHE_DIR / "org_list.json"


def _ensure_cache_dir():
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_org_list():
    if _ORG_LIST_CACHE.is_file():
        with open(_ORG_LIST_CACHE, "r") as jsonfile:
            org_list = json.load(jsonfile)

        t = threading.Thread(target=update_org_list, daemon=True)
        t.start()
    else:
        org_list = update_org_list()

    return org_list


def get_orgs_map(orgs):
    result = orgs.get("result", {})

    non_scratch_orgs = result.get("nonScratchOrgs") or result.get("salesforceOrgs") or []
    scratch_orgs = result.get("scratchOrgs") or []

    orgs_map = {}
    defaultusername = 1
    index = 1

    for o in non_scratch_orgs:
        clean_org = clean_org_data(o)
        if clean_org["defaultMarker"] == "(U)":
            defaultusername = index
        orgs_map[index] = clean_org
        index += 1

    for o in scratch_orgs:
        clean_org = clean_org_data(o)
        if clean_org["defaultMarker"] == "(U)":
            defaultusername = index
        orgs_map[index] = clean_org
        index += 1

    return orgs_map, defaultusername


def clean_org_data(org):
    org.setdefault("alias", "")
    org.setdefault("isDevHub", False)
    org.setdefault("defaultMarker", "")
    org.setdefault("status", "Active")
    org.setdefault("expirationDate", "")
    return org


def print_org_details(idx, o):
    color = TGREEN if o["status"] == "Active" else TRED
    print(
        f"{idx:>3} {o['defaultMarker']:<3} {o['alias']:<30} {o['username']:<45} {o['expirationDate']:<12} {color}{o['status']:<10}{ENDC}"
    )


def print_org_list(orgs):
    print(f"{'idx':>3} {'':3} {'Alias':<30} {'Username':<45} {'Expiration':<12} {'Status':<10}")
    print(f"{'---':>3} {'':3} {'-----':<30} {'--------':<45} {'----------':<12} {'------':<10}")
    for idx, o in orgs.items():
        print_org_details(idx, o)


def show_org_list(orgs):
    print()
    print_org_list(orgs)
    print()
    choice = input("Enter choice 'idx' or 'U' > ") or "Q"
    return choice


def user_details(org_alias):
    py_obj = sfdx.user_details(org_alias)

    if py_obj["status"] == 1:
        logging.error(f"MESSAGE: {py_obj.get('message', 'Unknown error')}")
        sys.exit(1)

    if py_obj["status"] == 0:
        print(f"OrgId \t\t: {py_obj['result']['orgId']}")
        print(f"Username \t: {py_obj['result']['username']}")
        print(
            f"Url \t\t: {py_obj['result']['instanceUrl']}"
            f"/secur/frontdoor.jsp?sid={py_obj['result']['accessToken']}"
        )
        print(f"Alias \t\t: {py_obj['result']['alias']}")
        print(f"Token \t\t: {py_obj['result']['accessToken']}")


def update_org_list():
    _ensure_cache_dir()
    org_list = sfdx.org_list()
    with open(_ORG_LIST_CACHE, "w") as jsonfile:
        json.dump(org_list, jsonfile)
    return org_list


def main():
    parser = argparse.ArgumentParser(
        prog="org_manager",
        description="Python wrapper for Salesforce CLI (sf) that lists Salesforce orgs.",
    )
    parser.add_argument("--debug", help="Turn on debug messages", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.ERROR,
        format="%(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )

    logging.info(f"argv[0] ~ {sys.argv[0]}")

    try:
        org_list = get_org_list()
        orgs, defaultusername = get_orgs_map(org_list)

        choice = show_org_list(orgs)

        if choice.isnumeric():
            idx = int(choice)
        elif choice.upper() == "U":
            idx = defaultusername
        else:
            sys.exit(0)

        org = orgs.get(idx)
        if org is None:
            print(f"No org found at index {idx}.")
            sys.exit(1)

        username = org["alias"] if org["alias"] else org["username"]

        print()
        user_details(username)
        print()

        action = input(f"[O]pen '{username}' >  ") or "O"

        if action.upper() in ("O", "OPEN"):
            logging.info(f"Opening org ({username})")
            sfdx.org_open(org["username"])
        elif action.upper() in ("Q", "QUIT"):
            sys.exit(0)

    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()
