import MySQLdb

class TitleExtractor(object):
	""" extract certain titles from MySQLdb """
	
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
		# in r[i], i is flexible to locate the title column
		titles_list = [r[3] for r in records]
		return titles_list