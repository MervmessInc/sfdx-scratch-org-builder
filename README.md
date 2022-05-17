# sfdx_scratch_org_builder

## Package Install

```
pip install -e .
```

## sf-orgs

org_manager.py is a Salesforce sfdx helper script that list Salesforce orgs and optionally logs the user in.

### Usage

```
$ sf-orgs -h
usage: org_manager [-h] [--debug]

Python wrapper for Salesforce CLI (sfdx) that list Salesforce orgs.

options:
  -h, --help  show this help message and exit
  --debug     Turn on debug messages
```

```
$ sf-orgs

idx     Alias                          Username                                      Expiration   Status
---     -----                          --------                                      ----------   ------
  1                                    user@brave-goat-76637.com                                  Active
  2                                    user@2gp.testing.net                                       Active
  3     2gp-hub-org                    2pack@2gp.testing.net                                      Active
  4     CCIDevHub                      user@resilient-fox-q2einl.com                              Active
  5     LWC_Workshop                   user@cunning-raccoon-jmz2bj.com                            Active
  6 (D) hub-org                        user@dev-hub-org.com                                       Active
  7     trailhead20190807              user@cunning-bear-7p8yp6.com                               Active
  8                                    test-9lrsnqttbvfm@example.com                 2022-05-23   Active
  9     user-dev                       test-v4ykj3fbwdne@example.com                 2022-06-12   Active
 10 (U) user-dev_II                    test-inilbb6oaint@example.com                 2022-05-23   Active
 11     user-dev_III                   test-8qtkf4vjqxlj@example.com                 2022-05-23   Active

Enter choice 'idx' or 'U' >
```

(D) is the default dev-hub for the sfdx project  
(U) is the default scratch org for the sfdx project

## sf-org_builder

org_builder.py is a Salesforce sfdx helper script that builds a fresh scratch org or updates an existing scratch org. Installs dependent pacakges, deploy source code, assign permission sets & runs annonymous APEX scripts.

### Usage

```
$ sf-org_builder
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

### Config

[org_config.yml](org_config.yml).

```
# Scratch Org Definition File
SCRATCH_DEF: config/project-scratch-def.json

# Default duration in days
DURATION: 10

# Default Devhub
DEVHUB: my-dev-hub-org

# List of managed package Ids to install into the Org.
PACKAGE_IDS: []

# List of managed package permission sets to assign to the user.
PACKAGE_P_SETS: []

# Pre-Deploy use if metadata deploy sequence is important.
PRE_DEPLOY: []

# List of metadata source folders (SRC_FOLDERS = ["force-app"])
SRC_FOLDERS: []

# List of permission sets to assign to the user.
P_SETS: []

# Anonymous APEX files to execute ("setupdata.apex")
BUILD_DATA_CMD: []

# Name of template to use to create the community
TMPLT_NAME:

# Name of the Lightning community that you want to publish.
SITE_NAME:

# Post-Deploy use if metadata deploy sequence is important.
POST_DEPLOY: []
```

## Project dependencies

- Salesforce Developer Experience ([SFDX](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_intro.htm)) CLI tools.
- Python 3.8 : https://www.python.org/downloads/
