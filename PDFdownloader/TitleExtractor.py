import MySQLdb

class TitleExtractor(object):
	""" extract certain titles from MySQLdb
	"""
	def __init__(self, hostname, username, password, database, table):
		self.hostname = hostname
		self.username = username
		self.password = password
		self.database = database
		self.table = table

	def get_titles_by_name(self, name):
		try:
			conn = MySQLdb.connect(self.hostname, self.username, self.password, self.database)
			c = conn.cursor()
			c.execute("select * from %s where name = '%s';" %(self.table, name))
			records = c.fetchall()
		except MySQLdb.Error, error:
			print '[-]', error
			return None
		titles_list = [r[4] for r in records]
		return titles_list

	def get_titles_by_express(self, press):
		try:
			conn = MySQLdb.connect(self.hostname, self.username, self.password, self.database)
			c = conn.cursor()
			c.execute("select * from %s where press = '%s';" %(self.table, press))
			records = c.fetchall()
		except MySQLdb.Error, error:
			print '[-]', error
			return None
		# in r[i], i is flexible for title column
		titles_list = [r[4] for r in records]
		return titles_list