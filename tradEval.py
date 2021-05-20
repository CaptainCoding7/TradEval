#!/usr/bin/env python
# -*- coding: utf-8 -*-



################ IMPORTATION DES MODULES ##################

from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Progressbar
import time
import numpy as np
import pandas as pd
from enum import Enum
import os
import subprocess
from threading import Thread
import concurrent.futures
from multiprocessing import Process


import re       # regex
import io

import csv
import math
import fractions
from collections import Counter
from files_manager import *

# import des bibiotheques de calcul de scores
import sacrebleu
from nltk.util import ngrams
from nist import sentence_nist
from meteor import single_meteor_score
from meteor import PorterStemmer
# ntlk.download('wordnet')
from meteor import wordnet
from wer import *
import pyter
from rouge_score import rouge_scorer


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
        #print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom

def closeMenu(popup):
    global killed
    killed=True
    popup.destroy()

def openAbout():

    about = Tk()
    x=about.winfo_screenwidth()*0.3
    y=about.winfo_screenheight()*0.3
    about.geometry("+%d+%d" % (x, y))


    about_msg = """

    TradEval is licensed under the MIT License

    MIT License

    Copyright (c) 2021 Agopian Paul, Lin Huiting, Sougoumar Pritie, Tahi Yasmine

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

    """

    about.wm_title("About TradEval")
    label = Label(about, text=about_msg)
    label.pack(side="top", fill="x", pady=10)
    about.mainloop()
   


def openManual():

    manual = Tk()
    x=manual.winfo_screenwidth()*0.3
    y=manual.winfo_screenheight()*0.3
    manual.geometry("+%d+%d" % (x, y))

    manual_msg = """

    *** Tiny manual ***

    Option 1: Evaluating a text
    
    The first option can be used to evaluate a translation by taking a target translation as a reference.
    The scores used to evaluate the distace between the two texts are mentionned below:

    Bleu (Papineni, 2002)
    Nist (Doddington, 2002)
    Meteor (Banerjee, 2005)
    WER
    TER (Snover, 2006)
    CharacTER (Wang, 2016)
    Rouge (Liu, 2011)
    Fuzzy-matching (Xu, 2020)

    =============================================================

    Option 2: Analysing an OpenNMT output with several scores

    The second option can be used to take in input a csv file containg an OpenNMT output.
    A new csv file with a similar structure is then created, and contains for each epochs the scores
    mentionned above.

    """

    manual.wm_title("TradEval - Tiny Manual")
    label = Label(manual, text=manual_msg)
    label.pack(side="top", fill="x", pady=10)
    manual.mainloop()
   



def popupmsg(msg):
    popup = Tk()

    x=popup.winfo_screenwidth()*0.45
    y=popup.winfo_screenheight()*0.4
    popup.geometry("+%d+%d" % (x, y))
    #popup.bind('<Escape>',self.toggle_geom)

    menubar = Menu(popup)

    menu1 = Menu(menubar, tearoff=0)
    menu1.add_command(label="Close", command = lambda: closeMenu(popup))
    menubar.add_cascade(label="File", menu=menu1)

    menu2 = Menu(menubar, tearoff=0)
    menu2.add_command(label="Tiny manual", command=openManual)
    menu2.add_command(label="About TradEval", command=openAbout)
    menubar.add_cascade(label="Help", menu=menu2)

    popup.config(menu=menubar)


    popup.wm_title("Welcome on TradEval !")
    label = Label(popup, text=msg)
    label.pack(side="top", fill="x", pady=10)
    B1 = Button(popup, text="Evaluating a text", command = popup.destroy)
    B1.pack()    
    B2 = Button(popup, text="Analysing an OpenNMT output with several scores", command = lambda: write_all_scores_into_csv(popup))
    B2.pack()
    popup.protocol("WM_DELETE_WINDOW", lambda arg=popup: closeMenu(arg))
    popup.mainloop()


    


# Chargement fichier de ref

