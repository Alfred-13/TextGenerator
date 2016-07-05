# -*- coding: utf-8 -*-
import re
import os
import time
import requests
import MySQLdb
from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def get_titles(url):
    response = requests.get(url)
    if response.status_code == 200:
        html = BeautifulSoup(response.content,'lxml')
    title_list=[]
    for i in html.find_all('tr',class_='lead'):
        x=i.find('strong').text
        if isinstance(x, unicode):
            x=x.encode()
        title_list.append(x)
    insert_mysql('2016','05','AsiaCCS',title_list)
    
def insert_mysql(year, month, conf_name, papers):
    try:
        tablename='papertitle'
        conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="13917331612", db="conference")
        c = conn.cursor()
        for p in papers:
            sql = "insert into "+tablename+"(year,month,name,title)  values(%s,%s,%s,%s)"
            param=(year,month,conf_name,p)
            c.execute(sql,param)
            print "insert..."
        conn.commit()
        c.close()
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def main():
    get_titles("http://meeting.xidian.edu.cn/conference/AsiaCCS2016/papers.html")

if __name__ == '__main__':
    main()