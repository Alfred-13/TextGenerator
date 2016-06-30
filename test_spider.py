from urllib2 import *
from bs4 import BeautifulSoup

url = 'http://www.ieee-security.org/TC/SP2016/program.html'

def get_titles(url):
    """ return a dict containing all titles in one page
    """
    titl = dict()
    html = urlopen(url)
    # using lxml parser
    soup = BeautifulSoup(html, 'lxml')
    tags = soup.find_all('b')
    for i in range(len(tags)):
        titl[i+1] = tags[i].contents[0]
    return titl

#titles = get_titles(url)
#print titles