def loadRefFile():
    #root.withdraw()
    global refFile
    refFile=askopenfilename(initialdir = "/path_host",title = "Select a translated reference text",filetypes = (("txt files","*.txt"),("pdf files","*.pdf")))
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
    hypFile=askopenfilename(initialdir = "/path_host",title = "Select a translated text to evaluate",filetypes = (("txt files","*.txt"),("pdf files","*.pdf")))
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
    srcFile=askopenfilename(initialdir = "/path_host",title = "Select the source text",filetypes = (("txt files","*.txt"),("pdf files","*.pdf")))
    print(srcFile+ " loaded")
    textToShow=file_to_string(srcFile)
    t3.delete('1.0',END)
    splittedText=textToShow.split('\n')
    i=1
    for s in splittedText:
        t3.insert(END, 'Phrase '+str(i)+' | '+s+'\n')
        i+=1
    ####################################################################



#### score processing functions ####


def bleu(r,h):

    b=sacrebleu.corpus_bleu([h], [[r]])
    bleu_splitted=str(b).split()
    sentScoreBleu=bleu_splitted[2]
    return sentScoreBleu

def nist(rw,hw):
    
    #nist
    # the nist algorithms calcules with a default highest ngrams order equaled to 5
    # so when the length of the sentence is below 5, a ZeroDivisionError occurs
    # we need to handle it:
    n=5
    while True:
        try:
            nistScore = float("{:.2f}".format(sentence_nist([rw], hw, n)))
            break;
        except ZeroDivisionError:
            #print("Nist reevaluation... Decreasing of the highest n-gram order... ")
            n-=1
    
    return nistScore

def meteor(r,h):
    
    #meteor
    meteorScore=float("{:.2f}".format(single_meteor_score(r, h, preprocess=str.lower, stemmer=PorterStemmer(), wordnet=wordnet, alpha=0.9, beta=3, gamma=0.5)))
    return meteorScore
    

def wer(rw,hw):

    # wer
    wer = WER(rw, hw)
    distance, path, ref_mod, hyp_mod = wer.distance()
    werScore=100*float("{:.2f}".format(distance[len(rw)][len(hw)]/len(rw)))
    return werScore

def ter(rw,hw):

    #ter
    terScore=100*float("{:.2f}".format( pyter.ter(hw, rw)))
    return terScore

def rouge(r,h):

    rouge=list()

    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    rougeNotFormated=scorer.score(r,h)
    rougeStr=str(rougeNotFormated).split()


    recall1=rougeStr[2].split('=')
    rouge1 = '%.2f' % float(recall1[1].split(',')[0])

    recallL=rougeStr[6].split('=')
    rougeL = '%.2f' % float(recallL[1].split(',')[0])

    rouge.append(rouge1)
    rouge.append(rougeL)
    
    return rouge

def characTer(r,h):
    
    f = open("ref_sentence.txt", "w")
    f.write(r)
    f.close()

    f = open("hyp_sentence.txt", "w")
    f.write(h)
    f.close()
    
    subprocess.getoutput("g++ -c -fPIC -m64 -std=c99 -lm -D_GNU_SOURCE -Wall -pedantic -fopenmp -o ed.o CharacTER-master/ed.cpp -lstdc++")
    subprocess.getoutput("g++ -m64 -shared -Wl,-soname,libED.so -o CharacTER-master/libED.so CharacTER-master/ed.o")
    cmd ="python3 /home/CharacTER/CharacTER.py -r ref_sentence.txt -o hyp_sentence.txt"
    #subprocess.getoutput(cmd)
    characTerScore = subprocess.getoutput(cmd)

    # deletion
    os.system("rm ref_sentence*")
    os.system("rm hyp_sentence*")

    return float("{:.2f}".format(100*float("{:.2f}".format(float(characTerScore)))))


def fuzzymatch(r,h):

        #print("ref: ",r)
        #print("hyp: ",h)

        #first, put the sentences into files
        f = open("ref_sentence.txt", "w")
        f.write(r)
        f.close()

        f = open("hyp_sentence.txt", "w")
        f.write(h)
        f.close()

        # compilation
        subprocess.getoutput("/home/fuzzy-match/build/cli/src/FuzzyMatch-cli -c ref_sentence.txt")
        # execution with subprocess
        cmd="/home/fuzzy-match/build/cli/src/FuzzyMatch-cli en -i ref_sentence.txt.fmi -a match -f 0.0 --ml 1 --mr 0 < hyp_sentence.txt"
        fuzzyOutput = subprocess.getoutput(cmd)

        buf=io.StringIO(fuzzyOutput)
        allOutput=buf.readlines()
        fuzzyScoreLine=str(allOutput).split()
        fuzzyScore=fuzzyScoreLine[4].split("\\")[0]
        fuzzyScore=fuzzyScore.replace("'","")
        fuzzyScore=float("{:.2f}".format(float(fuzzyScore)))

        # deletion
        os.system("rm ref_sentence*")
        os.system("rm hyp_sentence*")

        return float("{:.2f}".format(fuzzyScore))


