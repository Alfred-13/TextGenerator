import requests
from bs4 import BeautifulSoup
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# year, month, conf_name, papers, paper_class, category
paper_class = ['A', 'B', 'C']
# 'system', 'softeng', 'network', 'security', 'database', 'theory', 'multimedia', 'AI', 'HCI', 'MISC'
category = 'softeng'

def get_titles(url, year):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        '''
        print soup.prettify()
        for i in soup.find_all('header'):
            try:
                x = i.find('h2').text
                if isinstance(x, unicode):
                    x = x.encode()
                    header.append(x)
            except:
                pass
                '''
        ul = soup.find_all('ul', class_='publ-list',)
        index = 0
        for j in ul:
            title_list = list()
            try:
                titles = j.find_all('span', class_='title', itemprop='name')
                if titles is not None:
                    for title in titles:
                        x = title.text
                        if isinstance(x, unicode):
                            x = x.encode()
                            title_list.append(x)
            except:
                pass
            print index
            index += 1
            if index == 1:
                continue
            try:
                if year % 2 == 0:
                    month = 9
                else:
                    month = 11
                insert_mysql(year, 10, 'OOPSLA', title_list, paper_class[0], category)
            except:
                pass
    else:
        print 'fail...'

def insert_mysql(year,month,conf_name,papers,paper_class,category):
    try:
        tablename = 'papertitle'
        conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd = "13917331612", db ="conference")
        c = conn.cursor()
        conn.set_character_set('utf8')
        c.execute('SET NAMES utf8;')
        c.execute('SET CHARACTER SET utf8;')
        c.execute('SET character_set_connection=utf8;')
        print "insert..."
        for p in papers:
            sql = "insert into " + tablename + "(year, month, name, title, class, category)  values(%s,%s,%s,%s,%s,%s)"
            param = (year, month, conf_name, p, paper_class, category)
            try:
                c.execute(sql, param)
                print 'execute...'
            except:
                print 'execute' + ' ' + p + ' ' + 'failed'
        conn.commit()
        print "commit..."
        c.close()
    except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def main():
    num1 = [i+86 for i in range(14)]
    num2 = [i+2000 for i in range(16)]
    num = num1 + num2
    for i in num:
        ServiceUrl = 'http://dblp.uni-trier.de/db/conf/oopsla/oopsla{num}.html'
        Url = ServiceUrl.format(num=i)
        print Url
        if i < 1000:
            i += 1900
        print i
        get_titles(Url, i)

if __name__ == '__main__':
    main()