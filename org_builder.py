# org_builder.py
__version__ = '0.0.1'

import argparse
import json
import logging
import os
import subprocess
import sys
import time

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


def parse_output(cmd_output):

    logging.warning(f"ARGS: {cmd_output.args}")
    logging.debug(f"STDOUT:\n{cmd_output.stdout}")
    logging.debug(f"STDERR:\n{cmd_output.stderr}")

    pyObj={}

    if cmd_output.stderr != b'':
        logging.error(f"STDERR: {cmd_output.stderr}")
        sys.exit(1)

    if cmd_output.stdout != b'':
        pyObj = json.loads(cmd_output.stdout)

    logging.debug(json.dumps(pyObj,sort_keys=True, indent=3))

    return pyObj


def check_org(org_alias):
    logging.debug(f"check_org({org_alias})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:org:list",
            "--all",
            "--json"
        ],
        capture_output=True
    )

    pyObj = parse_output(out)

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
    logging.debug(f"create_sratch_org({org_alias}, {duration}, {devhub})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:org:create",
            "-f",
            "config/project-scratch-def.json",
            "-s",
            "-d",
            f"{duration}",
            "-a",
            f"{org_alias}",
            "-v",
            f"{devhub}",
            "--json"
        ],
        capture_output=True
    )

    pyObj = parse_output(out)

    if pyObj['status'] == 1:
        message = pyObj['message']
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{pyObj}")
        sys.exit(1)

    if pyObj['status'] == 0:
        username = pyObj['result']['username']

    return username


def check_install(org_alias, status_id):
    logging.debug(f"check_install({org_alias}, {status_id})")

    time.sleep(SLEEP_SEC)

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:package:install:report",
            "-u",
            f"{org_alias}",
            "-i",
            f"{status_id}",
            "--json"
        ],
        capture_output=True
    )

    pyObj = parse_output(out)

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
    logging.debug(f"install_package({org_alias})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:package:install",
            "--package",
            f"{package_id}",
            "-u",
            f"{org_alias}",
            "--noprompt",
            "--json"
        ],
        capture_output=True
    )

    pyObj = parse_output(out)

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
    logging.debug(f"install_source({org_alias}, {src_folder})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:source:deploy",
            "-p",
            src_folder,
            "-u",
            f"{org_alias}",
            "-g",
            "--loglevel",
            "fatal",
            "--json"
        ],
        capture_output=True
    )

    pyObj = parse_output(out)

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
    logging.debug(f"execute_script({org_alias}, {apex_file})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:apex:execute",
            "-f",
            f"{apex_file}",
            "-u",
            f"{org_alias}",
            "--json"
        ],
        capture_output=True
    )

    pyObj = parse_output(out)

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
    logging.debug(f"install_permission_Set({org_alias}, {pset})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:user:permset:assign",
            "-n",
            f"{pset}",
            "-u",
            f"{org_alias}",
            "--json"
        ],
        capture_output=True
    )

    pyObj = parse_output(out)

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
