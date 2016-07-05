# -*- coding: utf-8 -*-
import re
import copy
import time # time.sleep
import random
import os, sys
import MySQLdb
import requests
import threading
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

requests.adapters.DEFAULT_RETRIES = 5 

# pattern to store unit data
record = {
	'clade':    None,
	'leaf':     None,
	'year':     None,
	'month':    None,
	'name':     None,
	'titles':   [],
	'class':    None, # A, B, C
	'category': None # network, database, HCI, and etc. (self)
}

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

classes = {1:'A', 2:'B', 3:'C'}


root_network = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903028135856'
root_database = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903940690081'
root_HCI = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903940690320'

root = {
	'network': root_network,
	'database': root_database,
	'HCI': root_HCI 
}

# regex to match months in <h2> tags
re_mons=r'(January|February|March|April|May|June|July|August|September|October|November|December)'
repeato_mons=r'([ /-]*'+re_mons+r'*)*'
pattern_mons=re_mons+repeato_mons

# regex to match years in <h2> tags
re_year=r'((19|20)\d+)'
repeato_year=r'([ /-]*'+re_year+r'*)*'
pattern_year=re_year+repeato_year


def get_titles_journal(rec, tag):
	""" get titles with single <h2> tag and a record (in-place change)
	"""
	p = tag.parent.next_sibling.next_sibling
	while p.name == 'ul':
		for title in p.find_all('span', class_='title', itemprop='name'):
			rec['titles'].append(title.get_text())
		p = p.next_sibling.next_sibling
	print '---> [+] Get %d titles for leaf : %s' %(len(rec['titles']), rec['leaf']) 
	return None


def sub_months(match_obj):
	""" transfer months to digital form (in-place change)
	"""
	for m in months:
		match_obj = re.sub(m, months[m], match_obj)
	return match_obj


def get_yymm_journal(rec, tag):
	""" get years and months with single <h2> tag and a record (in-place change)
	"""
	txt = tag.get_text()
	# get year first
	try:
		match_obj_year = re.search(pattern_year, txt)
		match_obj_year = match_obj_year.group().strip()
		rec['year'] = match_obj_year
	except:
		rec['year'] = None
	# then get months
	try:
		match_obj_mons = re.search(pattern_mons, txt)
		match_obj_mons = match_obj_mons.group().strip()
		match_obj_mons = sub_months(match_obj_mons)
		rec['month'] = match_obj_mons
	except:
		rec['month'] = None
	print '---> [+] Add year <%s> month <%s> to leaf : %s' %(y, rec['month'], rec['leaf'])
	return None


def get_leaf_urls_journal(clade):
	""" return a list containing all leaf-urls in one clade page (journal)
	"""
	r = requests.get(clade)
	if r.status_code == 200:
		soup = BeautifulSoup(r.text, 'lxml')
	leaves = [] # list to store leaf-urls
	# using selector to locate the leaf-urls
	tags = soup.select('#main > ul > li:nth-child > a')
	for tag in tags:
		leaves.append(tag['href'])
	return leaves


# category = network, database, HCI, and etc.
def build_root_journal(root, category):
	""" return a list containing all journal's basic records (including 
	clade urls) in the root page, given the category of the root.
	"""
	r = requests.get(root)
	if r.status_code == 200:
		soup = BeautifulSoup(r.text, 'lxml')
	rec = copy.deepcopy(record)
	rec_lst_j = [] # store records for each journal's url in root page
	rec['category'] = category
	tables = soup.find_all('table', class_='tjb') # 6 tables
	tables_j = tables[:3] # journal —— the first 3
	for i in range(len(tables_j)):
		rec['class'] = classes[i+1]
		tags_u = tables_j[i].find_all('a') # url tags
		tags_n = tables_j[i].find_all('td')[6::5] # name tags
		tags_a = tables_j[i].find_all('td')[7::5] # full name tags
		tags_u = [tag for tag in tags_u if tag.get_text().startswith('http://')]
		#print len(tags_u), len(tags_n), len(tags_a)
		for j in range(len(tags_u)):
			rec['clade'] = tags_u[j]['href']
			if tags_n[j].get_text() != u'\xa0':
				rec['name'] = tags_n[j].get_text().strip()
			else:
				rec['name'] = tags_a[j].get_text().strip()
			rec_lst_j.append(copy.deepcopy(rec))
			print '---> [+] Add clade url : %s' %(rec['clade'])
	print '[+] Build <%s> root <journal> : done.' %(category)
 	# return the result in a list
 	return rec_lst_j


