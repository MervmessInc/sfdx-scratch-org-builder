# org_manager.py
__version__ = '0.0.1'

import logging
import os
import pickle
import sys

import sfdx_cli_utils as sfdx

# Set the working directory to the location of the file.
#
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

# Set the Log level
#
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger()

def print_org_list(orgs):
    for idx, o in orgs.items():
        print_org_details(idx, o)


def print_org_details(idx, o):
    print(f"{idx} > {o['username']}, Alias : {o['alias']}, DevHub : {o['isDevHub']} {o['defaultMarker']}")


def main():
    logging.debug("main()")

    if os.path.isfile("org_list.p"):
        pyObj = pickle.load( open ( "org_list.p", "rb" ))
    else:
        pyObj = sfdx.org_list()
        pickle.dump(pyObj, open( "org_list.p", "wb" ))

    non_scratch_orgs = pyObj['result']['nonScratchOrgs']
    scratch_orgs = pyObj['result']['scratchOrgs']

    print()

    orgs = {}
    index = 1

    for o in non_scratch_orgs:
        org = {
            index : o
        }
        orgs.update(org)
        index = index + 1

    for o in scratch_orgs:
        dh = { "isDevHub" : False }
        o.update(dh)
        org = {
            index : o
        }
        orgs.update(org)
        index = index + 1

    print_org_list(orgs)

    #choice = orgs.get(1)
    #sfdx.org_open(choice['username'])

if __name__ == '__main__':
    main()