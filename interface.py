#!/usr/bin/env python
# -*- coding: utf-8 -*-



################ IMPORTATION DES MODULES ##################

from tkinter import*
from tkinter.filedialog import askopenfilename
import time
import numpy as np
from enum import Enum
import os

import re       # regex
from tkinter.ttk import Progressbar
from tkinter import ttk
import csv
import math
import fractions
from collections import Counter
from files_manager import *

# import des bibiotheques de calcul de scores
from bleu import file_bleu
from bleu import list_bleu
import sacrebleu
from nltk.util import ngrams
from nist import sentence_nist
from meteor import single_meteor_score
from meteor import PorterStemmer
# ntlk.download('wordnet')
from meteor import wordnet
from wer import *
import pyter
from algorithims import *
from match import *



############### root PRINCIPALE  ######################

# On crée une méthode qui va gérer le dimensionnement de la fenetre principale

class FullScreenApp(object):
    #On initialise la taille de la fenetre. En cas de clic sur Echap, on exécute la fonction toggle_geom.
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)

    # Cette fonction permet de redimensionner la fenetre.
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom



# Chargement fichier de ref

def loadRefFile():
    #root.withdraw()
    global refFile
    refFile=askopenfilename(initialdir = "/home/paul/Documents/proj_tansv/datasets",title = "Selectionner une traduction de reference",filetypes = (("txt files","*.txt"),("pdf files","*.pdf")))
    print(refFile+" loaded")
    textToShow=file_to_string(refFile)
    t1.delete('1.0',END)
    splittedText=textToShow.split('\n')
    i=1
    for s in splittedText:
        t1.insert(END, 'Phrase '+str(i)+' | '+s+'\n')
        i+=1

# Chargement fichier à évaluer

def loadHypFile():
    #root.withdraw()
    global hypFile
    hypFile=askopenfilename(initialdir = "/home/paul/Documents/proj_tansv/datasets",title = "Selectionner une traduction à évaluer",filetypes = (("txt files","*.txt"),("pdf files","*.pdf")))
    print(hypFile+" loaded")
    textToShow=file_to_string(hypFile)
    t2.delete('1.0',END)
    splittedText=textToShow.split('\n')
    i=1
    for s in splittedText:
        t2.insert(END, 'Phrase '+str(i)+' | '+s+'\n')
        i+=1

# Chargement fichier source

def loadSrcFile():
    srcFile=askopenfilename(initialdir = "/home/paul/Documents/proj_tansv/datasets",title = "Selectionner le texte source",filetypes = (("txt files","*.txt"),("pdf files","*.pdf")))
    print(srcFile+ " loaded")
    textToShow=file_to_string(srcFile)
    t3.delete('1.0',END)
    t3.insert(END, textToShow)
    splittedText=textToShow.split('\n')
    i=1
    for s in splittedText:
        t3.insert(END, 'Phrase '+str(i)+' | '+s+'\n')
        i+=1
    ####################################################################

#### FONCTION REALISANT LE CALCUL DES SCORES

