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
isjournal = 'Y'

def get_titles(url, conference):
    header = list()
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        for i in soup.find_all('header'):
            try:
                x = i.find('h2').text
                if isinstance(x, unicode):
                    x = x.encode()
                    header.append(x)
            except:pass
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
            try:
                date_info = header[index].split(',')[2].strip()
                if ( '-' not in date_info ):
                    month = month_trans(date_info.split()[0])
                    year = date_info.split()[1]
                else:
                    info = date_info.split()
                    if info[1] == '-':
                        month = month_trans(info[0])
                        year = info[3]
                    else:
                        month = month_trans(info[0].split('-')[0])
                        year = info[1]
                insert_mysql(int(year), int(month), conference, title_list, paper_class[2], category, isjournal)
            except:
                pass
            index += 1

def insert_mysql(year,month,conf_name,papers,paper_class,category,isjournal):
    try:
        tablename='papertitle'
        conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd = "13917331612", db ="conference")
        c = conn.cursor()
        conn.set_character_set('utf8')
        c.execute('SET NAMES utf8;')
        c.execute('SET CHARACTER SET utf8;')
        c.execute('SET character_set_connection=utf8;')
        print "insert..."
        for p in papers:
            sql = "insert into "+ tablename +"(year, month, name, title, class, category, isjournal)  values(%s,%s,%s,%s,%s,%s,%s)"
            param = (year, month, conf_name, p, paper_class, category, isjournal)
            try:
                c.execute(sql,param)
                print 'execute...'
            except:
                pass
        conn.commit()
        print "commit..."
        c.close()
    except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

def month_trans(month):
    table = {
        'January'  : '01',
        'February' : '02',
        'March'    : '03',
        'April'    : '04',
        'May'      : '05',
        'June'     : '06',
        'July'     : '07',
        'August'   : '08',
        'September': '09',
        'October'  : '10',
        'November' : '11',
        'December' : '12'
    }
    return table.get(month)
match = {
    'CL':45,
    'IJSEKE':26,
    'STTT':18,
    'JWE':15,
    'SOCA':10,
    'SQJ':24,
    'TPLP':16
}

def main():
    items = match.items()
    print items
    for k, v in items:
        print k
        journal = k.lower()
        for i in range(v):
            ServiceUrl = 'http://dblp.uni-trier.de/db/journals/{journal}/{journal}{volume}.html'
            num = str(i+1)
            Url = ServiceUrl.format(journal=journal, volume=num)
            print Url
            print '{num}'.format(num=i+1)
            get_titles(Url, k)

if __name__ == '__main__':
    main()