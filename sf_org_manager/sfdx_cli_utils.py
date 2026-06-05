# sfdx_cli_utils.py

import json
import logging
import platform
import subprocess
import sys
import time

# sfdx command — use 'sf' on macOS/Linux, 'sf.cmd' on Windows
if platform.system() == "Windows":
    SFDX_CMD = "sf.cmd"
else:
    SFDX_CMD = "sf"

# Config
SLEEP_SEC = 120


def parse_output(cmd_output):
    logging.debug("parse_output(cmd_output)")
    logging.debug(f"ARGS: {cmd_output.args}")

    if not cmd_output.stdout and not cmd_output.stderr:
        logging.error(f"NO OUTPUT ~ {cmd_output}")
        sys.exit(1)

    if cmd_output.stderr and not cmd_output.stdout:
        logging.error(f"STDERR: {cmd_output.stderr}")
        sys.exit(1)

    try:
        py_obj = json.loads(cmd_output.stdout)
    except json.JSONDecodeError as exc:
        logging.error(f"Failed to parse JSON output: {exc}\nRaw: {cmd_output.stdout!r}")
        sys.exit(1)

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
            "community",
            "create",
            "--name",
            f"{community}",
            "--template-name",
            f"{template}",
            "--url-path-prefix",
            "demosite",
            "--target-org",
            f"{org_alias}",
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
            "community",
            "publish",
            "--name",
            f"{community}",
            "--target-org",
            f"{org_alias}",
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

    py_obj = parse_output(out)

    if py_obj.get("status") == 0 and "result" in py_obj:
        token = py_obj["result"].get("accessToken", "")
        if "[REDACTED]" in token:
            logging.debug("Token redacted, fetching with org auth show-access-token")
            token_out = subprocess.run(
                [
                    SFDX_CMD,
                    "org",
                    "auth",
                    "show-access-token",
                    "-o",
                    f"{org_alias}",
                    "--json",
                ],
                capture_output=True,
                encoding="utf-8",
            )
            token_py_obj = parse_output(token_out)
            if token_py_obj.get("status") == 0 and "result" in token_py_obj:
                py_obj["result"]["accessToken"] = token_py_obj["result"].get(
                    "accessToken", ""
                )

    return py_obj
