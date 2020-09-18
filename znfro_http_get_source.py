from selenium import webdriver
from datetime import date
from datetime import datetime
from urllib.parse import urlparse
import aiohttp
import asyncio
import hashlib
import os
import json
import time

class HttpContent():
	_ROOT_CACHE_FOLDER = "../HTTP_ARCHIVE"
	
	def __init__(self):
		# Initialize HttpContent
		self.chrome = None 
		
	async def httpGetSource(self, url, overwrite, mustContain=[], errorContain=[]):
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				# return abnormal return
				if response.status!=200:
					return response.status, response.headers['content-type'], html, False

				# get content in response
				html = await response.text()
					
				# VALIDATION
				if len(errorContain)>0:
					for error in errorContain:
						if error in html:
							# return error if html contain specified error content
							return 858, response.headers['content-type'], html, False
					
				if len(mustContain)>0: 
					for must in mustContain:
						if must not in html:
							# return error if html not contain expected content
							return 808, response.headers['content-type'], html, False
							
				# get date info by today()
				today = date.today()
				year = today.strftime("%Y")
				fdate = today.strftime("%Y-%m-%d")
				
				# create folder year & date folder if not exist
				if not os.path.exists(self._ROOT_CACHE_FOLDER):
					os.makedirs(self._ROOT_CACHE_FOLDER)
				if not os.path.exists(self._ROOT_CACHE_FOLDER + "/" + year):
					os.makedirs(self._ROOT_CACHE_FOLDER + "/" + year)
				if not os.path.exists(self._ROOT_CACHE_FOLDER + "/" + year + "/" + fdate):
					os.makedirs(self._ROOT_CACHE_FOLDER + "/" + year + "/" + fdate)
				
				# get domain
				domain = urlparse(url).netloc
				
				# create domain folder if not exist
				if not os.path.exists(self._ROOT_CACHE_FOLDER + "/" + year + "/" + fdate + "/" + domain):
					os.makedirs(self._ROOT_CACHE_FOLDER + "/" + year + "/" + fdate + "/" + domain)
				
				# get md5 url as filename 
				h = hashlib.md5(bytes(url, 'utf-8'))
				filename = h.hexdigest() + ".html";
				
				# check if archive found
				archiveFilename = self._ROOT_CACHE_FOLDER + "/" + year + "/" + fdate + "/" + domain + "/" + filename;
				if os.path.exists(archiveFilename):	 
					# if archive exist, need to check overwrite parameter to determine do or not
					if overwrite:
						with open(archiveFilename, "w") as outfile:
							outfile.write(html);
				else:
					# if archive not exist, archive page source
					with open(archiveFilename, "w") as outfile:
						outfile.write(html);
					
				return response.status, response.headers['content-type'], html, True
				
				  
	async def chromeGetSource(self, url, overwrite, mustContain=[], errorContain=[]):
		if(self.chrome==None):
			# no browser instance, create one
			option = webdriver.ChromeOptions()
			option.add_argument("--window-size=1024,1024")
			option.add_argument("disable-infobars")
			option.add_argument("--disable-extensions")
			option.add_argument("--disable-dev-shm-usage")
			option.add_argument("--no-sandbox")
			
			# headless
			option.add_argument('--headless')
			option.add_argument('--disable-gpu')
			
			self.chrome = webdriver.Chrome(chrome_options=option)
			#print("Browser instance created....")
		
		
		# Get page content
		self.chrome.get(url);
		html = self.chrome.page_source;
		
		# VALIDATION
		if len(errorContain)>0:
			for error in errorContain:
				if error in html:
					# return error if html contain specified error content
					return 858, html, False
					
		if len(mustContain)>0:
			for must in mustContain:
				if must not in html:
					# return error if html not contain expected content
					return 808, html, False
		
		# get date
		today = date.today()
		year = today.strftime("%Y")
		fdate = today.strftime("%Y-%m-%d")
		
		# create folder year & date folder if not exist
		if not os.path.exists(self._ROOT_CACHE_FOLDER):
			os.makedirs(self._ROOT_CACHE_FOLDER)
		if not os.path.exists(self._ROOT_CACHE_FOLDER + "/" + year):
			os.makedirs(self._ROOT_CACHE_FOLDER + "/" + year)
		if not os.path.exists(self._ROOT_CACHE_FOLDER + "/" + year + "/" + fdate):
			os.makedirs(self._ROOT_CACHE_FOLDER + "/" + year + "/" + fdate)
			
		# get domain
		domain = urlparse(url).netloc
		
		# create domain folder if not exist
		if not os.path.exists(self._ROOT_CACHE_FOLDER + "/" + year + "/" + fdate + "/" + domain):
			os.makedirs(self._ROOT_CACHE_FOLDER + "/" + year + "/" + fdate + "/" + domain)
			
		# get md5 url as filename 
		h = hashlib.md5(bytes(url, 'utf-8'))
		filename = h.hexdigest() + ".html";
		
		# check if archive found
		archiveFilename = self._ROOT_CACHE_FOLDER + "/" + year + "/" + fdate + "/" + domain + "/" + filename;
		if os.path.exists(archiveFilename): 
			# if archive exist, need to check overwrite parameter to determine do or not
			if overwrite:
				with open(archiveFilename, "w") as outfile:
					outfile.write(html);		
		else:
			# if archive not exist, archive page source
			with open(archiveFilename, "w") as outfile:
				outfile.write(html);
					
		return 200, html, True
		
		
	def getSource(self, url, overwrite, mustContain=[], errorContain=[]):			
		loop = asyncio.get_event_loop()
		status, contentType, source, update = loop.run_until_complete(self.httpGetSource(url, overwrite, mustContain, errorContain))
		if status==858:
			# retry by chrome
			status, source, update = loop.run_until_complete(self.chromeGetSource(url, overwrite, mustContain, errorContain))
			if status==858:
				# retry again by chrome
				status, source, update = loop.run_until_complete(self.chromeGetSource(url, overwrite, mustContain, errorContain))
				if status==858:
					# Still get javascript error
					return 858, source
			
			if status==808:
				return status, source
			else:
				return 200, source;
		elif status==808:
			return 808, source
		else:
			return 200, source
			
			
	def getCachedSource(self, url, mustContain, errorContain, fdate):
		# get date
		tday = fdate
		theDate = None;
		if fdate != None:
			theDate = datetime.strptime(fdate, "%Y-%m-%d")
		else:
			tday = time.strftime("%Y-%m-%d")
			theDate = datetime.strptime(tday, '%Y-%m-%d');
		
		year = theDate.strftime("%Y")
		
		# create folder year & date folder if not exist
		if not os.path.exists(self._ROOT_CACHE_FOLDER):
			os.makedirs(self._ROOT_CACHE_FOLDER)
		if not os.path.exists(self._ROOT_CACHE_FOLDER + "/" + year):
			os.makedirs(self._ROOT_CACHE_FOLDER + "/" + year)
		if not os.path.exists(self._ROOT_CACHE_FOLDER + "/" + year + "/" + tday):
			os.makedirs(self._ROOT_CACHE_FOLDER + "/" + year + "/" + tday)
			
		# get domain
		domain = urlparse(url).netloc
		
		# create domain folder if not exist
		if not os.path.exists(self._ROOT_CACHE_FOLDER + "/" + year + "/" + tday + "/" + domain):
			os.makedirs(self._ROOT_CACHE_FOLDER + "/" + year + "/" + tday + "/" + domain)
			
		# get md5 url as filename 
		h = hashlib.md5(bytes(url, 'utf-8'))
		filename = h.hexdigest() + ".html";
		
		archiveFilename = self._ROOT_CACHE_FOLDER + "/" + year + "/" + tday + "/" + domain + "/" + filename;
		if os.path.exists(archiveFilename): 
			# read source
			file = open(archiveFilename)
			html = file.read()
			file.close()
			
			return 200, html
		else:
			return self.getSource(url, False, mustContain, errorContain)
			
			
	def closeBrowser(self):
		if self.chrome != None:
			self.chrome.close()