#### FONCTION REALISANT LE CALCUL DES SCORES SUR UN TEXTE CHARGÉ

def evaluate(scoresMatrice):

    print("evaluation en cours...\n")
    global refFile
    global hypFile
    global refSent
    global hypSent

    # fenetre de chargement
    popup_window = Toplevel()
    popup_window.title("Evaluation")
    label = Label(popup_window, text = "Please wait during the scores calculus...")
    label.pack()
    p = Progressbar(popup_window,orient=HORIZONTAL,length=200,mode="determinate",takefocus=True,maximum=len(refSent))
    p.pack()
    x = root.winfo_screenwidth()/2
    y = root.winfo_screenheight()/2
    popup_window.geometry('+%d+%d' % (x, y))


    # score bleu pour tout le fichier
    #bleuScoreFile=file_bleu(refFile,hypFile)/100
    #print("bleu total= ",bleuScoreFile)

    refSent = file_to_listeSentence(refFile)
    hypSent = file_to_listeSentence(hypFile)

    i=1
    str_score=''

    scoresMatrice.append(('Numéro de phrase','Phrase de référence', 'Phrase à évaluer','Bleu', 'Score Nist', 'Score Meteor','Score Wer', 'Score Ter', 'Score characTER', 'Score Rouge1', 'Score RougeL', 'Score de Fuzzy Matching'))

    fuzzyScores=list()

    for r,h in zip(refSent,hypSent):


        # decomposition au mot pour le calcul des scores nist, wer, ter
        rw=r.split(" ")
        hw=h.split(" ")

        #bleu
        sentScoreBleu=bleu(r,h)

        #nist
        nistScore=nist(rw,hw)

        #meteor
        meteorScore=meteor(r,h)

        # wer
        werScore=wer(rw,hw)

        #ter
        terScore=ter(rw,hw)

        #characTER
        characTerScore=characTer(r,h)

        #rouge
        rougeScores=rouge(r,h)
        rouge1=rougeScores[0]
        rougeL=rougeScores[1]

        ###### FUZZY MATCHING
        #print("---- Fuzzy Matching: Phrase ",str(i))
        #fuzzyScores.append(fuzzymatch(r,h))
        fuzzyScr=fuzzymatch(r,h)

        # affichage et stockage des données dans la matrice des scores
        str_score += '* Sent.' + str(i)+':  - Bleu = ' + str(sentScoreBleu)+ '  - Nist = ' + str(nistScore) + '  - Meteor = ' + str(meteorScore)+ '  - Wer = '+'{:.0f}%'.format(werScore)+ '%   - Ter = '+ str(terScore)+ '%   - CharacTer = ' + str(characTerScore) + '%   - Rouge1 = '+ str(rouge1)+ '  - RougeL = ' + str(rougeL) + '  - FM = '+str(fuzzyScr)+'\n'
        scoresMatrice.append((str(i),r,h,str(sentScoreBleu), str(nistScore), str(meteorScore), '{:.0f}%'.format(werScore), str(characTerScore), str(terScore), str(rouge1), str(rougeL), str(fuzzyScr)))

        i+=1

        p.step()
        root.update()

    #### fin de la boucle for


    #print("**** FUZZY SCORES: ******")
    #print(fuzzyScores)

    popup_window.destroy()
    t4.delete('1.0',END)
    t4.insert(END, str_score)




######

