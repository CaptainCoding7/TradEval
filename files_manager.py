import csv
import pdftotext
import nltk
from nltk.tokenize import sent_tokenize

#export des score deans un fichier csv
'''@param
   @return 
'''
def export_to_csv(array):
	with open('scores.csv','w') as csvfile:
		writer = csv.writer(csvfile)
		for r in array:
			writer.writerow(r)
		csvfile.close()

#copie le text d'un pdf dqns un fichier .txt
'''@param String pdf_path, txt_file( chemin des fichiers)
   @ return void
'''
def convert_pdf_to_txt(pdf_path, txt_file):
# Load your PDF
	with open(pdf_path, "rb") as f:
		pdf = pdftotext.PDF(f)
	f.close()
	file = open(txt_file,"a") 
	print(pdf)
	for page in pdf:
		one_shot=page.replace("\n"," ")
		file.write(one_shot)
	file.close() 

#recupere le texte depuis un fichier txt ou pdf et retourne un string
#file_to_string?
def file_to_string(file_path):
    
	#cas 1: pdf file
	try :
		with open(file_path, "rb") as f:
			pdf = pdftotext.PDF(f)
		data=''
		for page in pdf:
			data+=page.replace("\n"," ")
		f.close()

	# cas2 : txt file
	except:
		with open(file_path, 'r') as file:
			data = file.read()
		file.close()
	#print(data)

	return data

#recupere le texte depuis un fichier txt ou pdf et retourne une liste de phrases

def file_to_listeSentence(file_path):
	sentences =[]

	#cas 1 : pdf file
	try :
		with open(file_path, "rb") as f:
			pdf = pdftotext.PDF(f)
		for page in pdf:
			#sentences.extend(sent_tokenize(page))
			lines = page.split("\n")
			for sentence in lines:
    				if sentence!='' :
    					sentences.append(sentence)
	# cas2: txt file				
	except:
		with open(file_path,"r") as text:
			line = text.readline()
		#data=file_to_string(file_path)
		#sentences.extend(sent_tokenize(data))
			while line!='':
				line1 = line.split("\n")
				for sentence in line1:
					if sentence!='' :
						sentences.append(sentence)
				line = text.readline()

	return sentences

