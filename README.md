# pythonETL
ETL tool set by python


Extraction Tool

HttpContent

Usage example:

from datetime import date
from znfro_http_get_source import HttpContent
			
link = "https://www.google.com/"
contains = [
				'google',
			]

archiver = HttpContent()

responseCode, html = archiver.getSource(link, False, contains, [])
if responseCode==808:
	print("Essential content not found!")
else:
	print(html) 

...