def scoresProcessingSentence(r,h,sentCounter):
    
    global scoresMatrice

    #print("******* sentCounter : ",sentCounter, "*******")

    rw=r.split(" ")
    hw=h.split(" ")

    #bleu
    scoresMatrice[sentCounter][0]=bleu(r,h)
    
    #nist
    scoresMatrice[sentCounter][1]=nist(rw,hw)

    #meteor
    scoresMatrice[sentCounter][2]=meteor(r,h)
    
    # wer
    scoresMatrice[sentCounter][3]=wer(rw,hw)

    #ter
    scoresMatrice[sentCounter][4]=ter(rw,hw)

    #characTER
    scoresMatrice[sentCounter][5]=ter(rw,hw)

    # rouge (rouge1 and rougeL)
    rougeScore=rouge(r,h)
    scoresMatrice[sentCounter][6]=rougeScore[0]
    scoresMatrice[sentCounter][7]=rougeScore[1]

    # fuzzymatch
    scoresMatrice[sentCounter][8]=fuzzymatch(r,h)


    #print("SENTENCE ",sentCounter+1, " calculus completed")


def scoresProcessingColumn_SentThreads(refArray,hypArray):

    global scoresMatrice

    l=len(refArray)
    scoresMatrice = [[None] * 9 for i in range(l)]
    sentCounter=0


    # solution (doesn't work) for preventing meteor to crash when multithreading is used 
    #wordnet.ensure_loaded()
    

    while sentCounter<l:

        #print("LINE ",sentCounter+1)

        r=refArray[sentCounter]
        h=hypArray[sentCounter]
        #print(r)
        #print(h)
        
        scoresProcessingSentence(r,h,sentCounter)

        sentCounter+=1


    return scoresMatrice

############

def write_all_scores_into_csv(menu):

    scoresSent=[]
    scorename=['bleu','nist','meteor','wer','ter', 'characTER', 'rouge1', 'rougeL', 'fuzzymatching']
    nbScores=len(scorename)

    csv=askopenfilename(initialdir = "./",title = "Select a csv to analyse",filetypes = (("csv files","*.csv"),))

    #stp contains (source,target,predictions)
    stp = openLearningCsv(csv)

    nTest=10
    epoch=0
    #creation of the dictionnary
    # first we put the source sentences and the target sentences into a dataframe
    d = {stp[0][0] : stp[0][1:],stp[1][0] : stp[1][1:]}
    df = pd.DataFrame(d)

    # headers insertion into the dataframe
    num=1
    nbRow=len(stp[2])
    #nbRow=nTest #test
    nbCol=len(stp[2][0])

    # fenetre de chargement
    popup_window = Toplevel()
    popup_window.title="Generation of the csv file"
    label = Label(popup_window, text = "Please wait during the scores calculus...")
    label.pack()
    p = Progressbar(popup_window,orient=HORIZONTAL,length=200,mode="determinate",takefocus=True, maximum=nbCol)
    p.pack()
    x = menu.winfo_screenwidth()/2
    y =menu.winfo_screenheight()/2
    popup_window.geometry('+%d+%d' % (x, y))


    start=time.time()
    
    for col in range(nbCol):

        p.step()
        menu.update()

        num+=1
        pred_col_name=stp[2][0][col]

        # insertion of the prediction strings of a same column
        predSingleCol=[]
        for i in range(1,nbRow):
            predSingleCol.append(stp[2][i][col])
        df.insert(num,pred_col_name,pd.Series(predSingleCol))

        if (num-2)%6==0:
            epoch+=1
        #print("EPOCH ",epoch)
        
        #wordnet.ensure_loaded()
        # scores calculus for a single column
        scoresColumn=scoresProcessingColumn_SentThreads(stp[1][1:],predSingleCol)

        # insertion of the scores
        for i in range(nbScores):

            num+=1
            score_col_name = scorename[i]+" ("+pred_col_name+") "

            currentScoreArray=[]
            for j in range(len(scoresColumn)):
                currentScoreArray.append(scoresColumn[j][i])
                #print(scoresColumn[j][i])
            
            df.insert(num,score_col_name,pd.Series(currentScoreArray),True)
        


    #print(df)

    popup_window.destroy()


    end=time.time()
    print("ELAPSED TIME:::: ", end-start)

    # write dataframe to csv
    df.to_csv('AllScore.csv',index=False,header=True)
    print("--- export completed ---")



#######################################   MAIN ###############################
###############################################################################

##### variables globales

refFile=''
hypFile=''
refSent=[]
hypSent=[]
scoresMatrice=[]
killed=False


