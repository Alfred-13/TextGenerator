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
	http://www.sciencedirect.com/ (find the first one)"""

	def __init__(self, title):
		self.title   = title
		self.driver  = webdriver.PhantomJS('/home/rumia/WebDrivers/PhantomJS/phantomjs')
		#self.driver  = webdriver.Chrome('/home/rumia/WebDrivers/Chrome/chromedriver')
		self.rootpg  = 'http://www.sciencedirect.com/' 
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
			(KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
		}

	def __get_search_result_url(self):
		print '[*] Searching for paper <%s>' %(self.title)
		self.driver.get(self.rootpg)
		sleep(3)
		try:
			element = self.driver.find_element_by_id('search-input')
			element.send_keys(self.title)
			element.submit()
			search_url = copy.copy(self.driver.current_url)
			self.driver.quit()
			print '[+] Find search result page ==> %s' %(search_url)
			return search_url
		except Exception, error:
			print '[-]', error
			return None

	def get_pdf_url(self):
		search_url = self.__get_search_result_url()
		if search_url != None:
			r = requests.get(search_url, headers=self.headers)
		else:
			print '[-] Failed to get PDF url <%s>' %(self.title)
			return None
		if r.status_code == 200:
			soup = BeautifulSoup(r.content, 'lxml')
		tag = soup.find('a', href=re.compile(r'http://.*\.pdf'))
		try:
			print '[+] Get PDF url for <%s>' %(self.title)
			return tag['href']
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


#PD = PaperDownloader('Combing CCN with network coding: An architectural perspective')
#PD.download_pdf()