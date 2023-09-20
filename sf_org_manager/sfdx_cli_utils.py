# sfdx_cli_utils.py
__version__ = "0.0.3"


import json
import logging
import platform
import subprocess
import sys
import time


# sfdx command.
if platform.system() == "Linux":
    SFDX_CMD = "sf"
if platform.system() == "Windows":
    SFDX_CMD = "sf.cmd"

# Config
#
SLEEP_SEC = 120
#


def parse_output(cmd_output):
    logging.debug("parse_output(cmd_output)")
    logging.warning(f"ARGS: {cmd_output.args}")

    py_obj = {}

    if cmd_output.stderr == "" and cmd_output.stdout == "":
        logging.error(f"NO OUTPUT ~ {cmd_output}")
        sys.exit(1)

    if cmd_output.stderr != "" and cmd_output.stdout == "":
        logging.error(f"STDERR: {cmd_output.stderr}")
        if "Warning: sfdx-cli update available" not in str(cmd_output.stderr):
            sys.exit(1)

    if cmd_output.stdout != "":
        js_str = cmd_output.stdout[cmd_output.stdout.index("{") :]
        py_obj = json.loads(js_str)

    logging.debug(json.dumps(py_obj, sort_keys=True, indent=3))

    return py_obj


def check_install(org_alias: str, status_id: str):
    logging.debug(f"check_install({org_alias}, {status_id})")

    time.sleep(SLEEP_SEC)

    out = subprocess.run(
        [
            SFDX_CMD,
            "package",
            "install",
            "report",
            "-o",
            f"{org_alias}",
            "-i",
            f"{status_id}",
            "--json",
        ],
        capture_output=True,
        encoding="utf-8",
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
        encoding="utf-8",
    )

    time.sleep(120)
    return parse_output(out)


def create_sratch_org(
    org_alias: str,
    duration: str,
    devhub: str,
    scratch_def: str,
    use_namepspace: bool,
    email: str = None,
    preview: bool = False,
):
    logging.debug(
        f"create_sratch_org({org_alias}, {duration}, {devhub}, {scratch_def}, {use_namepspace}, {email}, {preview})"
    )

    cmd = [
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
    ]

    if not use_namepspace:
        cmd.append("--no-namespace")

    if email:
        cmd.append("--admin-email")
        cmd.append(f"{email}")

    if preview:
        cmd.append("--release")
        cmd.append("preview")

    out = subprocess.run(
        cmd,
        capture_output=True,
        encoding="utf-8",
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
        encoding="utf-8",
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
        encoding="utf-8",
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
        encoding="utf-8",
    )

    return parse_output(out)


def install_source(org_alias: str, src_folder: str):
    logging.debug(f"install_source({org_alias}, {src_folder})")

    return source_push(org_alias, False, src_folder)


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
        encoding="utf-8",
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
        encoding="utf-8",
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
        encoding="utf-8",
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
        encoding="utf-8",
    )

    return parse_output(out)


def source_push(org_alias: str, forceoverwrite: bool, src_folder: str = None):
    logging.debug(f"source_push({org_alias}, {forceoverwrite}, {src_folder})")

    cmd = [
        SFDX_CMD,
        "project",
        "deploy",
        "start",
        "-o",
        f"{org_alias}",
        "--json",
    ]

    if forceoverwrite:
        cmd.append("-c")
        cmd.append("-g")

    if src_folder:
        cmd.append("-d")
        cmd.append(f"{src_folder}")

    out = subprocess.run(
        cmd,
        capture_output=True,
        encoding="utf-8",
    )

    return parse_output(out)


def source_pull(org_alias: str, metadata: str = None):
    logging.debug(f"source_pull({org_alias}, {metadata})")

    cmd = [
        SFDX_CMD,
        "project",
        "retrieve",
        "start",
        "-o",
        f"{org_alias}",
        "--json",
    ]

    if metadata:
        cmd.append("-m")
        cmd.append(f"{metadata}")

    out = subprocess.run(
        cmd,
        capture_output=True,
        encoding="utf-8",
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
        encoding="utf-8",
    )

    return parse_output(out)
