# org_builder.py
__version__ = "0.0.2"

import argparse
import logging
import os
import sys
import yaml

from . import sfdx_cli_utils as sfdx

# Set the Log level
#
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"
)
logger = logging.getLogger()

parser = argparse.ArgumentParser(
    prog="org_builder",
    description="""
Python wrapper for a number of Salesforce CLI (sfdx) commands,
 to build and setup Scratch Orgs.
    """,
)


def get_config():
    if os.path.isfile("./org_config.yml"):
        with open("org_config.yml", "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
    else:
        logging.error("Missing org_config.yml")
        sys.exit(1)

    return cfg


def setup_args(cfg):
    parser.add_argument("-a", "--alias", help="Scratch Org user alias")
    parser.add_argument(
        "-d",
        "--duration",
        help=f"Number of days org will last [1..30]. Default: {cfg['DURATION']}",
        default=cfg["DURATION"],
    )
    parser.add_argument(
        "-v",
        "--devhub",
        help=f"Target dev hub username or alias. Default: {cfg['DEVHUB']}",
        default=cfg["DEVHUB"],
    )
    parser.add_argument("--debug", help="Turn on debug messages", action="store_true")


def check_install(org_alias, status_id):

    py_obj = sfdx.check_install(org_alias, status_id)

    if py_obj["status"] == 1:
        message = py_obj["message"]
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj["status"] == 0:
        status = py_obj["result"]["Status"]

    logging.error(f"Checking package install status ~ {status}")

    return status


def check_org(org_alias):

    py_obj = sfdx.org_list()

    scratch_orgs = py_obj["result"]["scratchOrgs"]
    for org in scratch_orgs:
        try:
            if org_alias == org["alias"] and not org["isExpired"]:
                logging.debug(
                    f"Alias : {org['alias']}, Username : {org['username']}, End Date : {org['expirationDate']}"
                )
                return org["username"], True

        except KeyError:
            pass

    return "", False


def create_sratch_org(org_alias, duration, devhub, scratch_def):

    py_obj = sfdx.create_sratch_org(org_alias, duration, devhub, scratch_def)

    if py_obj["status"] == 1:
        message = py_obj["message"]
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj["status"] == 0:
        username = py_obj["result"]["username"]

    return username


def execute_script(org_alias, apex_file):

    py_obj = sfdx.execute_script(org_alias, apex_file)

    if py_obj["status"] == 1:
        message = py_obj["message"]
        logging.error(f"MESSAGE: {message}")
        logging.error(
            f"CompileProblem: {py_obj['result']['compileProblem']}\nExceptionMessage: {py_obj['result']['exceptionMessage']}"
        )
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj["status"] == 0:
        logging.warning(f"{py_obj}")

    return True


def install_package(org_alias, package_id):

    py_obj = sfdx.install_package(org_alias, package_id)

    if py_obj["status"] == 1:
        message = py_obj["message"]
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj["status"] == 0:
        install_status = py_obj["result"]["Status"]
        while install_status == "IN_PROGRESS":
            install_status = check_install(org_alias, py_obj["result"]["Id"])

    return True


def install_permission_set(org_alias, pset):

    py_obj = sfdx.install_permission_set(org_alias, pset)

    if py_obj["status"] == 1:
        message = py_obj["result"]["failures"][0]["message"]
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")

    if py_obj["status"] == 0:
        logging.info(f"{py_obj}")

    return True


def install_source(org_alias, src_folder):

    py_obj = sfdx.install_source(org_alias, src_folder)

    if py_obj["status"] == 1:
        message = py_obj["message"]
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj["status"] == 0:
        for item in py_obj["result"]["deployedSource"]:
            logging.info(
                f"Type: {item['type']}, State: {item['state']}, Name: {item['fullName']}"
            )

    return True


def package_list(org_alias):

    py_obj = sfdx.package_list(org_alias)

    packages = []

    if py_obj["status"] == 1:
        message = py_obj["message"]
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj["status"] == 0:
        for item in py_obj["result"]:
            logging.info(
                f"Name: {item['SubscriberPackageName']}, Version: {item['SubscriberPackageVersionNumber']}, Version Id: {item['SubscriberPackageVersionId']}"
            )
            packages.append(item["SubscriberPackageVersionId"])

    return packages


def publish_community(org_alias, community):

    py_obj = sfdx.publish_community(org_alias, community)

    if py_obj["status"] == 1:
        message = py_obj["message"]
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj["status"] == 0:
        logging.error(f"Name \t: {py_obj['result']['name']}")
        logging.error(f"Status \t: {py_obj['result']['status']}")
        logging.error(f"url \t: {py_obj['result']['url']}")

    return True


def source_push(org_alias):

    py_obj = sfdx.source_push(org_alias, True)

    if py_obj["status"] == 1:
        logging.warning(f"{py_obj}")
        message = py_obj["message"]
        logging.error(f"MESSAGE: {message}")
        sys.exit(1)

    if py_obj["status"] == 0:
        for item in py_obj["result"]["pushedSource"]:
            logging.info(
                f"Type: {item['type']}, State: {item['state']}, Name: {item['fullName']}"
            )

    return True


def user_details(org_alias):

    py_obj = sfdx.user_details(org_alias)

    if py_obj["status"] == 1:
        message = py_obj["message"]
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{py_obj}")
        sys.exit(1)

    if py_obj["status"] == 0:
        logging.error(f"OrgId \t: {py_obj['result']['orgId']}")
        logging.error(f"Username \t: {py_obj['result']['username']}")
        logging.error(f"Url \t: {py_obj['result']['instanceUrl']}")
        logging.error(f"Alias \t: {py_obj['result']['alias']}")


def main():
    logging.debug("main()")

    cfg = get_config()
    dir_path = os.getcwd()

    setup_args(cfg)
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
        username = create_sratch_org(
            args.alias, args.duration, args.devhub, cfg["SCRATCH_DEF"]
        )

    if cfg["PACKAGE_IDS"]:
        installed = package_list(args.alias)

        for pckg in cfg["PACKAGE_IDS"]:
            if pckg not in installed:
                logging.error(f"~~~ Installing Packages {pckg} ~~~")
                install_package(args.alias, pckg)

    if cfg["PRE_DEPLOY"]:
        for fldr in cfg["PRE_DEPLOY"]:
            logging.error(f"~~~ Installing Source ({fldr}) ~~~")
            install_source(args.alias, f"{dir_path}/{fldr}")

    if cfg["PACKAGE_P_SETS"]:
        for pset in cfg["PACKAGE_P_SETS"]:
            logging.error(f"~~~ Installing Permission Set ({pset}) ~~~")
            install_permission_set(args.alias, pset)

    logging.error("~~~ Installing Source ~~~")
    source_push(args.alias)

    if cfg["SRC_FOLDERS"]:
        for fldr in cfg["SRC_FOLDERS"]:
            logging.error(f"~~~ Installing Source ({fldr}) ~~~")
            install_source(args.alias, f"{dir_path}/{fldr}")

    if cfg["P_SETS"]:
        for pset in cfg["P_SETS"]:
            logging.error(f"~~~ Installing Permission Set ({pset}) ~~~")
            install_permission_set(args.alias, pset)

    if cfg["TMPLT_NAME"]:
        logging.error(f"~~~ Create Community({cfg['SITE_NAME']}) ~~~")
        # create_community(org_alias, SITE_NAME, TMPLT_NAME)

    if cfg["BUILD_DATA_CMD"]:
        for script in cfg["BUILD_DATA_CMD"]:
            logging.error(f"~~~ Running Build data({script}) ~~~")
            execute_script(args.alias, script)

    if cfg["SITE_NAME"]:
        logging.error(f"~~~ Publish Community({cfg['SITE_NAME']}) ~~~")
        publish_community(args.alias, cfg["SITE_NAME"])

    if cfg["POST_DEPLOY"]:
        for fldr in cfg["POST_DEPLOY"]:
            logging.error(f"~~~ Installing Source ({fldr}) ~~~")
            install_source(args.alias, f"{dir_path}/{fldr}")

    logging.error("~~~ Details ~~~")
    user_details(args.alias)

    logging.error("~~~ Scratch Org Complete ~~~")
