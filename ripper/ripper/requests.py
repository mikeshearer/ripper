# Python built-in imports

# Python site-package imports
from aiohttp import ClientSession, ClientResponse
from fake_headers import Headers
from ssl import SSLContext

from typing import Optional

READ = "read"
TEXT = "text"


def get_headers(browser="chrome", os="win") -> dict:
	""" Get fake headers for use in making requests.
		*Note* This requires the installation of brolipy

		:param browser: Seed the header generation with a specific browser
		:param os:		Seed the header generation with a specific OS

		:return headers: Fake headers as a dictionary
	"""
	return Headers(
		browser=browser,
		os=os,
		headers=True
	).generate()

async def fetch(url: str, session: ClientSession, ssl_context: SSLContext) -> ClientResponse:
	""" Make an asynchronous HTTP GET request using aiohttp
	"""
	response = await session.get(url)
	response.raise_for_status()
	return response

async def head(url, session, ssl_context):
	response = await session.head(url)
	response.raise_for_status()
	return response

