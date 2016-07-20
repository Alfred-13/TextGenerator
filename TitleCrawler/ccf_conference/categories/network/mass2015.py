
# -*- coding: utf-8 -*-
import re
import copy
import random
import os, sys
import MySQLdb
import requests
from time import sleep
from threading import Thread
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')


clade = 'http://dblp.uni-trier.de/db/conf/mass/index.html'


months = {
	'January':   '01',
	'February':  '02',
	'March':     '03',
	'April':     '04',
	'May':       '05',
	'June':      '06',
	'July':      '07',
	'August':    '08',
	'September': '09',
	'October':   '10',
	'November':  '11',
	'December':  '12'
}


# regex to match months in <h2> tags
re_mons=r'(January|February|March|April|May|June|July|August|September|October|November|December)'
repeato_mons=r'([ /-]*'+re_mons+r'*)*'
pattern_mons=re_mons+repeato_mons

# regex to match years in <h2> tags
re_year=r'((19|20)\d+)'
repeato_year=r'([ /-]*'+re_year+r'*)*'
pattern_year=re_year+repeato_year


def get_leaves(clade):
	r = requests.get(clade)
	if r.status_code == 200:
		soup = BeautifulSoup(r.text, 'lxml')
	leaves = []
	late = soup.find('ul', class_='publ-list')
	tags = late.find_all('div', class_='data', itemprop='headline')
	for tag in tags:
		leaves.append(tag.find_all('a')[-1]['href'])
	return leaves


def sub_months(match_obj):
	""" transfer months to digital form (in-place change)
	"""
	for m in months:
		match_obj = re.sub(m, months[m], match_obj)
	return match_obj


def get_yymm(leaf):
	r = requests.get(leaf)
	if r.status_code == 200:
		soup = BeautifulSoup(r.text, 'lxml')
	lat = soup.find('div', class_='data', itemprop='headline')
	tag = lat.find('span', class_='title', itemprop='name')
	txt = tag.get_text()
	try:
		match_obj_mons = re.search(pattern_mons, txt)
		match_obj_mons = match_obj_mons.group().strip()
		match_obj_mons = sub_months(match_obj_mons)
		month = match_obj_mons
	except Exception, error_mons:
		print '[-]', error_mons
		month = None
	try:
		match_obj_year = re.search(pattern_year, txt)
		match_obj_year = match_obj_year.group().strip()
		year = match_obj_year
	except Exception, error_year:
		print '[-]', error_year
		year = None
	return year, month


def get_titles(leaf):
	r = requests.get(leaf)
	if r.status_code == 200:
		soup = BeautifulSoup(r.text, 'lxml')
	title_lst = []
	tags = soup.find_all('span', class_='title', itemprop='name')
	for tag in tags:
		title_lst.append(tag.get_text())
	return title_lst


def incert_mysql(year, month, title_lst):
	try:
		tablename = 'papertitle'
		conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='13917331612', db='conference')
		c = conn.cursor()
		conn.set_character_set('utf8')
		c.execute('SET NAMES utf8;')
		c.execute('SET CHARACTER SET utf8;')
		c.execute('SET character_set_connection=utf8;')
		for p in title_lst:
			try:
				sql = "insert into " + tablename + "(year, month, name, title, class, category) \
					values(%s, %s, %s, %s, %s, %s)"
				param = (year, month, 'MASS', p, 'C', 'network')
				c.execute(sql, param)
				print ">>>> [+] Insert paper <%s> : done." %(p)
			except MySQLdb.Error, e:
				print "[-] Mysql Error %d: %s" % (e.args[0], e.args[1])
				continue
		conn.commit()
		c.close()
	except MySQLdb.Error, e:
		print "[-] Mysql Error %d: %s" % (e.args[0], e.args[1])
	return None


def build():
	leaves = get_leaves(clade)
	for leaf in leaves:
		title_lst = get_titles(leaf)
		year, month = get_yymm(leaf)
		incert_mysql(year, month, title_lst)
	return None

build()