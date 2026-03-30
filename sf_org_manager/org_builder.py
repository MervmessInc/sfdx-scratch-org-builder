# org_builder.py

import argparse
import logging
import os
import sys
import yaml

from . import sfdx_cli_utils as sfdx


def get_config(config_file):
    if os.path.isfile(config_file):
        with open(config_file, "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
    else:
        logging.error(f"Missing config file: {config_file}")
        sys.exit(1)

    return cfg


def setup_args(cfg):
    parser = argparse.ArgumentParser(
        prog="org_builder",
        description="Python wrapper for a number of Salesforce CLI (sf) commands, to build and setup Scratch Orgs.",
    )
    parser.add_argument("-a", "--alias", help="Scratch Org user alias", type=str)
    parser.add_argument(
        "-d",
        "--duration",
        help=f"Number of days org will last [1..30]. Default: {cfg['DURATION']}",
        default=cfg["DURATION"],
        type=int,
    )
    parser.add_argument(
        "-v",
        "--devhub",
        help=f"Target dev hub username or alias. Default: {cfg['DEVHUB']}",
        default=cfg["DEVHUB"],
        type=str,
    )
    parser.add_argument(
        "-e",
        "--email",
        help="Email address that will be applied to the org's admin user",
        type=str,
    )
    parser.add_argument("--debug", help="Turn on debug messages", action="store_true")
    parser.add_argument("--skip", help="Skip source deploy", action="store_true")
    return parser


def check_install(org_alias, status_id):
    py_obj = sfdx.check_install(org_alias, status_id)

    if py_obj["status"] == 1:
        logging.error(f"MESSAGE: {py_obj.get('message', 'Unknown error')}")
        sys.exit(1)

    status = py_obj["result"]["Status"]
    logging.info(f"Checking package install status ~ {status}")
    return status


def check_org(org_alias):
    py_obj = sfdx.org_list()
    scratch_orgs = py_obj.get("result", {}).get("scratchOrgs", [])

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


def create_sratch_org(org_alias, duration, devhub, email, config):
    preview = config.get("PREVIEW", False)

    py_obj = sfdx.create_sratch_org(
        org_alias,
        duration,
        devhub,
        config["SCRATCH_DEF"],
        config["USE_NAMESPACE"],
        email,
        preview,
    )

    if py_obj["status"] == 1:
        logging.error(f"MESSAGE: {py_obj.get('message', 'Unknown error')}")
        sys.exit(1)

    return py_obj["result"]["username"]


def execute_script(org_alias, apex_file):
    py_obj = sfdx.execute_script(org_alias, apex_file)

    if py_obj["status"] == 1:
        logging.error(f"MESSAGE: {py_obj.get('message', 'Unknown error')}")
        sys.exit(1)

    logging.debug(f"{py_obj}")
    return True


def install_package(org_alias, package_id):
    py_obj = sfdx.install_package(org_alias, package_id)

    if py_obj["status"] == 1:
        logging.error(f"MESSAGE: {py_obj.get('message', 'Unknown error')}")
        sys.exit(1)

    install_status = py_obj["result"]["Status"]
    while install_status == "IN_PROGRESS":
        install_status = check_install(org_alias, py_obj["result"]["Id"])

    return True


def install_permission_set(org_alias, pset):
    py_obj = sfdx.install_permission_set(org_alias, pset)

    if py_obj["status"] == 1:
        message = py_obj.get("result", {}).get("failures", [{}])[0].get("message", "Unknown error")
        logging.error(f"MESSAGE: {message}")

    logging.info(f"{py_obj}")
    return True


def install_source(org_alias, src_folder):
    py_obj = sfdx.install_source(org_alias, src_folder)

    if py_obj["status"] == 1:
        if "message" in py_obj:
            logging.info(f"MESSAGE: {py_obj['message']}")
            if py_obj.get("name") != "NothingToDeploy":
                sys.exit(1)

        if "result" in py_obj:
            if "details" in py_obj["result"]:
                message = py_obj["result"]["details"]
                for item in message.get("componentFailures", []):
                    logging.error(
                        f"Type: {item['componentType']}, Error: {item['problem']}, Item: {item['fileName']}"
                    )
                for item in message.get("componentSuccesses", []):
                    logging.debug(
                        f"Type: {item['componentType']}, Filename: {item['fileName']}, Name: {item['fullName']}"
                    )
            sys.exit(1)

    if py_obj["status"] == 0:
        if "result" in py_obj:
            if "status" in py_obj["result"]:
                logging.info(f"STATUS: {py_obj['result']['status']}")
            if "details" in py_obj["result"]:
                for item in py_obj["result"]["details"].get("componentSuccesses", []):
                    logging.info(
                        f"Type: {item['componentType']}, Filename: {item['fileName']}, Name: {item['fullName']}"
                    )

    return True


def package_list(org_alias):
    py_obj = sfdx.package_list(org_alias)
    packages = []

    if py_obj["status"] == 1:
        logging.error(f"MESSAGE: {py_obj.get('message', 'Unknown error')}")
        sys.exit(1)

    for item in py_obj.get("result", []):
        logging.info(
            f"Name: {item['SubscriberPackageName']}, "
            f"Version: {item['SubscriberPackageVersionNumber']}, "
            f"Version Id: {item['SubscriberPackageVersionId']}"
        )
        packages.append(item["SubscriberPackageVersionId"])

    return packages


def publish_community(org_alias, community):
    py_obj = sfdx.publish_community(org_alias, community)

    if py_obj["status"] == 1:
        logging.error(f"MESSAGE: {py_obj.get('message', 'Unknown error')}")
        sys.exit(1)

    logging.info(f"Name \t: {py_obj['result']['name']}")
    logging.info(f"Status \t: {py_obj['result']['status']}")
    logging.info(f"url \t: {py_obj['result']['url']}")
    return True


def source_push(org_alias):
    py_obj = sfdx.source_push(org_alias, True)
    logging.debug(f"{py_obj}")

    if py_obj["status"] == 1:
        if "message" in py_obj:
            logging.info(f"MESSAGE: {py_obj['message']}")

        if "result" in py_obj:
            if "details" in py_obj["result"]:
                message = py_obj["result"]["details"]
                for item in message.get("componentFailures", []):
                    logging.error(
                        f"Type: {item['componentType']}, Error: {item['problem']}, Item: {item['fileName']}"
                    )
                for item in message.get("componentSuccesses", []):
                    logging.debug(
                        f"Type: {item['componentType']}, Filename: {item['fileName']}, Name: {item['fullName']}"
                    )

        sys.exit(1)

    if py_obj["status"] == 0:
        if "result" in py_obj:
            if "status" in py_obj["result"]:
                logging.info(f"STATUS: {py_obj['result']['status']}")
            if "details" in py_obj["result"]:
                for item in py_obj["result"]["details"].get("componentSuccesses", []):
                    logging.info(
                        f"Type: {item['componentType']}, Filename: {item['fileName']}, Name: {item['fullName']}"
                    )

    return True


def user_details(org_alias):
    py_obj = sfdx.user_details(org_alias)

    if py_obj["status"] == 1:
        logging.error(f"MESSAGE: {py_obj.get('message', 'Unknown error')}")
        sys.exit(1)

    logging.info(f"OrgId \t: {py_obj['result']['orgId']}")
    logging.info(f"Username \t: {py_obj['result']['username']}")
    logging.info(f"Url \t: {py_obj['result']['instanceUrl']}")
    logging.info(f"Alias \t: {py_obj['result']['alias']}")


def main(config_file="./org_config.yml"):
    # Initialise logging first so errors during config load are visible.
    # Use a quick sys.argv scan for --debug rather than waiting for argparse.
    logging.basicConfig(
        level=logging.DEBUG if "--debug" in sys.argv else logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )

    cfg = get_config(config_file)
    dir_path = os.getcwd()

    parser = setup_args(cfg)
    args = parser.parse_args()

    if args.alias is None:
        parser.print_help()
        sys.exit(0)

    logging.info("~~~ Setting up Scratch Org ~~~")
    logging.debug(f"{args}")

    logging.info("~~~ Check if Org Already Exists ~~~")
    username, org_exists = check_org(args.alias)

    if not org_exists:
        logging.info("~~~ Create New Scratch Org ~~~")
        username = create_sratch_org(args.alias, args.duration, args.devhub, args.email, cfg)

    if cfg["PACKAGE_IDS"]:
        logging.info("~~~ Check Installed Packages ~~~")
        installed = package_list(args.alias)
        for pckg in cfg["PACKAGE_IDS"]:
            if pckg not in installed:
                logging.info(f"~~~ Installing Package {pckg} ~~~")
                install_package(username, pckg)

    if cfg["PRE_DEPLOY"]:
        for fldr in cfg["PRE_DEPLOY"]:
            logging.info(f"~~~ Installing Source ({fldr}) ~~~")
            install_source(args.alias, f"{dir_path}/{fldr}")

    if cfg["PACKAGE_P_SETS"]:
        for pset in cfg["PACKAGE_P_SETS"]:
            logging.info(f"~~~ Installing Permission Set ({pset}) ~~~")
            install_permission_set(args.alias, pset)

    if args.skip:
        logging.info("~~~ Skipping Source Deploy ~~~")
    else:
        logging.info("~~~ Source Deploy ~~~")
        source_push(args.alias)

    if cfg["SRC_FOLDERS"]:
        for fldr in cfg["SRC_FOLDERS"]:
            logging.info(f"~~~ Installing Source ({fldr}) ~~~")
            install_source(args.alias, f"{dir_path}/{fldr}")

    if cfg["P_SETS"]:
        for pset in cfg["P_SETS"]:
            logging.info(f"~~~ Installing Permission Set ({pset}) ~~~")
            install_permission_set(args.alias, pset)

    if cfg["TMPLT_NAME"]:
        logging.info(f"~~~ Create Community ({cfg['SITE_NAME']}) ~~~")
        # create_community(args.alias, cfg["SITE_NAME"], cfg["TMPLT_NAME"])

    if cfg["BUILD_DATA_CMD"]:
        for script in cfg["BUILD_DATA_CMD"]:
            logging.info(f"~~~ Running Build data ({script}) ~~~")
            execute_script(args.alias, script)

    if cfg["SITE_NAME"]:
        logging.info(f"~~~ Publish Community ({cfg['SITE_NAME']}) ~~~")
        publish_community(args.alias, cfg["SITE_NAME"])

    if cfg["POST_DEPLOY"]:
        for fldr in cfg["POST_DEPLOY"]:
            logging.info(f"~~~ Installing Source ({fldr}) ~~~")
            install_source(args.alias, f"{dir_path}/{fldr}")

    logging.info("~~~ Details ~~~")
    user_details(args.alias)

    logging.info("~~~ Scratch Org Setup Complete ~~~")


if __name__ == "__main__":
    main()
