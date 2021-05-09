import csv
import pdftotext
import nltk
from nltk.tokenize import sent_tokenize
from tkinter.ttk import Progressbar
from tkinter import HORIZONTAL
from tkinter import Label
from tkinter import Toplevel


#export des score deans un fichier csv
'''@param
   @return
'''
def export_to_csv(array, root):
	
		# fenetre de chargement
	popup_window = Toplevel()
	label = Label(popup_window, text = "Please wait during the scores calculus...")
	label.pack()
	p = Progressbar(popup_window,orient=HORIZONTAL,length=200,mode="determinate",takefocus=True,maximum=len(array))
	p.pack()
	x = root.winfo_screenwidth()/2
	y = root.winfo_screenheight()/2
	popup_window.geometry('+%d+%d' % (x, y))
	
	with open('scores.csv','w') as csvfile:
		writer = csv.writer(csvfile)
		for r in array:
			writer.writerow(r)
			p.step()
			root.update()
		csvfile.close()
	
	popup_window.destroy()

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
	#print(pdf)
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


def getSource(rows):
    source=[]
    for row in rows:
        source.append(row[0])
    return source

def getTarget(rows):
    target=[]
    for row in rows:
        target.append(row[1])
    return target

def get_Predictions(rows):
    predictions=[]

    col_num=[]
    for i in range(2,len(rows[0]),4):
        col_num.append(i)

    for row in rows:
        content=list(row[i] for i in col_num)
        predictions.append(content)

    return predictions


def openLearningCsv(f):

    rows=[]
    #f_in= open('datasets/adadelta_translation_copie.csv','r')
    f_in= open(f,'r')
    reader=csv.reader(f_in,delimiter=',')
    for row in reader:
        rows.append(row)

    predictions=get_Predictions(rows)
    source =  getSource(rows)
    target = getTarget(rows)

    #print(get_Predictions(rows)[1][0])
    #print(getSource(rows)[0])
    print(len(getTarget(rows)), " lignes")

    return (source,target,predictions)

def test():

    rows=[]
    f_in= open('datasets/adadelta_translation_copie.csv','r')
    reader=csv.reader(f_in,delimiter=',')
    for row in reader:
        rows.append(row)

    predictions=get_Predictions(rows)
    source =  getSource(rows)
    target = getTarget(rows)

    print(len(get_Predictions(rows)[1]))
    #print(getSource(rows)[0])
    #print(getTarget(rows)[0])

    return (source,target,predictions)


#test()
