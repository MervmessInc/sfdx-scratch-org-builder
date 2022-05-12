import argparse
import logging
import sf_org_manager
import sys

parser = argparse.ArgumentParser(
    prog="org_manager",
    description="""
Python wrapper for Salesforce CLI (sfdx) that list Salesforce orgs.
    """,
)


def setup_args():
    logging.debug("setup_args()")
    parser.add_argument("--debug", help="Turn on debug messages", action="store_true")


def main():
    # Set the Log level
    #
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )
    logger = logging.getLogger()

    setup_args()
    args = parser.parse_args()

    if args.debug:
        logging.error("~~~ Setting up DEBUG ~~~")
        logger.setLevel(logging.INFO)

    logging.info(f"argv[0] ~ {sys.argv[0]}")

    sf_org_manager.org_manager.main()
