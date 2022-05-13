# org_manager.py
__version__ = "0.0.1"

import json
import logging
import os
import sys
import threading
import traceback

from . import sfdx_cli_utils as sfdx

# Config
#
TGREEN = "\033[1;32m"
TRED = "\033[1;31m"
ENDC = "\033[m"
#
#


def clean_org_data(org):
    if "alias" not in org:
        a = {"alias": ""}
        org.update(a)

    if "isDevHub" not in org:
        dh = {"isDevHub": False}
        org.update(dh)

    if "defaultMarker" not in org:
        dm = {"defaultMarker": ""}
        org.update(dm)

    if "status" not in org:
        s = {"status": "Active"}
        org.update(s)

    if "expirationDate" not in org:
        dt = {"expirationDate": ""}
        org.update(dt)

    return org


def get_org_list():
    if os.path.isfile("./org_list.json"):
        with open("./org_list.json", "r") as jsonfile:
            org_list = json.load(jsonfile)

        t = threading.Thread(target=update_org_list)
        t.start()

    else:
        org_list = update_org_list()

    return org_list


def get_orgs_map(orgs):

    try:
        non_scratch_orgs = orgs["result"]["nonScratchOrgs"]
    except KeyError:
        pass

    try:
        non_scratch_orgs = orgs["result"]["salesforceOrgs"]
    except KeyError:
        pass

    try:
        scratch_orgs = orgs["result"]["scratchOrgs"]
    except KeyError:
        pass

    orgs = {}
    defaultusername = 1
    index = 1

    for o in non_scratch_orgs:
        org = {index: clean_org_data(o)}
        orgs.update(org)
        index = index + 1

    for o in scratch_orgs:
        clean_org = clean_org_data(o)

        if clean_org["defaultMarker"] == "(U)":
            defaultusername = index

        org = {index: clean_org}
        orgs.update(org)
        index = index + 1

    return orgs, defaultusername


def print_org_details(idx, o):
    color = TGREEN
    if o["status"] != "Active":
        color = TRED

    print(
        "{:>3} {:<3} {:<30} {:<45} {:<12} {:<10}".format(
            idx,
            o["defaultMarker"],
            o["alias"],
            o["username"],
            o["expirationDate"],
            color + o["status"] + ENDC,
        )
    )


def print_org_list(orgs):
    print(
        "{:>3} {:<3} {:<30} {:<45} {:<12} {:<10}".format(
            "idx", "", "Alias", "Username", "Expiration", "Status"
        )
    )
    print(
        "{:>3} {:<3} {:<30} {:<45} {:<12} {:<10}".format(
            "---", "", "-----", "--------", "----------", "------"
        )
    )

    for idx, o in orgs.items():
        print_org_details(idx, o)


def show_org_list(orgs):
    print()
    print_org_list(orgs)
    print()
    choice = input("Enter choice 'idx' or 'U' > ") or "Q"

    return choice


def update_org_list():
    org_list = sfdx.org_list()
    with open("./org_list.json", "w") as jsonfile:
        json.dump(org_list, jsonfile)

    return org_list


def main():
    try:
        org_list = get_org_list()
        orgs, defaultusername = get_orgs_map(org_list)

        choice = show_org_list(orgs)

        if choice.isnumeric():
            idx = int(choice)
        elif choice.upper() == "U":
            idx = defaultusername
        elif choice.isalpha():
            sys.exit(0)

        org = orgs.get(idx)
        username = org["username"]
        if len(org["alias"]) > 0:
            username = org["alias"]

        print()
        action = input(f"[O]pen '{username}' >  ") or "O"

        if action.upper() == "O" or action.upper() == "OPEN":
            logging.error(f"~~~ Opening Org ({username}) ~~~")
            sfdx.org_open(org["username"])
        elif action.upper() == "Q" or action.upper() == "QUIT":
            sys.exit(0)

    except Exception:
        traceback.print_exc()
