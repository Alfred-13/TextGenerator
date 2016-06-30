import requests
from urllib2 import *
from bs4 import BeautifulSoup

# program
url1 = 'http://www.ieee-security.org/TC/SP2016/program.html'
# program-papers
url2 = 'http://www.ieee-security.org/TC/SP2016/program-papers.html'
# program-posters (pdfs in this url)
url3 = 'http://www.ieee-security.org/TC/SP2016/program-posters.html'


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

def get_intros(url):
    """ return a dict containing all intros in one page
    """
    intr = dict()
    html = urlopen(url)
    # using lxml parser
    soup = BeautifulSoup(html, 'lxml')
    tags = soup.find_all('div', style='margin-left: 1.5em')
    for i in range(len(tags)):
        intr[i+1] = tags[i].contents[0].strip()
    return intr

#intros = get_intros(url)
#print intros

def download_pdf(url):  
    """ download the pdf to local given the exact url
    """
    file_name = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(file_name, 'wb') as dst_file:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                dst_file.write(chunk)
                dst_file.flush()
    return file_name


def download_all(root_url):
    """ download all pdfs to local given the root_url
    """
    r = requests.get(root_url)
    if r.status_code != 200:
        return "Bad root url!"
    soup = BeautifulSoup(r.text, 'lxml')
    tags = soup.find_all('b')
    # root_url is 'http://www.ieee-security.org/TC/SP2016/program-posters.html'
    # home page is 'http://www.ieee-security.org/TC/SP2016/'
    home = root_url[:-20] 
    for i in range(len(tags)):
        new_url = home + tags[i].contents[1]['href']
        if new_url.endswith('.pdf'):
            file_path = download_pdf(new_url)
            print 'Downloading: ' + new_url + ' -> ' + file_path
    print 'All downloading complete!'
    return None

#download_all(url3)
