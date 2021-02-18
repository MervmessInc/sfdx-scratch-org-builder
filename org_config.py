import platform

# sfdx command.
if platform.system() == 'Linux':
    SFDX_CMD = "sfdx"
if platform.system() == 'Windows':
    SFDX_CMD = "sfdx.cmd"

# Scratch Org Definition File
SCRATCH_DEF = "config/project-scratch-def.json"

# Default duration in days
DURATION = 10

# Default Devhub
DEVHUB = "my-dev-hub-org"

# List of managed package Ids to install into the Org.
PACKAGE_IDS = []

# List of managed package permission sets to assign to the user.
PACKAGE_P_SETS = []

# Pre-Deploy use if metadata deploy sequence is important.
PRE_DEPLOY = []

# List of metadata source folders (SRC_FOLDERS = ["force-app"])
SRC_FOLDERS = []

# Anonymous APEX file to execute ("setupdata.apex")
BUILD_DATA_CMD = ""

# List of permission sets to assign to the user.
P_SETS = []
