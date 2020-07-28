# sfdx_cli_utils.py
__version__ = '0.0.2'

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

# Config
#
SFDX_CMD = "sfdx.cmd"
SLEEP_SEC = 120
SCRATCH_DEF = "config/project-scratch-def.json"
#
#


def parse_output(cmd_output):

    logging.warning(f"ARGS: {cmd_output.args}")
    logging.debug(f"STDOUT:\n{cmd_output.stdout}")
    logging.debug(f"STDERR:\n{cmd_output.stderr}")

    py_obj = {}

    if cmd_output.stderr != b'':
        logging.error(f"STDERR: {cmd_output.stderr}")
        sys.exit(1)

    if cmd_output.stdout != b'':
        py_obj = json.loads(cmd_output.stdout)

    logging.debug(json.dumps(py_obj, sort_keys=True, indent=3))

    return py_obj


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

    return parse_output(out)


def create_sratch_org(org_alias, duration, devhub):
    logging.debug(f"create_sratch_org({org_alias}, {duration}, {devhub})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:org:create",
            "-f",
            f"{SCRATCH_DEF}",
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

    return parse_output(out)


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

    return parse_output(out)


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

    return parse_output(out)


def install_permission_set(org_alias, pset):
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

    return parse_output(out)


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

    return parse_output(out)


def org_list():
    logging.debug(f"org_list()")

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:org:list",
            "--all",
            "--json"
        ],
        capture_output=True
    )

    return parse_output(out)


def org_open(org_user):
    logging.debug(f"open_org({org_user})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:org:open",
            "-u",
            f"{org_user}",
            "--json"
        ],
        capture_output=True
    )

    return parse_output(out)


def user_details(org_alias):
    logging.debug(f"user_details({org_alias})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:user:display",
            "-u",
            f"{org_alias}",
            "--json"
        ],
        capture_output=True
    )

    return parse_output(out)
