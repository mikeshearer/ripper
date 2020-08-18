from ripper.strategies.favicon import rip as rip_favicon
from ripper.strategies.title import rip as rip_title
from ripper.constants import (FAVICON, TITLE)

RIP_MAP = {
	FAVICON: rip_favicon,
	TITLE: rip_title
}