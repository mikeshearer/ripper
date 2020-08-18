# Python Built-in imports
import os
import sys

# Python site-package imports
from argparse import ArgumentParser, Namespace

# Local imports
from ripper.constants import (
	FAVICON,
	SUPPORTED_RIPS)
from ripper.logger import get_logger
from ripper.rip import run

def parse_args() -> Namespace:
	""" Define and parse command line arguments
	
		:return argparse.Namespace Contains references to all parsed arguments and default values
	"""
	parser = ArgumentParser()

	parser.add_argument("input_csv", help="CSV file with format <rank>,<domain>")
	parser.add_argument("--parallelism",
						type=int,
						default=100,
						help="Max parallelism allowed when making HTTP requests")
	parser.add_argument("--rip_type",
						default=FAVICON,
						choices=SUPPORTED_RIPS,
						help=f"Strategy to rip various elements from websites. Options: {', '.join(SUPPORTED_RIPS)}")
	parser.add_argument("--output_directory",
						default=os.getcwd(),
						help="Directory where results files will be written",
						)
	parser.add_argument("--timeout",
						default=5,
						type=int,
						help="Timeout for individual HTTP requests")
	return parser.parse_args()


def main() -> int:
	""" Entry point for ripper script from the command line

	:return int status code (0 for success)
	"""
	args = parse_args()
	logger = get_logger()

	status = 0

	# try:
	status = run(
		csv=args.input_csv,
		rip_type=args.rip_type,
		parallelism=args.parallelism,
		output_directory=args.output_directory,
		timeout=args.timeout,
		logger=logger
	)
	# except Exception as e:
	# 	logger.error(f"Ripper failed with: {type(e)} {str(e)}")
	# 	status = 1
	# finally:
	# 	logger.info(f"Ripper complete - Exited with status code: {status}")


main()