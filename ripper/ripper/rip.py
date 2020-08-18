# Python built-in imports
import os
import time

from collections import Callable
from typing import Dict, List, Tuple

# Python site-packages imports
import asyncio
import aiohttp
from aiohttp import ClientSession, ClientTimeout
from aiohttp.resolver import AsyncResolver

import ssl
import certifi
import socket

from logging import RootLogger


# Local imports
from ripper.constants import DEFAULT_OUTPUT_FILE_BASE
from ripper.strategies import RIP_MAP
from ripper.file_operations import (
	csv_to_list,
	write_csv)
from ripper.requests import get_headers


def run(csv: str,
		rip_type: str,
		parallelism: int,
		output_directory: str,
		timeout: int,
		logger: RootLogger) -> int:
	""" Ripper script entrypoint to rip web elements from a CSV containing web URLs.

		:param csv: 				Input CSV containing list of web URLs
		:param rip_type: 			Which strategy to use for ripping web elements
		:param parallelism:			Number of parallel requests allowed to be sent at once
		:param output_directory:	Directory where result logs will be written
		:param timeout:				Per request timeout
		:param logger:				Logger for results

		:return status_code:		Status code for success/failure reporting
	"""
	domains = csv_to_list(csv)

	start = time.time()
	successes, failures = asyncio.run(
		rip(domains=domains,
			func=RIP_MAP[rip_type],
			parallelism=parallelism,
			timeout=timeout,
			logger=logger))
	end = time.time()
	print(f"Ripper took: {end-start} seconds")

	if successes:
		write_csv(
			content=sorted(successes, key=lambda x: int(x[0])),
			file=os.path.join(output_directory, DEFAULT_OUTPUT_FILE_BASE.format(
				strategy=rip_type,
				result="success",
				timestamp=time.strftime("%Y%m%d-%H%M%S"))))

	if failures:
		write_csv(
			content=sorted(failures, key=lambda x: int(x[0])),
			file=os.path.join(output_directory, DEFAULT_OUTPUT_FILE_BASE.format(
				strategy=rip_type,
				result="failed",
				timestamp=time.strftime("%Y%m%d-%H%M%S"))))

	return 0

async def rip(domains: list,
			  func: Callable,
			  parallelism: int,
			  timeout: int,
			  logger: logging.RootLogger) -> Tuple[list, list]:
	""" Setup and run a task-list of domains to rip elements from

		:param domains: list of [rank, domain] to rip elements from
		:param func: Callable which performs strategy specific ripping logic
		:param parallelism: Maximum number of simultaneous active requests
		:param timeout: Per request timeout
		:param logger: Logger for results

		:return (successes, failures): Lists of (un)successful rips
	"""
	successes = []
	failures = []
	connector = aiohttp.TCPConnector(
		family=socket.AF_INET,
		ssl=False,
		limit=parallelism,
		resolver=AsyncResolver(nameservers=["8.8.8.8", "8.8.4.4"]))
	ssl_context = ssl.create_default_context(cafile=certifi.where())

	# Many websites refuse traffic from obvious bots
	headers={'Accept': '*/*', 'Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36', 'Accept-Encoding': 'gzip', 'Accept-Language': 'en-US;q=0.5,en;q=0.3', 'Cache-Control': 'max-age=0', 'DNT': '1', 'Upgrade-Insecure-Requests': '1'}


	async with ClientSession(connector=connector, 
							 timeout=ClientTimeout(total=None, sock_connect=5, sock_read=5),
							 headers=headers) as session:
		tasks = []
		# Setup a task list of coroutines (web URLs to be ripped)
		for row in domains:
			tasks.append(
				func(row=row, session=session, ssl_context=ssl_context))
		results = await asyncio.gather(*tasks)

	# Results returns as a list of dictionaries, successful rips will have a 'favicon_url'
	for result in results:
		if result.get("favicon_url"):
			successes.append([result["rank"], result["domain"], result["favicon_url"]])
		else:
			failures.append([result["rank"], result["domain"], result["error"]])

	return successes, failures