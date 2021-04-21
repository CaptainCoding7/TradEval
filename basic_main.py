#!/usr/bin/env python
# -*- coding: utf-8 -*-



################ IMPORTATION DES MODULES ##################

import time
import asyncio
import numpy as np
import pandas as pd
from enum import Enum
import os
import sys


import re       # regex
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
from algorithims import *
from match import *

from fuzzywuzzy import fuzz



############### root PRINCIPALE  ######################

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

    refSent = file_to_listeSentence(refFile)
    hypSent = file_to_listeSentence(hypFile)

    i=1
    str_score=''

    scoresMatrice.append(('Numéro de phrase','Phrase de référence', 'Phrase à évaluer','Score Bleu', 'Score Nist', 'Score Meteor','Score Wer', 'Score Ter'))

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
        os.system("/home/paul/Documents/proj_tansv/fuzzy-match-master/build/cli/src/FuzzyMatch-cli -c ref_sentence.txt")
        # execution
        os.system("/home/paul/Documents/proj_tansv/fuzzy-match-master/build/cli/src/FuzzyMatch-cli en -i ref_sentence.txt.fmi -a match -f 0.3 -N 4 -n 1 [--ml 10] -P < hyp_sentence.txt")

        # deletion
        os.system("rm ref_sentence*")
        os.system("rm hyp_sentence*")


        # bigrams
        #print("     Evaluation par groupe de 2 mots: ", trigram(h,r,2))
        #trigrams
        #print("     Trigrams algorithm: ", trigram(h,r))
        #4grams
        #print("     Evaluation par groupe de 4 mots: ", trigram(h,r,4))
        #5-grams
        #print("     Evaluation par groupe de 5 mots: ", trigram(h,r,5))

        #print("     Levenshtein distance algorithm: ", levenshtein(h,r))
        #print("     Cosine algorithm ", cosine(h,r))
        #print("     Jaro-Winkler algorithm ", jaro_winkler(h,r))
        #print("     With fuzzywuzzy package: ", fuzz.token_set_ratio(r,h))

        #print(extractOne(h, [r]))


        # affichage et stockage des données dans la matrice des scores
        str_score+='--- Phrase n°'+str(i)+':    - Bleu = '+str(sentScoreBleu)+ '    - Nist = '+str(nistScore)+ '    - Meteor = '+str(meteorScore)+ '    - Wer = '+'{:.0f}%'.format(werScore)+ '    - Ter = '+terScore+'\n'
        scoresMatrice.append((str(i),r,h,str(sentScoreBleu),str(nistScore), str(meteorScore),'{:.0f}%'.format(werScore), str(terScore)))

        i+=1



 
 

    
def scoresProcessingSentence(r,h,sentCounter):

    global scoresMatrice

    print("******* sentCounter : ",sentCounter, "*******")

    rw=r.split(" ")
    hw=h.split(" ")

    #bleu
    #sentScoreBleu=list_bleu([r], [h])
    b=sacrebleu.corpus_bleu([h], [[r]])
    bleu_splitted=str(b).split()
    sentScoreBleu=bleu_splitted[2]
    scoresMatrice[sentCounter][0]=sentScoreBleu
    
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
    scoresMatrice[sentCounter][1]=nistScore

    """
    #meteor
    meteorScore=float("{:.2f}".format(single_meteor_score(r, h, preprocess=str.lower, stemmer=PorterStemmer(), wordnet=wordnet, alpha=0.9, beta=3, gamma=0.5)))
    scoresMatrice[sentCounter][2]=meteorScore
    """
    # wer
    wer = WER(rw, hw)
    distance, path, ref_mod, hyp_mod = wer.distance()
    werScore=100 * distance[len(rw)][len(hw)]/len(rw)
    scoresMatrice[sentCounter][3]='%.2f' % werScore


    #ter
    terScore='%.2f' % pyter.ter(hw, rw)
    scoresMatrice[sentCounter][4]=terScore


    print("SENTENCE ",sentCounter+1, " calculus completed")



def test(r,h,sc):
    time.sleep(sc/10)

#### score processing functions ####


def bleu(r,h,sentCounter):
    
    global scoresMatrice

    b=sacrebleu.corpus_bleu([h], [[r]])
    bleu_splitted=str(b).split()
    sentScoreBleu=bleu_splitted[2]
    scoresMatrice[sentCounter][0]=sentScoreBleu


def meteor(r,h,sentCounter):

    global scoresMatrice

    
    #meteor
    meteorScore=float("{:.2f}".format(single_meteor_score(r, h, preprocess=str.lower, stemmer=PorterStemmer(), wordnet=wordnet, alpha=0.9, beta=3, gamma=0.5)))
    scoresMatrice[sentCounter][2]=meteorScore
    

def wer(rw,hw,sentCounter):

    global scoresMatrice

    # wer
    wer = WER(rw, hw)
    distance, path, ref_mod, hyp_mod = wer.distance()
    werScore=100 * distance[len(rw)][len(hw)]/len(rw)
    scoresMatrice[sentCounter][3]=werScore

def ter(rw,hw,sentCounter):

    global scoresMatrice

    #ter
    terScore='%.3f' % pyter.ter(hw, rw)
    scoresMatrice[sentCounter][4]=terScore

    print("SENTENCE ",sentCounter+1, " calculus completed")


def nist(rw,hw,sentCounter):
    
    global scoresMatrice

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
    scoresMatrice[sentCounter][1]=nistScore


############

def write_all_scores_into_csv():

    global csvFile
    scoresSent=[]
    scorename=['bleu','nist','meteor','wer','ter']
    nbScores=len(scorename)


    csv='/home/paul/Documents/proj_tansv/datasets/adadelta_translation_copie.csv'

    #stp contains (source,target,predictions)
    stp = openLearningCsv(csv)

    nTest=5
    epoch=0
    #creation of the dictionnary
    # first we put the source sentences and the target sentences into a dataframe
    d = {stp[0][0] : stp[0][1:nTest],stp[1][0] : stp[1][1:nTest]}
    df = pd.DataFrame(d)

    # headers insertion into the dataframe
    num=1
    nbRow=len(stp[2])
    nbRow=nTest #test
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
        scoresColumn=scoresProcessingColumn_SentThreads(stp[1][1:nTest],predSingleCol)

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
    print("export ----")

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




