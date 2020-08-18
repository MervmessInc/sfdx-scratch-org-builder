# sfdx_scratch_org_builder

Python wrapper for a number of Salesforce CLI (sfdx) commands, to build and setup Scratch Orgs.

## Usage

org_builder [-h] [-a ALIAS] [-d DURATION] [-v DEVHUB] [--debug]

arguments:

  -h, --help            show help message and exit

  -a ALIAS, --alias ALIAS
                        Scratch Org user alias

  -d DURATION, --duration DURATION
                        Number of days org will last [1..30]. Default: 10

  -v DEVHUB, --devhub DEVHUB
                        Target dev hub username or alias. Default: my-dev-hub-org

  --debug               Turn on debug messages

## Config

Edit the follow value in the to enable specfic org setup features.

**PACKAGE_IDS = []** List of managed package Ids to install into the Org.

**PACKAGE_P_SETS = []** List of permission sets to assign to the user.

**SRC_FOLDERS = []** List of metadata source folders (SRC_FOLDERS = ["force-app"])

**BUILD_DATA_CMD = ""** Name of Anonymous APEX file to execute ("setupdata.apex")

**P_SETS = []** List of permission sets to assign to the user.
