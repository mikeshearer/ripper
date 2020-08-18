# Python built-in imports
from http import HTTPStatus

import os

# Python site-packages imports
import aiohttp
import asyncio

from bs4 import BeautifulSoup
from ssl import SSLContext
from urllib.parse import urlparse

# Local imports
from ripper.requests import fetch, READ, TEXT

async def rip(row: list,
			  session: aiohttp.ClientSession,
			  ssl_context: SSLContext) -> dict:
	""" Strategy to rip favicons from websites. Favicons are most often found in 3 places:
		1. {domain}/favicon.ico
		2. In markup with a <link> tag with rel="shortcut icon" attribute
		3. In markup with a <link> tag with rel="icon"
		Rip attempts to find the favicon in all three locations (in this order)

		:param row: Row of the initial CSV file with format <rank>,<domain>
		:param session: Client Session that we'll share for all requests
		:param ssl_context: certificate manager

		:return results: Results from attempting to rip the favicon
	"""
	favicon_url = None
	rank, domain = row
	results = {"rank": rank, "domain": domain, "favicon_url": favicon_url, "error": None}

	try:
		url = await to_favicon_url(domain)
		response = await fetch(url=url, session=session, ssl_context=ssl_context)
		results["favicon_url"] = response.url.__str__()
		return results
	except (
		aiohttp.http_exceptions.HttpProcessingError,
		aiohttp.ClientResponseError,
		asyncio.TimeoutError,
		aiohttp.client_exceptions.ServerTimeoutError,
		aiohttp.client_exceptions.ServerDisconnectedError,
		aiohttp.client_exceptions.ClientConnectorError,
		aiohttp.client_exceptions.ClientOSError) as e:
		error = e
	except (aiohttp.client_exceptions.InvalidURL, ValueError, Exception) as e:
		print(url, str(e))

	try:
		url = await add_scheme(domain)
		response = await fetch(url=url, session=session, ssl_context=ssl_context)
		favicon_url = await parse_markup(await response.text(), domain)
		results["favicon_url"] = favicon_url
		return results
	except (
		aiohttp.http_exceptions.HttpProcessingError,
		aiohttp.ClientResponseError,
		aiohttp.ClientConnectionError,
		asyncio.TimeoutError,
		aiohttp.client_exceptions.ServerTimeoutError,
		aiohttp.client_exceptions.ServerDisconnectedError,
		aiohttp.client_exceptions.ClientConnectorError,
		aiohttp.client_exceptions.ClientOSError) as e:
		results["error"] = str(e)
	except aiohttp.client_exceptions.InvalidURL as e:
		print(url, str(e))
	except (Exception, ValueError) as e:
		print(url, str(e))
		error = e
		results["error"] = str(e)

	return results

async def to_favicon_url(domain):
	""" Return the default favicon URL given a domain.

		:param domain: base domain that we want to search

		:return favicon_url: Standard favicon URL for the target domain
	"""
	return f"http://{domain}/favicon.ico"

async def add_scheme(url) -> str:
	"""	Add 'http://' to any url which doesn't start with it already

		:param url: url to add a scheme to

		:return url: url with the scheme added (if it didn't have one already)
	"""
	if not url.startswith("http"):
		return f"http://{url}"
	return url

async def parse_markup(content, url) -> str:
	"""	Search html for references to the favicon URL

		:param content: Website's html content
		:param url: 	Website's base domain (required for rebuilding absolute URLs)

	"""
	favicon_url = None
	parsed_url = await add_scheme(url)
	parsed_url = urlparse(parsed_url)

	soup = BeautifulSoup(content, features="html.parser")

	favicon_ref = soup.find("link", rel="icon") or soup.find("link", rel="shortcut icon")

	if favicon_ref and favicon_ref.has_attr("href"):
		favicon_url = favicon_ref["href"]

		if favicon_url.startswith("//"):
			favicon_url = f"{parsed_url.scheme}:{favicon_url}"
		elif favicon_url.startswith("/"):
			favicon_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{favicon_url}"
		elif favicon_url.startswith("data"):
			favicon_url = favicon_url
		elif not favicon_url.startswith("http"):
			path, filename = os.path.split(parsed_url.path)
			favicon_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{os.path.join(path, favicon_url)}"

	return favicon_url