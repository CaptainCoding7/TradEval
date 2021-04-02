import pdftotext
#sudo apt install build-essential libpoppler-cpp-dev pkg-config python3-dev
#pip3 install pdftotext

def convert_pdf_to_txtFile(pdf_path, txt_file):
# Load your PDF
	with open(pdf_path, "rb") as f:
	    pdf = pdftotext.PDF(f)
	file = open(txt_file,"a") 
		

	for page in pdf:
	    print(page)
	    file.write(page)
	file.close() 
