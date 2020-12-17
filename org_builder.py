# org_builder.py
__version__ = '0.0.2'

import argparse
import logging
import os
import sys

import config
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
DURATION = config.DURATION
DEVHUB = config.DEVHUB
PACKAGE_IDS = config.PACKAGE_IDS
PACKAGE_P_SETS = config.PACKAGE_P_SETS
PRE_DEPLOY = config.PRE_DEPLOY
SRC_FOLDERS = config.SRC_FOLDERS
BUILD_DATA_CMD = config.BUILD_DATA_CMD
P_SETS = config.P_SETS
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
        help="Scratch Org user alias"
    )
    parser.add_argument(
        '-d', '--duration',
        help=f"Number of days org will last [1..30]. Default: {DURATION}",
        default=DURATION
    )
    parser.add_argument(
        '-v', '--devhub',
        help=f"Target dev hub username or alias. Default: {DEVHUB}",
        default=DEVHUB
    )
    parser.add_argument(
        '--debug',
        help="Turn on debug messages",
        action='store_true'
    )


def check_install(org_alias, status_id):

    py_obj = sfdx.check_install(org_alias, status_id)

    if py_obj['status'] == 1:
        message = py_obj['message']
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj['status'] == 0:
        status = py_obj['result']['Status']

    logging.error(f"Checking package install status ~ {status}")

    return status


def check_org(org_alias):

    py_obj = sfdx.org_list()

    scratch_orgs = py_obj['result']['scratchOrgs']
    for org in scratch_orgs:
        try:
            if org_alias == org['alias'] and not org['isExpired']:
                logging.debug(
                    f"Alias : {org['alias']}, Username : {org['username']}, End Date : {org['expirationDate']}")
                return org['username'], True

        except KeyError:
            pass

    return '', False


def create_sratch_org(org_alias, duration, devhub):

    py_obj = sfdx.create_sratch_org(org_alias, duration, devhub)

    if py_obj['status'] == 1:
        message = py_obj['message']
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj['status'] == 0:
        username = py_obj['result']['username']

    return username


def execute_script(org_alias, apex_file):

    py_obj = sfdx.execute_script(org_alias, apex_file)

    if py_obj['status'] == 1:
        message = py_obj['message']
        logging.error(f"MESSAGE: {message}")
        logging.error(
            f"CompileProblem: {py_obj['result']['compileProblem']}\nExceptionMessage: {py_obj['result']['exceptionMessage']}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj['status'] == 0:
        logging.warning(f"{py_obj}")

    return True


def install_package(org_alias, package_id):

    py_obj = sfdx.install_package(org_alias, package_id)

    if py_obj['status'] == 1:
        message = py_obj['message']
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj['status'] == 0:
        install_status = py_obj['result']['Status']
        while install_status == "IN_PROGRESS":
            install_status = check_install(org_alias, py_obj['result']['Id'])

    return True


def install_permission_set(org_alias, pset):

    py_obj = sfdx.install_permission_set(org_alias, pset)

    if py_obj['status'] == 1:
        message = py_obj['result']['failures'][0]['message']
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")

    if py_obj['status'] == 0:
        logging.info(f"{py_obj}")

    return True


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


def user_details(org_alias):

    py_obj = sfdx.user_details(org_alias)

    if py_obj['status'] == 1:
        message = py_obj['message']
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj['status'] == 0:
        logging.error(f"OrgId \t: {py_obj['result']['orgId']}")
        logging.error(f"Username \t: {py_obj['result']['username']}")
        logging.error(f"Url \t: {py_obj['result']['instanceUrl']}")
        logging.error(f"Alias \t: {py_obj['result']['alias']}")


def main():
    logging.debug("main()")

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

    if PACKAGE_IDS:
        for pckg in PACKAGE_IDS:
            logging.error(f"~~~ Installing Packages {pckg} ~~~")
            install_package(args.alias, pckg)

    if PRE_DEPLOY:
        for fldr in PRE_DEPLOY:
            logging.error(f"~~~ Installing Source ({fldr}) ~~~")
            install_source(args.alias, f"{dir_path}/{fldr}")

    if PACKAGE_P_SETS:
        for pset in PACKAGE_P_SETS:
            logging.error(f"~~~ Installing Permission Set ({pset}) ~~~")
            install_permission_set(args.alias, pset)

    if SRC_FOLDERS:
        for fldr in SRC_FOLDERS:
            logging.error(f"~~~ Installing Source ({fldr}) ~~~")
            install_source(args.alias, f"{dir_path}/{fldr}")

    if P_SETS:
        for pset in P_SETS:
            logging.error(f"~~~ Installing Permission Set ({pset}) ~~~")
            install_permission_set(args.alias, pset)

    if BUILD_DATA_CMD:
        logging.error("~~~ Running Build data ~~~")
        execute_script(args.alias, BUILD_DATA_CMD)

    logging.error("~~~ Details ~~~")
    user_details(args.alias)

    logging.error("~~~ Scratch Org Complete ~~~")


if __name__ == '__main__':
    main()
