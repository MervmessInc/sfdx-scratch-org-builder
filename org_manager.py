# org_manager.py
__version__ = '0.0.1'

import json
import logging
import os
import sys
import threading
import traceback

import sfdx_cli_utils as sfdx

# Set the working directory to the location of the file.
#
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

# Set the Log level
#
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger()

# Config
#
TGREEN = "\033[1;32m"
TRED = "\033[1;31m"
ENDC = "\033[m"
#
#



def clean_org_data(org):
    if "alias" not in org:
        a = {"alias" : ""}
        org.update(a)

    if "isDevHub" not in org:
        dh = {"isDevHub" : False}
        org.update(dh)

    if "defaultMarker" not in org:
        dm = {"defaultMarker" : ""}
        org.update(dm)

    if "status" not in org:
        s = {"status" : "Active"}
        org.update(s)

    if "expirationDate" not in org:
        dt = {"expirationDate" : ""}
        org.update(dt)

    return org

def get_org_list():
    if os.path.isfile("org_list.json"):
        org_list = json.load(open("org_list.json", "r"))
        t = threading.Thread(target=update_org_list)
        t.start()

    else:
        org_list = update_org_list()

    return org_list


def get_orgs_map(org_list):

    non_scratch_orgs = org_list['result']['nonScratchOrgs']
    scratch_orgs = org_list['result']['scratchOrgs']

    orgs = {}
    defaultusername = 1
    index = 1

    for o in non_scratch_orgs:
        org = {index : clean_org_data(o)}
        orgs.update(org)
        index = index + 1

    for o in scratch_orgs:
        clean_org = clean_org_data(o)

        if clean_org['defaultMarker'] == "(U)":
            defaultusername = index

        org = {index : clean_org}
        orgs.update(org)
        index = index + 1

    return orgs, defaultusername


def install_source(org_alias, src_folder):

    py_obj = sfdx.install_source(org_alias, src_folder)

    if py_obj['status'] == 1:
        message = py_obj['message']
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj['status'] == 0:
        for item in py_obj['result']['deployedSource']:
            logging.info(
                f"Type: {item['type']}, State: {item['state']}, Name: {item['fullName']}")

    return True


def parse_sfdx_project():
    defaultpath = ''

    if os.path.isfile("sfdx-project.json"):
        sfdx_project = json.load(open("sfdx-project.json", "r"))
        for o in sfdx_project['packageDirectories']:
            if o['default']:
                defaultpath = o['path']

    return defaultpath


def print_org_details(idx, o):
    color = TGREEN
    if o['status'] != "Active":
        color = TRED

    print("{:>3} {:<3} {:<20} {:<45} {:<12} {:<10}"
    .format(
        idx,
        o['defaultMarker'],
        o['alias'],
        o['username'],
        o['expirationDate'],
        color + o['status'] + ENDC))


def print_org_list(orgs):
    print("{:>3} {:<3} {:<20} {:<45} {:<12} {:<10}"
    .format("idx", "", "Alias", "Username", "Expiration", "Status"))
    print("{:>3} {:<3} {:<20} {:<45} {:<12} {:<10}"
    .format("---", "", "-----", "--------", "----------", "------"))


    for idx, o in orgs.items():
        print_org_details(idx, o)


def show_org_list(orgs):
    print()
    print_org_list(orgs)
    print()
    choice = input("Enter choice 'idx' or 'U' > ") or 'Q'

    return choice


def update_org_list():
    org_list = sfdx.org_list()
    json.dump(org_list, open("org_list.json", "w"))

    return org_list


def main():
    logging.debug("main()")
    try:
        org_list = get_org_list()
        orgs, defaultusername = get_orgs_map(org_list)
    
        choice = show_org_list(orgs)

        if choice.isnumeric():
            idx = int(choice)
        elif choice.upper() == 'U':
            idx = defaultusername
        elif choice.isalpha():
            sys.exit(0)

        org = orgs.get(idx)
        defaultpath = parse_sfdx_project()
        username = org['username']
        if len(org['alias']) > 0:
            username = org['alias']

        print()
        action = input(f"[D]eploy '{defaultpath}' or [O]pen '{username}' >  ") or 'O'

        if action.upper() == 'D' or action.upper() == 'DEPLOY':
            logging.error(f"~~~ Installing Source ({defaultpath}) ~~~")
            install_source(username, f"{defaultpath}")
        elif action.upper() == 'O' or action.upper() == 'OPEN':
            logging.error(f"~~~ Opening Org ({username}) ~~~")
            sfdx.org_open(org['username'])
        

    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    main()
