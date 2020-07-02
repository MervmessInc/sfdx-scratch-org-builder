# org_builder.py
__version__ = '0.0.1'

import argparse
import json
import logging
import os
import subprocess
import sys
import time

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
SFDX_CMD = "sfdx.cmd"
SLEEP_SEC = 120
# List of managed package Ids to install into the Org.
PACKAGE_IDS = []
# List of metadata source folders (SRC_FOLDERS = ["force-app"])
SRC_FOLDERS = []
# Anonymous APEX file to execute ("setupdata.apex")
BUILD_DATA_CMD = ""
# List of permission sets to assign to the user.
P_SETS= []
#
#

parser = argparse.ArgumentParser(
    prog='org_builder',
    description='''
    Python wrapper for a number of Salesforce CLI (sfdx) commands, to build and setup Scratch Orgs.
    ''')


def setup_args():
    logging.debug("setup_args()")

    parser.add_argument(
        '-a', '--alias',
        help='Scratch Org user alias'
    )
    parser.add_argument(
        '-d', '--duration',
        help='Number of days org will last [1..30]. Default: 10',
        default=10
    )
    parser.add_argument(
        '-v', '--devhub',
        help='Target dev hub username or alias. Default: my-dev-hub-org',
        default='my-dev-hub-org'
    )
    parser.add_argument(
        '--debug',
        help='Turn on debug messages',
        action='store_true'
    )


def check_org(org_alias):

    pyObj = sfdx.check_org(org_alias)

    scratch_orgs = pyObj['result']['scratchOrgs']
    for org in scratch_orgs:
        try:
            if org_alias == org['alias'] and not org['isExpired']:
                logging.debug(f"Alias : {org['alias']}, Username : {org['username']}, End Date : {org['expirationDate']}")
                return org['username'], True

        except KeyError:
            pass

    return '', False


def create_sratch_org(org_alias, duration, devhub):

    pyObj = sfdx.create_sratch_org(org_alias, duration, devhub)

    if pyObj['status'] == 1:
        message = pyObj['message']
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{pyObj}")
        sys.exit(1)

    if pyObj['status'] == 0:
        username = pyObj['result']['username']

    return username


def check_install(org_alias, status_id):

    pyObj = sfdx.check_install(org_alias, status_id)

    if pyObj['status'] == 1:
        message = pyObj['message']
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{pyObj}")
        sys.exit(1)

    if pyObj['status'] == 0:
        status = pyObj['result']['Status']

    logging.error(f"Checking package install status ~ {status}")

    return status


def install_package(org_alias, package_id):

    pyObj = sfdx.install_package(org_alias, package_id)

    if pyObj['status'] == 1:
        message = pyObj['message']
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{pyObj}")
        sys.exit(1)

    if pyObj['status'] == 0:
        install_status = pyObj['result']['Status']
        while install_status == "IN_PROGRESS":
            install_status = check_install(org_alias, pyObj['result']['Id'])

    return True


def install_source(org_alias, src_folder):

    pyObj = sfdx.install_source(org_alias, src_folder)

    if pyObj['status'] == 1:
        message = pyObj['message']
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{pyObj}")
        sys.exit(1)

    if pyObj['status'] == 0:
        for item in pyObj['result']['deployedSource']:
            logging.info(f"Type: {item['type']}, State: {item['state']}, Name: {item['fullName']}")

    return True


def execute_script(org_alias, apex_file):

    pyObj = sfdx.execute_script(org_alias, apex_file)

    if pyObj['status'] == 1:
        message = pyObj['message']
        logging.error(f"MESSAGE: {message}")
        logging.error(f"Compiled: {pyObj['result']['compiled']}\nCompileProblem: {pyObj['result']['compileProblem']}\nExceptionMessage: {pyObj['result']['exceptionMessage']}")
        logging.warning(f"{pyObj}")
        sys.exit(1)

    if pyObj['status'] == 0:
        logging.info(f"{pyObj['result']['compiled']}\nCompileProblem: {pyObj['result']['compileProblem']}\nExceptionMessage: {pyObj['result']['exceptionMessage']}")

    return True


def install_permission_Set(org_alias, pset):

    pyObj = sfdx.install_permission_Set(org_alias, pset)

    if pyObj['status'] == 1:
        message = pyObj['result']['failures'][0]['message']
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{pyObj}")

    if pyObj['status'] == 0:
        logging.info(f"{pyObj}")

    return True


def main():
    logging.debug(f"main()")

    setup_args()
    args = parser.parse_args()

    if args.alias is None:
        parser.print_help()
        sys.exit(0)

    if args.debug:
        logging.error("~~~ Setting up DEBUG ~~~")
        logger.setLevel(logging.INFO)

    logging.error("~~~ Setting up Scratch Org ~~~")
    logging.error(f"{args}")

    logging.error("~~~ Check if Org Already Exists ~~~")
    username, org_exists = check_org(args.alias)

    if not org_exists:
        logging.error("~~~ Create New Scratch Org ~~~")
        username = create_sratch_org(args.alias, args.duration, args.devhub)

    logging.error(f"USER: {username}\n")

    if PACKAGE_IDS:
        for pckg in PACKAGE_IDS:
            logging.error(f"~~~ Installing Packages {pckg} ~~~")
            install_package(args.alias, pckg)

    if SRC_FOLDERS:
        for fldr in SRC_FOLDERS:
            logging.error(f"~~~ Installing Source ({fldr}) ~~~")
            install_source(args.alias, f"{dir_path}/{fldr}")

    if P_SETS:
        for pset in P_SETS:
            logging.error(f"~~~ Installing Permission Set ({pset}) ~~~")
            install_permission_Set(args.alias, pset)

    if BUILD_DATA_CMD:
        logging.error(f"~~~ Running Build data ~~~")
        execute_script(args.alias, BUILD_DATA_CMD)

    logging.error("~~~ Scratch Org Complete ~~~")

if __name__ == '__main__':
    main()
