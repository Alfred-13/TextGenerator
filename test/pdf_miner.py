import os, sys
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator


def pdf_to_txt(in_file):
	""" turn a PDF file to a TXT file (roughly processed)
	"""
	# Open a PDF file.
	fp = open(in_file, 'rb')
	# Create a PDF parser object associated with the file object.
	parser = PDFParser(fp)
	# Create a PDF document object that stores the document structure.
	document = PDFDocument(parser)
	# Check if the document allows text extraction. If not, abort.
	if not document.is_extractable:
		raise PDFTextExtractionNotAllowed
	# Set parameters for analysis.
	laparams = LAParams()
	# Create a PDF resource manager object that stores shared resources.
	rsrcmgr = PDFResourceManager()
	# Create a PDF page aggregator object.
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)
	# Create a PDF interpreter object.
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	for page in PDFPage.create_pages(document):
		interpreter.process_page(page)
		# Receive the LTPage object for the page.
		layout = device.get_result()
		for klass in layout:
			if isinstance(klass, LTTextBoxHorizontal):
				out_file = in_file[:-3] + 'txt'
				with open(out_file, 'a') as dst_file:
					text = klass.get_text().encode('utf-8')
					dst_file.write(text + '\n')
	return None

def get_all_pdfs():
	""" return a list containing all PDF filenames in current directory
	"""
	pdf_lst = []
	# Get all files (including directories) in current directory
	src_lst = os.listdir(os.getcwd())
	# Select PDF files
	for fn in src_lst:
		if (not os.path.isdir(fn)) and fn.endswith('.pdf'):
			pdf_lst.append(fn)
	return pdf_lst

def build_all():
	""" turn all PDF files in current directory to TXT files
	"""
	pdf_lst = get_all_pdfs()
	for fn in pdf_lst:
		pdf_to_txt(fn)
	return None

build_all()