def evaluate(scoresMatrice):

    print("evaluation en cours...\n")
    global refFile
    global hypFile
    global refSent
    global hypSent

    # fenetre de chargement
    popup_window = Toplevel()
    label = Label(popup_window, text = "Veuillez patienter pendant le calcul des scores...")
    label.pack()
    p = Progressbar(popup_window,orient=HORIZONTAL,length=200,mode="determinate",takefocus=True,maximum=len(refSent))
    p.pack()
    x = root.winfo_screenwidth()/2
    y = root.winfo_screenheight()/2
    popup_window.geometry('+%d+%d' % (x, y))


    # score bleu pour tout le fichier
    bleuScoreFile=file_bleu(refFile,hypFile)/100
    print("bleu total= ",bleuScoreFile)

    refSent = file_to_listeSentence(refFile)
    hypSent = file_to_listeSentence(hypFile)

    i=1
    str_score=''

    scoresMatrice.append(('Numéro de phrase','Phrase de référence', 'Phrase à évaluer','Score Bleu', 'Score Nist', 'Score Meteor'))

    for r,h in zip(refSent,hypSent):
        # decomposition au mot pour le calcul du score nist
        rw=r.split(" ")
        hw=h.split(" ")

        #bleu
        #sentScoreBleu=list_bleu([r], [h])
        b=sacrebleu.corpus_bleu([h], [[r]])
        bleu_splitted=str(b).split()
        sentScoreBleu=bleu_splitted[2]

        #nist
        nistScore= float("{:.2f}".format(sentence_nist([rw], hw)))

        #meteor
        meteorScore=float("{:.2f}".format(single_meteor_score(r, h, preprocess=str.lower, stemmer=PorterStemmer(), wordnet=wordnet, alpha=0.9, beta=3, gamma=0.5)))

        # wer
        wer = WER(rw, hw)
        distance, path, ref_mod, hyp_mod = wer.distance()
        werScore=100 * distance[len(rw)][len(hw)]/len(rw)
        
        #ter
        terScore='%.3f' % pyter.ter(hw, rw)


        ###### FUZZY MATCHING   /!\ SPLIT PAR GROUPES DE CARACTERES !!

        print("---- Fuzzy Matching: Phrase ",str(i))
        # bigrams
        print("     Evaluation par groupe de 2 mots: ", trigram(h,r,2))
        #trigrams
        print("     Evaluation par groupe de 3 mots: ", trigram(h,r))
        #4grams
        print("     Evaluation par groupe de 4 mots: ", trigram(h,r,4))
        #5-grams
        print("     Evaluation par groupe de 5 mots: ", trigram(h,r,5))

        #print(extractOne(h, [r]))


        # affichage et stockage des données dans la matrice des scores
        str_score+='--- Phrase n°'+str(i)+':    - Bleu = '+str(sentScoreBleu)+ '    - Nist = '+str(nistScore)+ '    - Meteor = '+str(nistScore)+ '    - Wer = '+'{:.0f}%'.format(werScore)+ '    - Ter = '+terScore+'\n'
        scoresMatrice.append((str(i),str(sentScoreBleu),str(nistScore), str(meteorScore),'{:.0f}%'.format(werScore)))

        i+=1
        p.step()
        root.update()

    #### fin de la boucle for


    popup_window.destroy()
    t4.delete('1.0',END)
    t4.insert(END, str_score)


##########################################################################""

def convert_pdf_to_txtFile(pdf_path, txt_file):
# Load your PDF
	with open(pdf_path, "rb") as f:
	    pdf = pdftotext.PDF(f)
	#file = open(txt_file,"a")


	for page in pdf:
	    print(page)
	 #   file.write(page)
	#file.close()


#######################################   MAIN ###############################
###############################################################################

##### variables globales

refFile=''
hypFile=''
refSent=[]
hypSent=[]
scoresMatrice=[]


### fenetre principale
root=Tk()
#app=FullScreenApp(root)
root.title("Evaluateur de traduction")


####################  MENU HAUT  ##############################

# Pour créer le menu supérieur, on crée des objets avec la classe Menu()

# On assigne à ces objets différentes méthodes.

menubar = Menu(root)

menu1 = Menu(menubar, tearoff=0)
menu1.add_command(label="Ouvrir")
menu1.add_command(label="Enregistrer")
menu1.add_separator()
menu1.add_command(label="Quitter")
menubar.add_cascade(label="Fichier", menu=menu1)

menu2 = Menu(menubar, tearoff=0)
menu2.add_command(label="A propos")
menubar.add_cascade(label="Aide", menu=menu2)

root.config(menu=menubar)
root['bg']="lightblue"


###################  FRAMES  ##########################


lf1 = LabelFrame(root, text="Charger fichiers (.txt, .pdf)", height=root.winfo_screenheight()*0.1,width=root.winfo_screenwidth(),bg="lightblue")
lf1.grid(row=0,sticky='nw',column=0,columnspan=3)
lf1.grid_propagate(False)


lf2 = LabelFrame(root, text="Traduction de référence",height=root.winfo_screenheight()*0.4,width=root.winfo_screenwidth()/3, bg="lightblue")
lf2.grid(column=1,row=1)
lf2.grid_propagate(False)

lf3 = LabelFrame(root, text="Traduction à évaluer",height=root.winfo_screenheight()*0.4,width=root.winfo_screenwidth()/3,bg="lightblue")
lf3.grid(row=1,column=2, sticky="e")
lf3.grid_propagate(False)

