import re
import os,sys
import requests
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common import keys


class PaperDownloader(object):
	""" Download the exact paper given the title on 
	http://dl.acm.org/ (find the first one)"""

	def __init__(self, title):
		self.title = title
		self.driver = webdriver.PhantomJS('/home/rumia/WebDrivers/PhantomJS/phantomjs')
		self.search = 'http://dl.acm.org/results.cfm?query=' + title
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
			(KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
		}

	def get_pdf_url(self):
		print '[*] Searching for paper <%s>' %(self.title)
		self.driver.get(self.search)
		sleep(3)
		try:
			# find the first PDF url in the result page
			element = self.driver.find_element_by_name('FullTextPDF')
			pdf_url = element.get_attribute('href')
			print '[+] Find download page ==> %s' %(pdf_url)
			print '[+] Get PDF url for <%s>' %(self.title)
			self.driver.quit()
			return pdf_url
		except Exception, error:
			print '[-]', error
			self.driver.quit()
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

#PD = PaperDownloader('What next, ubicomp?: celebrating an intellectual disappearing act')
#PD.download_pdf()