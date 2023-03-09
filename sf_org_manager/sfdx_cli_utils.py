# sfdx_cli_utils.py
__version__ = "0.0.2"

import json
import logging
import platform
import subprocess
import sys
import time

# sfdx command.
if platform.system() == "Linux":
    SFDX_CMD = "sfdx"
if platform.system() == "Windows":
    SFDX_CMD = "sfdx.cmd"

# Config
#
SLEEP_SEC = 120
#


def parse_output(cmd_output):

    logging.warning(f"ARGS: {cmd_output.args}")
    logging.debug(f"\n{cmd_output}\n")

    py_obj = {}

    if cmd_output.stderr != b"" and cmd_output.stdout == b"":
        if "Warning: sfdx-cli update available" not in str(cmd_output.stderr):
            logging.error(f"STDERR: {cmd_output.stderr}")
            sys.exit(1)

    if cmd_output.stdout != b"":
        py_obj = json.loads(cmd_output.stdout)

    logging.debug(json.dumps(py_obj, sort_keys=True, indent=3))

    return py_obj


def check_install(org_alias: str, status_id: str):
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
            "--json",
        ],
        capture_output=True,
    )

    return parse_output(out)


def create_community(org_alias: str, community: str, template: str):
    logging.debug(f"create_community({org_alias}, {community}, {template})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:community:create",
            "-u",
            f"{org_alias}",
            "-n",
            f"{community}",
            "-t",
            f"{template}",
            "-p",
            "demosite",
            "--json",
        ],
        capture_output=True,
    )

    time.sleep(120)
    return parse_output(out)


def create_sratch_org(org_alias: str, duration: str, devhub: str, scratch_def: str):
    logging.debug(f"create_sratch_org({org_alias}, {duration}, {devhub})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "org",
            "create",
            "scratch",
            "-f",
            f"{scratch_def}",
            "-d",
            "-y",
            f"{duration}",
            "-a",
            f"{org_alias}",
            "-v",
            f"{devhub}",
            "--json",
        ],
        capture_output=True,
    )

    return parse_output(out)


def execute_script(org_alias: str, apex_file: str):
    logging.debug(f"execute_script({org_alias}, {apex_file})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "apex",
            "run",
            "-f",
            f"{apex_file}",
            "-o",
            f"{org_alias}",
            "--json",
        ],
        capture_output=True,
    )

    return parse_output(out)


def install_package(org_alias: str, package_id: str):
    logging.debug(f"install_package({org_alias})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "package",
            "install",
            "-p",
            f"{package_id}",
            "-o",
            f"{org_alias}",
            "-r",
            "--json",
        ],
        capture_output=True,
    )

    return parse_output(out)


def install_permission_set(org_alias: str, pset: str):
    logging.debug(f"install_permission_Set({org_alias}, {pset})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "org",
            "assign",
            "permset",
            "-n",
            f"{pset}",
            "-o",
            f"{org_alias}",
            "--json",
        ],
        capture_output=True,
    )

    return parse_output(out)


def install_source(org_alias: str, src_folder: str):
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
            "--json",
        ],
        capture_output=True,
    )

    return parse_output(out)


def org_list():
    logging.debug("org_list()")

    out = subprocess.run(
        [
            SFDX_CMD,
            "org",
            "list",
            "--all",
            "--json",
        ],
        capture_output=True,
    )

    return parse_output(out)


def org_open(org_user: str):
    logging.debug(f"open_org({org_user})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "org",
            "open",
            "-o",
            f"{org_user}",
            "--json",
        ],
        capture_output=True,
    )

    return parse_output(out)


def package_list(org_alias: str):
    logging.debug(f"package_list({org_alias})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "package",
            "installed",
            "list",
            "-o",
            f"{org_alias}",
            "--json",
        ],
        capture_output=True,
    )

    return parse_output(out)


def publish_community(org_alias: str, community: str):
    logging.debug(f"publish_community({org_alias}, {community})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "force:community:publish",
            "-u",
            f"{org_alias}",
            "-n",
            f"{community}",
            "--json",
        ],
        capture_output=True,
    )

    return parse_output(out)


def source_push(org_alias: str, forceoverwrite: bool):
    logging.debug(f"source_push({org_alias}, {forceoverwrite})")

    if forceoverwrite:
        out = subprocess.run(
            [
                SFDX_CMD,
                "force",
                "source",
                "push",
                "-u",
                f"{org_alias}",
                "--json",
                "-f",
                "-g",
            ],
            capture_output=True,
        )
    else:
        out = subprocess.run(
            [
                SFDX_CMD,
                "force",
                "source",
                "push",
                "-u",
                f"{org_alias}",
                "--json",
            ],
            capture_output=True,
        )

    return parse_output(out)


def user_details(org_alias: str):
    logging.debug(f"user_details({org_alias})")

    out = subprocess.run(
        [
            SFDX_CMD,
            "org",
            "display",
            "user",
            "-o",
            f"{org_alias}",
            "--json",
        ],
        capture_output=True,
    )

    return parse_output(out)
