# sfdx_scratch_org_builder
org_builder.py is a Salesforce sfdx helper script that builds a fresh scratch org or updates an existing scratch org. Installs dependent pacakges, deploy source code, assign permission sets & builds test data.

## Usage
```
$ py org_builder.py
usage: org_builder [-h] [-a ALIAS] [-d DURATION] [-v DEVHUB] [--debug]

Python wrapper for a number of Salesforce CLI (sfdx) commands, to build and setup Scratch Orgs.

optional arguments:
  -h, --help            show this help message and exit
  -a ALIAS, --alias ALIAS
                        Scratch Org user alias
  -d DURATION, --duration DURATION
                        Number of days org will last [1..30]. Default: 10
  -v DEVHUB, --devhub DEVHUB
                        Target dev hub username or alias. Default: hub-org
  --debug               Turn on debug messages
```

## Config 
[org_config.py](org_config.py).

```
# Scratch Org Definition File
SCRATCH_DEF = "config/project-scratch-def.json"

# Default duration in days
DURATION = 10

# Default Devhub
DEVHUB = "my-hub-org"

# List of managed package Ids to install into the Org.
PACKAGE_IDS = []

# List of managed package permission sets to assign to the user.
PACKAGE_P_SETS = []

# Pre-Deploy use if metadata deploy sequence is important.
PRE_DEPLOY = []

# List of metadata source folders (SRC_FOLDERS = ["force-app"])
SRC_FOLDERS = []

# List of permission sets to assign to the user.
P_SETS = []

# Anonymous APEX files to execute ("setupdata.apex")
BUILD_DATA_CMD = []

# Name of template to use to create the community
TMPLT_NAME = None

# Name of the Lightning community that you want to publish.
SITE_NAME = None

# Post-Deploy use if metadata deploy sequence is important.
POST_DEPLOY = []
```
