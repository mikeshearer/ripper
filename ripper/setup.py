import ast
import re

import setuptools

_version_re = re.compile(r"__version__\s+=\s+(.*)")
with open("ripper/__init__.py", "rb") as f:
	match = _version_re.search(f.read().decode("utf-8"))
	if match is None:
		raise SystemExit(1)
	version = str(ast.literal_eval(_match.group(1)))

setuptools.setup(
	name="ripper",
	version=version,
	url="https://https://github.com/mikeshearer/ripper",
	author="Mike Shearer",
	author_email="MikeSShearer@gmail.com",
	description="Scripts for asynchronously ripping elements from lists of websites",
	long_description=open("README.md").read(),
	packages=setuptools.find_packages(
		exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
	),
	install_requires=[],
	classifiers=[
		"Development Status :: 2 - Pre-Alpha",
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.7",
	],
)