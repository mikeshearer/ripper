import logging
from logging import RootLogger

import sys

def get_logger(level=logging.INFO,
			   handler=logging.StreamHandler(sys.stdout),
			   formatter=logging.Formatter(
			   		"%(asctime)s - %(name)s - %(levelname)s - %(message)s")) -> RootLogger:
	logger = logging.getLogger()
	logger.setLevel(level)

	handler.setFormatter(formatter)
	logger.addHandler(handler)

	return logger

