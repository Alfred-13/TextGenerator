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
#requests.adapters.DEFAULT_RETRIES = 5 

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


root_system = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903028135780'
root_network = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903028135856'
root_security = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903940690850'
root_softeng = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903028135775'
root_database = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903940690081'
root_theory = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903940690325'
root_multimedia = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903940690854'
root_AI = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903940690839'
root_HCI = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903940690320'
root_MISC = 'http://www.ccf.org.cn/sites/ccf/biaodan.jsp?contentId=2903940690316'

root = {
	'system': root_system,
	'network': root_network,
	'security': root_security,
	'softeng': root_softeng,
	'database': root_database,
	'theory': root_theory,
	'multimedia': root_multimedia,
	'AI': root_AI,
	'HCI': root_HCI,
	'MISC': root_MISC 
}

# regex to match months in <h2> tags
re_mons=r'(January|February|March|April|May|June|July|August|September|October|November|December)'
repeato_mons=r'([ /-]*'+re_mons+r'*)*'
pattern_mons=re_mons+repeato_mons

# regex to match years in <h2> tags
re_year=r'((19|20)\d+)'
repeato_year=r'([ /-]*'+re_year+r'*)*'
pattern_year=re_year+repeato_year

# open a log file for potential errors
#try:
#	os.remove('error.log')
#	ferror = open('error.log', 'w+')
#except:
#	ferror = open('error.log', 'w+')


def get_titles_journal(rec, tag):
	""" get titles with single <h2> tag and a record (in-place change)
	"""
	p = tag.parent.next_sibling.next_sibling
	while p.name == 'ul':
		for title in p.find_all('span', class_='title', itemprop='name'):
			rec['titles'].append(title.get_text())
		p = p.next_sibling.next_sibling
	print 'and hit %d titles for leaf : %s' %(len(rec['titles']), rec['leaf']) 
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
	print '>>>> [+] Add yymm <%s> <%s>' %(rec['year'], rec['month']),
	return None


def get_leaf_urls_journal(clade):
	""" return a list containing all leaf-urls in one clade page (journal)
	"""
	leaves = [] # list to store leaf-urls
	try:
		r = requests.get(clade, timeout=1)
		if r.status_code == 200:
			soup = BeautifulSoup(r.content, 'lxml')
		# using selector to locate the leaf-urls
		#tags = soup.select('#main > ul > li:nth-child > a')
		# select the latest papers
		tags = soup.select('#main > ul > li:nth-child')[0].find_all('a')
		for tag in tags:
			leaves.append(tag['href'])
		return leaves
		#return tags
	except Exception, error:
		#ferror.write(error)
		#ferror.write('\n')
		print '!!!! [-]', error,
		return None


# category = network, database, HCI, and etc.
def build_root_journal(root, category):
	""" return a list containing all journal's basic records (including 
	clade urls) in the root page, given the category of the root.
	"""
	r = requests.get(root)
	if r.status_code == 200:
		soup = BeautifulSoup(r.content, 'lxml')
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
			print '>>>> [+] Add clade url : %s' %(rec['clade'])
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
		try:
			leaves = get_leaf_urls_journal(rec['clade'])
			for leaf in leaves:
				rec['leaf'] = leaf
				rec_lst_clades.append(copy.deepcopy(rec))
				print '>>>> [+] Add leaf url : %s' %(leaf)
		except Exception, error:
			print '===> Error clade : %s' %(rec['clade'])
			continue
	print '[+] Build <%s> clades <journal> : done.' %(rec['category'])
	return rec_lst_clades

def build_leaves_journal(rec_lst_clades):
	""" get month and titles for each record in rec_lst_clades
	"""
	# get year, month and titles
	#rec_lst_leaves = []
	for rec in rec_lst_clades:
		# diffrent leaves for each record in rec_lst_clades
		try:
			r = requests.get(rec['leaf'], timeout=1)
			if r.status_code == 200:
				soup = BeautifulSoup(r.content, 'lxml')
			tags = soup.find_all('h2')
			for tag in tags:
				get_yymm_journal(rec, tag)
				get_titles_journal(rec, tag)
				incert_mysql(rec)
				#rec_lst_leaves.append(copy.deepcopy(rec))
				rec['titles'] = [] # initialize the titles list
		except Exception, error:
			#ferror.write(error)
			#ferror.write('\n')
			print '!!!! [-]', error,
			print '===> Error leaf : %s' %(rec['leaf'])
			continue
	print '[+] Build <%s> leaves <journal> : done.' %(rec['category'])
	# return rec_lst_leaves
	return None


def incert_mysql(rec):
	""" incert a record's full data into mysqldb
	"""
	try:
		tablename = 'titles'
		conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='dcc', db='cs_papers')
		c = conn.cursor()
		for p in rec['titles']:
			delete = "delete from " + tablename + ' where title = "%s"' %(p)
			incert = "insert into " + tablename + " (year, month, name, title, class, category) \
				values(%s, %s, %s, %s, %s, %s)"
			iparam = (rec['year'],rec['month'],rec['name'],p,rec['class'],rec['category'])
			# try to execute delete
			try:
				c.execute(delete)
				print '>>>> [+] Delete paper <%s> : done.' %(p)
			except MySQLdb.Error, de:
				#ferror.write("[-] Mysql Error %d : %s\n" % (de.args[0], de.args[1]))
				print "!!!! [-] Mysql Error %d : %s" % (de.args[0], de.args[1])
			# try to execute incert
			try:
				c.execute(incert, iparam)
				print ">>>> [+] Insert paper <%s> : done." %(p)
			except MySQLdb.Error, ie:
				#ferror.write("[-] Mysql Error %d : %s\n" % (ie.args[0], ie.args[1]))
				print "!!!! [-] Mysql Error %d : %s" % (ie.args[0], ie.args[1])
			# commit for each paper
			conn.commit()
		c.close()
	except MySQLdb.Error, e:
		#ferror.write("[-] Mysql Error %d : %s\n" % (e.args[0], e.args[1]))
		print "!!!! [-] Mysql Error %d : %s" % (e.args[0], e.args[1])
	return None

def build_all_category(category):
	""" build one category's journal part all 
	"""
	try:
		rec_lst_root = build_root_journal(root[category], category)
		rec_lst_clades = build_clades_journal(rec_lst_root)
		build_leaves_journal(rec_lst_clades)
		print '[+] Build category <%s> : done.' %(category)
	except Exception, error:
		print '[-] Error when building category <%s>. Program killed.' %(category),
		print error
	return None


def build_all():
	""" build all categories' journal part all
	"""
	build_all_category('system')
	build_all_category('network')
	build_all_category('security')
	build_all_category('softeng')
	build_all_category('database')
	build_all_category('theory')
	build_all_category('multimedia')
	build_all_category('AI')
	build_all_category('HCI')
	build_all_category('MISC')
	#ferror.close()
	print '[*] All finished.' 
	return None

#build_all()