lf4 = LabelFrame(root, text="Texte source",height=root.winfo_screenheight()/2,width=root.winfo_screenwidth()/3,bg="lightblue")
lf4.grid(row=1,column=0, sticky="w")
lf4.grid_propagate(False)

lf5 = LabelFrame(root, text="Scores",height=root.winfo_screenheight()/2,width=root.winfo_screenwidth()*0.8,bg="#33CCFF")
lf5.grid(row=2,column=0, columnspan=2,sticky="n")
lf5.grid_propagate(False)

lf6 = LabelFrame(root, text="Evaluer",height=root.winfo_screenheight()/2,width=root.winfo_screenwidth()*0.2,bg="lightblue")
lf6.grid(row=2,column=2)
lf6.grid_propagate(False)

################################# BOUTONS ###########################

###### load buttons

loadFileButton1=Button(lf1, text='Charger le texte traduit de référence', width=30, height=2, bg="white")
loadFileButton1.grid(column=1, row=0, padx=root.winfo_screenwidth()/6, pady=root.winfo_screenheight()/50)
loadFileButton1.bind("<Button-1>", lambda event :loadRefFile())


loadFileButton2=Button(lf1, text='Charger le texte traduit à évaluer', width=30, height=2, bg="white")
loadFileButton2.grid(column=2, row=0, padx=root.winfo_screenwidth()/20, pady=root.winfo_screenheight()/50)
loadFileButton2.bind("<Button-1>", lambda event :loadHypFile())

loadFileButton3=Button(lf1, text='Charger le texte source (facultatif)', width=30, height=2, bg="white")
loadFileButton3.grid(column=0, row=0, padx=root.winfo_screenwidth()/20, pady=root.winfo_screenheight()/50)
loadFileButton3.bind("<Button-1>", lambda event :loadSrcFile())

### eval buttons

evalButton=Button(lf6, text="Lancer l'évaluation", width=20, height=2, bg="#0099FF")
evalButton.grid(column=0, row=0, pady=root.winfo_screenheight()/40, sticky="w")
evalButton.bind("<Button-1>", lambda event :evaluate(scoresMatrice))

exportButton=Button(lf6, text="Exporter les scores dans un fichier csv", width=30, height=2, bg="#33CCFF")
exportButton.grid(column=0, row=1, pady=root.winfo_screenheight()/20)
exportButton.bind("<Button-1>", lambda event :export_to_csv(scoresMatrice))


################ text widgets ###################

# texte ref
scrollbar1 = Scrollbar(lf2, bg="grey")
scrollbar1.pack( side = RIGHT, fill = Y )
# Create text widget and specify size.
t1 = Text(lf2,height=root.winfo_screenheight()/40,width=int(root.winfo_screenwidth()/26), yscrollcommand = scrollbar1.set, bg='#EAEAEA' )
t1.pack(expand=True, fill='both')
#t1.grid(sticky="we")
#T.grid_columnconfigure(0, weight=1)
scrollbar1.config( command = t1.yview )

#texte hyp
scrollbar2 = Scrollbar(lf3, bg="grey")
scrollbar2.pack( side = RIGHT, fill = Y )
# Create text widget and specify size.
t2 = Text(lf3,height=root.winfo_screenheight()/40,width=int(root.winfo_screenwidth()/26),yscrollcommand = scrollbar2.set, bg='#EAEAEA')
t2.pack(expand=True, fill='both')
scrollbar2.config(command = t2.yview )

#texte source
scrollbar3 = Scrollbar(lf4, bg="grey")
scrollbar3.pack( side = RIGHT, fill = Y )
# Create text widget and specify size.
t3 = Text(lf4,height=root.winfo_screenheight()/40,width=int(root.winfo_screenwidth()/26),yscrollcommand = scrollbar3.set, bg='#EAEAEA')
t3.pack(expand=True, fill='both')
#t3.grid(sticky="w")
scrollbar3.config(command = t3.yview )

#scores
scrollbar4 = Scrollbar(lf5, bg="grey")
scrollbar4.pack( side = RIGHT, fill = Y )
# Create text widget and specify size.
t4 = Text(lf5,height=root.winfo_screenheight()/50,width=int(root.winfo_screenwidth()/12),yscrollcommand = scrollbar4.set, bg='#EAEAEA')
t4.pack(expand=True, fill='both')
scrollbar4.config(command = t4.yview )


mainloop()

#########################################################################################################

root.mainloop()