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
```
