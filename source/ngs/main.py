import argparse
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ngtools')

parser=argparse.ArgumentParser()
subparsers=parser.add_subparsers(help="available subcommands")
