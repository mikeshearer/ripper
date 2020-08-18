
# Python site-package imports
import csv
from ssl import SSLContext

def csv_to_list(file: str, delimiter=",": str) -> list:
	""" Read a csv into a 2D list (list of lists)

		:param file: 		Filename reference
		:param delimiter:	Column delimiter used in the file

		:return contents: 	CSV contents as a list of lists
	"""
	contents = []
	with open(file, 'r') as f:
		reader = csv.reader(f, delimiter=delimiter)
		contents = [row for row in reader]
	return contents

def write_csv(content: list, file: str, delimiter=",": str) -> None:
	"""	Write content to a CSV *or TSV or anything based on the input delimiter

		:param content: 	List of content (rows)
		:param file: 		Destination file to be written to
		:param delimiter:	Delimiter to write the file with

		:return None:
	"""
	with open(file, 'w+') as f:
		writer = csv.writer(f, delimiter=delimiter, quotechar="'", quoting=csv.QUOTE_MINIMAL)
		for row in content:
			writer.writerow(row)