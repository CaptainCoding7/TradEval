#!/usr/bin/env python
# -*- coding: utf-8 -*-



################ IMPORTATION DES MODULES ##################

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
            print("Nist reevaluation... Decreasing of the highest n-gram order... ")
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
    werScore=100 * distance[len(rw)][len(hw)]/len(rw)
    return werScore

def ter(rw,hw):

    #ter
    terScore='%.3f' % pyter.ter(hw, rw)
    return terScore

    print("SENTENCE ",sentCounter+1, " calculus completed")

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

     subprocess.getoutput("g++ -c -fPIC -m64 -std=c99 -lm -D_GNU_SOURCE -Wall -pedantic -fopenmp -o ed.o /home/CharacTER/ed.cpp -lstdc++")
     subprocess.getoutput("g++ -m64 -shared -Wl,-soname,libED.so -o /home/CharacTER/libED.so /home/CharacTER/ed.o")
    cmd ="python3 CharacTER.py -r ref_sentence.txt -o hyp_sentence.txt"
    subprocess.getoutput(cmd)
    output = subprocess.getoutput(cmd)
   



    # deletion
    #os.system("rm ref_sentence*")
    #os.system("rm hyp_sentence*")


def fuzzymatch(r,h):

        print("ref: ",r)
        print("hyp: ",h)

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
        cmd="/home/fuzzy-match/build/cli/src/FuzzyMatch-cli en -i ref_sentence.txt.fmi -a match -f 0.3 -N 4 -n 1 [--ml 10] -P < hyp_sentence.txt"
        fuzzyOutput = subprocess.getoutput(cmd)

        buf=io.StringIO(fuzzyOutput)
        allOutput=buf.readlines()
        fuzzyScoreLine=str(allOutput).split()
        fuzzyScore=fuzzyScoreLine[4].split("\\")[0]
        fuzzyScore=fuzzyScore.replace("'","")
        fuzzyScore='%.3f' % float(fuzzyScore)

        # deletion
        #os.system("rm ref_sentence*")
        #os.system("rm hyp_sentence*")

        return fuzzyScore


#### FONCTION REALISANT LE CALCUL DES SCORES SUR UN TEXTE CHARGÉ

def evaluate(scoresMatrice):

    print("evaluation en cours...\n")
    global refFile
    global hypFile
    global refSent
    global hypSent

    # score bleu pour tout le fichier
    #bleuScoreFile=file_bleu(refFile,hypFile)/100
    #print("bleu total= ",bleuScoreFile)

    i=1
    str_score=''

    scoresMatrice.append(('Numéro de phrase','Phrase de référence', 'Phrase à évaluer','Score Bleu', 'Score Nist', 'Score Meteor','Score Wer', 'Score Ter'))

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

        #red
        redScore=rouge(r,h)


        ###### FUZZY MATCHING
        print("---- Fuzzy Matching: Phrase ",str(i))
        #fuzzyScores.append(fuzzymatch(r,h))
        fuzzyScr=fuzzymatch(r,h)

        #characTER
        characTer(r,h)


        # affichage et stockage des données dans la matrice des scores
        str_score+='--- Phrase n°'+str(i)+':    - Bleu = '+str(sentScoreBleu)+ '    - Nist = '+str(nistScore)+ '    - Meteor = '+str(meteorScore)+ '    - Wer = '+'{:.0f}%'.format(werScore)+ '    - Ter = '+terScore+'    - FuzzyMatching = '+str(fuzzyScr)+'\n'
        scoresMatrice.append((str(i),r,h,str(sentScoreBleu),str(nistScore), str(meteorScore),'{:.0f}%'.format(werScore), str(terScore),str(fuzzyScr)))

        i+=1

    #### fin de la boucle for


    print("**** FUZZY SCORES: ******")
    print(fuzzyScores)





######

def scoresProcessingSentence(r,h,sentCounter):
    
    global scoresMatrice

    print("******* sentCounter : ",sentCounter, "*******")

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

    print("SENTENCE ",sentCounter+1, " calculus completed")


def scoresProcessingColumn(refArray,hypArray):

    global scoresMatrice

    l=len(refArray)
    scoresMatrice = [[None] * 5 for i in range(l)]
    sentCounter=0


    # solution (doesn't work) for preventing meteor to crash when multithreading is used 
    #wordnet.ensure_loaded()
    

    while sentCounter<l:

        pList=list()

        for i in range(2):

            if sentCounter<l:

                print("LINE ",sentCounter+1)

                r=refArray[sentCounter]
                h=hypArray[sentCounter]
                #print(r)
                #print(h)

                
                #p = Process(target=scoresProcessingSentence, args=(r,h,sentCounter))
                #pList.append(p)
                #p.start()
                
                scoresProcessingSentence(r,h,sentCounter)

                """
                #meteor
                meteorScore=float("{:.2f}".format(single_meteor_score(r, h, preprocess=str.lower, stemmer=PorterStemmer(), wordnet=wordnet, alpha=0.9, beta=3, gamma=0.5)))
                scoresMatrice[sentCounter][2]=meteorScore
                """

                sentCounter+=1
            
            else:
                break

        for p in pList:
            p.join()


    return scoresMatrice

############

def write_all_scores_into_csv():

    scoresSent=[]
    scorename=['bleu','nist','meteor','wer','ter']
    nbScores=len(scorename)

    csv=askopenfilename(initialdir = "./",title = "Selectionner un csv à analyser",filetypes = (("csv files","*.csv"),))

    #stp contains (source,target,predictions)
    stp = loadNMTcsv(csv)

    nTest=5
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

    start=time.time()
    
    for col in range(nbCol):
        num+=1
        pred_col_name=stp[2][0][col]

        # insertion of the prediction strings of a same column
        predSingleCol=[]
        for i in range(1,nbRow):
            predSingleCol.append(stp[2][i][col])
        df.insert(num,pred_col_name,pd.Series(predSingleCol))

        if (num-2)%6==0:
            epoch+=1
        print("EPOCH ",epoch)
        
        #wordnet.ensure_loaded()
        # scores calculus for a single column
        scoresColumn=scoresProcessingColumn(stp[1][1:],predSingleCol)

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

    end=time.time()
    print("ELAPSED TIME:::: ", end-start)

    # write dataframe to csv
    df.to_csv('AllScore.csv',index=False,header=True)
    print("--- export completed ---")

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


arg_len=len(sys.argv)

if arg_len == 1:
    print("no input files enter")
elif arg_len == 2:
    print("csv enter")
else :
    print("ref and candidate enter")
    refFile = sys.argv[1]
    hypFile = sys.argv[2]
    evaluate(scoresMatrice)
    export_to_csv(scoresMatrice)
    print(refFile)



