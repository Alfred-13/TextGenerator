import re
import copy
import os,sys
import requests
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common import keys


class PaperDownloader(object):
	""" Download the exact paper given the title on 
	http://ieeexplore.ieee.org/ (find the first one)"""

	def __init__(self, title):
		self.title  = title
		self.driver = webdriver.PhantomJS('/home/rumia/WebDrivers/PhantomJS/phantomjs')
		self.search = 'http://ieeexplore.ieee.org/search/searchresult.jsp?&queryText=' + title
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
			(KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
		}

	def __get_download_page(self):
		print '[*] Searching for paper <%s>' %(self.title)
		self.driver.get(self.search)
		sleep(3)
		try:
			element = self.driver.find_element_by_class_name('icon-pdf')
			element.click()
			download_page = copy.copy(self.driver.current_url)
			print '[+] Find download page ==> %s' %(download_page)
			self.driver.quit()
			return download_page
		except Exception, error:
			print '[-]', error
			self.driver.quit()
			return None

	def get_pdf_url(self):
		download_page = self.__get_download_page()
		if download_page != None:
			r = requests.get(download_page, headers=self.headers)
		else:
			print '[-] Failed to get PDF url <%s>' %(self.title)
			return None
		if r.status_code == 200:
			soup = BeautifulSoup(r.content, 'lxml')
		tag = soup.find('frame', src=re.compile(r'http://.*'))
		try:
			print '[+] Get PDF url for <%s>' %(self.title)
			return tag['src']
		except Exception, error:
			print '[-]', error
			return None

	def download_pdf(self):
		filename = self.title.replace('/', '\\') + '.pdf'
		if filename in os.listdir(os.getcwd()):
			print '[-] File already exists <%s>' %(filename)
			return None
		pdf_url = self.get_pdf_url()
		if pdf_url != None:
			r = requests.get(pdf_url, headers=self.headers, stream=True)
		else:
			print '[-] Failed to download <%s>\n' %(self.title)
			return None
		if r.status_code == 200:
			soup = BeautifulSoup(r.content, 'lxml')
		with open (filename, 'wb') as dst_file:
			for chunk in r.iter_content(chunk_size=1024):
				if chunk:
					dst_file.write(chunk)
					dst_file.flush()
		print '[+] Downloaded <%s>\n' %(self.title)
		return filename

#PD = PaperDownloader('networks')
#PD.download_pdf()