def build_clades_journal(rec_lst_j):
	""" return a list containing all journal's basic records (including 
	leaf urls) in the root page, given the category of the root.
	"""
	rec_lst_clades = []
	# one rec_lst_j share the same <category>
	for rec in rec_lst_j:
		leaves = get_leaf_urls_journal(rec['clade'])
		for leaf in leaves:
			rec['leaf'] = leaf
			rec_lst_clades.append(copy.deepcopy(rec))
			print '---> [+] Add leaf url : %s' %(leaf)
	print '[+] Build <%s> clades <journal> : done.' %(rec['category'])
	return rec_lst_clades

def build_leaves_journal(rec_lst_clades):
	""" get month and titles for each record in rec_lst_clades
	"""
	# get year, month and titles
	rec_lst_leaves = []
	for rec in rec_lst_clades:
		# diffrent leaves for each record in rec_lst_clades
		r = requests.get(rec['leaf'])
		if r.status_code == 200:
			soup = BeautifulSoup(r.text, 'lxml')
		tags = soup.find_all('h2')
		for tag in tags:
			get_yymm_journal(rec, tag)
			get_titles_journal(rec, tag)
			rec_lst_leaves.append(copy.deepcopy(rec))
			rec['titles'] = [] # initialize the titles list
	# then incert each record in rec_lst_leaves into mysqldb
	#for rec in rec_lst_leaves:
	#	incert_mysql(rec)
	print '[+] Build <%s> leaves <journal> : done.' %(rec['category'])
	return rec_lst_leaves


def incert_mysql(rec):
	""" incert a record's full data into mysqldb
	"""
	try:
		tablename = 'papertitle'
		conn = MySQLdb.connect(host = "127.0.0.1", user = "root", \
			passwd = "xxxxxx", db = "conference")
		c = conn.cursor()
		for p in rec['titles']:
			sql = "insert into " + tablename + \
				"(year, month, name, title, class, category)  values(%s, %s, %s, %s, %s, %s)"
			param = (rec['year'], rec['month'], rec['name'], p, rec['class'], rec['category'])
			c.execute(sql, param)
			print "---> [+] Insert paper <%s> : done." %(p)
		conn.commit()
		c.close()
	except MySQLdb.Error, e:
		print "[-] Mysql Error %d: %s" % (e.args[0], e.args[1])
	return None

def build_all_category(category):
	""" build one category's journal part all 
	"""
	try:
		rec_lst_root = build_root_journal(root[category], category)
		rec_lst_clades = build_clades_journal(rec_lst_root)
		build_leaves_journal(rec_lst_clades)
		print '[+] Build category <%s> : done.'
	except:
		print '[-] Error when building category <%s>. Program killed.' %(category)
	return None

def build_all():
	""" build all categories' journal part all
	"""
	build_all_category('network')
	build_all_category('database')
	build_all_category('HCI')
	print '[+] Build all : done.'
	return None

build_all()
#build_root_journal(root_network, 'network')
#trec = copy.deepcopy(record)
#trec['leaf'] = 'http://dblp.uni-trier.de/db/journals/jnca/jnca32.html'
#get_year_journal(trec)

#rec_lst_root_j = build_root_journal(root_database, 'database')
#rec_lst_clades_j = build_clades_journal(rec_lst_root_j[13:14])
#rec_lst_leaves_j = build_leaves_journal(rec_lst_clades_j[-1:])
#for i in rec_lst_leaves_j:
#	print i


#l = get_leaf_urls_journal('http://dblp.uni-trier.de/db/journals/jasis/')
#for i in range(len(l)):
#	print i+1, l[i]