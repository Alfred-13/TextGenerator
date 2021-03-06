import os, sys
import TitleExtractor as TE

try:
	os.remove('main.log')
	fp = open('main.log', 'w+')
except:
	fp = open('main.log', 'w+')


def download_ieee(name):
	import IEEE.PaperDownloader as PD
	te = TE.TitleExtractor('127.0.0.1', \
	'root', 'dcc', 'cs_papers', 'titles')
	lst = te.get_titles_by_name(name)
	for t in lst:
		pd = PD.PaperDownloader(t[:-1])
		pd.download_pdf()
	return None

def download_acm(name):
	import ACM.PaperDownloader as PD
	te = TE.TitleExtractor('127.0.0.1', \
	'root', 'dcc', 'cs_papers', 'titles')
	lst = te.get_titles_by_name(name)
	for t in lst:
		pd = PD.PaperDownloader(t[:-1])
		pd.download_pdf()
	return None

def download_springer(name):
	import Springer.PaperDownloader as PD
	te = TE.TitleExtractor('127.0.0.1', \
	'root', 'dcc', 'cs_papers', 'titles')
	lst = te.get_titles_by_name(name)
	for t in lst:
		pd = PD.PaperDownloader(t[:-1])
		pd.download_pdf()
	return None

def download_elsevier(name):
	import Elsevier.PaperDownloader as PD
	te = TE.TitleExtractor('127.0.0.1', \
	'root', 'dcc', 'cs_papers', 'titles')
	lst = te.get_titles_by_name(name)
	for t in lst:
		pd = PD.PaperDownloader(t[:-1])
		pd.download_pdf()
	return None

def download(name, press):
	if press == 'IEEE':
		download_ieee(name)
	elif press == 'ACM':
		download_acm(name)
	elif press == 'Springer':
		download_springer(name)
	elif press == 'Elsevier':
		download_elsevier(name)
	else:
		print '[-] Unknown press name.'
		return None
	return name, press

def move_to_archive(name, press):
	os.system('mkdir %s' %(name))
	cwd_lst = os.listdir(os.getcwd())
	for f in cwd_lst:
		if f[-4:] == '.pdf':
			os.system('cp %s %s' %(f, name))
		else:
			pass
	os.system('cp -r %s ../PDFArchive/%s' %(name, press))
	print '[+] Move to archive: done.'
	return None

def build_all():
	name  = raw_input('Extract titles by name: ')
	press = raw_input('Download papaers by press: ')
	try:
		download(name, press)
		#move_to_archive(name, press)
		print '[+] Build all: done.'
	except:
		print '[-] Build all: failed.'
	return None

if __name__ == '__main__':
    build_all()