def evalTextMAin(popup):

    popup.destroy()


welcome=" Please choose one of the following options: \n"
popupmsg(welcome)

### fenetre principale
root=Tk()
#app=FullScreenApp(root)
root.title("TradEval - Evaluate a text")


####################  MENU HAUT  ##############################

# Pour créer le menu supérieur, on crée des objets avec la classe Menu()

# On assigne à ces objets différentes méthodes.

menubar = Menu(root)

menu1 = Menu(menubar, tearoff=0)
menu1.add_command(label="Main Menu",command = lambda: popupmsg(welcome))
menu1.add_command(label="Close",command = lambda: closeMenu(root))
menubar.add_cascade(label="File", menu=menu1)

menu2 = Menu(menubar, tearoff=0)
menu2.add_command(label="About", command=openAbout)
menubar.add_cascade(label="Help", menu=menu2)

root.config(menu=menubar)
root['bg']="lightblue"


###################  FRAMES  ##########################


lf1 = LabelFrame(root, text="Load files (.txt, .pdf)", height=root.winfo_screenheight()*0.1,width=root.winfo_screenwidth(),bg="lightblue")
lf1.grid(row=0,sticky='nw',column=0,columnspan=3)
lf1.grid_propagate(False)


lf2 = LabelFrame(root, text="Target translation",height=root.winfo_screenheight()*0.4,width=root.winfo_screenwidth()/3, bg="lightblue")
lf2.grid(column=1,row=1)
lf2.grid_propagate(False)

lf3 = LabelFrame(root, text="Translation to evaluate",height=root.winfo_screenheight()*0.4,width=root.winfo_screenwidth()/3,bg="lightblue")
lf3.grid(row=1,column=2, sticky="e")
lf3.grid_propagate(False)

lf4 = LabelFrame(root, text="Source text",height=root.winfo_screenheight()/2,width=root.winfo_screenwidth()/3,bg="lightblue")
lf4.grid(row=1,column=0, sticky="w")
lf4.grid_propagate(False)

lf5 = LabelFrame(root, text="Scores",height=root.winfo_screenheight()/2,width=root.winfo_screenwidth()*0.9,bg="#33CCFF")
lf5.grid(row=2,column=0, columnspan=2,sticky="n")
lf5.grid_propagate(False)

lf6 = LabelFrame(root, text="Evaluate",height=root.winfo_screenheight()/2,width=root.winfo_screenwidth()*0.2,bg="lightblue")
lf6.grid(row=2,column=2)
lf6.grid_propagate(False)

################################# BOUTONS ###########################

###### load buttons

loadFileButton1=Button(lf1, text='Load the translated target text', width=30, height=2, bg="white")
loadFileButton1.grid(column=1, row=0, padx=root.winfo_screenwidth()/6, pady=root.winfo_screenheight()/50)
loadFileButton1.bind("<Button-1>", lambda event :loadRefFile())


loadFileButton2=Button(lf1, text='Load the tanslated text to evaluate', width=30, height=2, bg="white")
loadFileButton2.grid(column=2, row=0, padx=root.winfo_screenwidth()/20, pady=root.winfo_screenheight()/50)
loadFileButton2.bind("<Button-1>", lambda event :loadHypFile())

loadFileButton3=Button(lf1, text='Load the source text (optional)', width=30, height=2, bg="white")
loadFileButton3.grid(column=0, row=0, padx=root.winfo_screenwidth()/20, pady=root.winfo_screenheight()/50)
loadFileButton3.bind("<Button-1>", lambda event :loadSrcFile())

### eval buttons

evalButton=Button(lf6, text="Start evaluation", width=20, height=2, bg="#0099FF")
evalButton.grid(column=0, row=0, pady=root.winfo_screenheight()/40, sticky="w")
evalButton.bind("<Button-1>", lambda event :evaluate(scoresMatrice))

exportButton=Button(lf6, text="Export scores in a csv file", width=30, height=2, bg="#33CCFF")
exportButton.grid(column=0, row=1, pady=root.winfo_screenheight()/20)
exportButton.bind("<Button-1>", lambda event :export_to_csv(scoresMatrice, root))

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




#########################################################################################################

if killed:
    root.destroy()
else:
    root.mainloop()
