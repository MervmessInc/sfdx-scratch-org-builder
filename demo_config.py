# Default duration in days
DURATION = 10

# Default Devhub
DEVHUB = "hub-org"

# List of managed package Ids to install into the Org.
# Sage People Recruit ~ 04t1W000000kpEg
PACKAGE_IDS = [
    "04t1W000000kpEg",
    "04t4K000002O66eQAC",
    "04t4K000002O6CdQAK"
]

# List of managed package permission sets to assign to the user.
PACKAGE_P_SETS = [
    "Sage_People_Recruit_Administrator",
    "Sage_People_HR_Administrator_fRecruit"
]

# Pre-Deploy use if metadata deploy sequence is important.
PRE_DEPLOY = [
    "buildData\main\default\classes\BuildData.cls"
]

# List of metadata source folders (SRC_FOLDERS = ["force-app"])
SRC_FOLDERS = []

# Anonymous APEX file to execute ("setupdata.apex")
BUILD_DATA_CMD =  "scripts/apex/buildData.apex"

# List of permission sets to assign to the user.
P_SETS = []

# Post-Deploy
# Deploy the profile again as does not work 
# until the community has been created.
POST_DEPLOY = []