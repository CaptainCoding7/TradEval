import csv
import matplotlib.pyplot as plt

rows=[]
f_in= open('AllScore.csv','r')
reader=csv.reader(f_in,delimiter=',')
for row in reader:
    rows.append(row)

rows.pop(0)
    
epochs=[]

for i in range(1,31):
    tab=[]
    for k in range(3+(i-1)*9,11+(i-1)*9):
        tab.append(float(rows[5][k]))   # rows[l][k] avec l la ligne de phrase
    epochs.append(tab)


bleu=[]
nist=[]
meteor=[]
wer=[]
ter=[]
rouge1=[]
rougeL=[]
fuzzymatching=[]

for epoch in epochs:
    bleu.append(epoch[0])
    nist.append(epoch[1])
    meteor.append(epoch[2])
    wer.append(epoch[3])
    ter.append(epoch[4])
    rouge1.append(epoch[5])
    rougeL.append(epoch[6])
    fuzzymatching.append(epoch[7])
    
x=[i for i in range(1,31)]

plt.figure(figsize=(13,5))
#plt.plot(x,bleu,linestyle='--',label='BLEU')
#plt.plot(x,nist,linestyle='--',label='Nist')
plt.plot(x,meteor,linestyle='--',label='METEOR')
plt.plot(x,wer,linestyle='--',label='WER')
plt.plot(x,ter,linestyle='--',label='TER')
plt.plot(x,rouge1,linestyle='--',label='ROUGE-1')
plt.plot(x,rougeL,linestyle='--',label='ROUGE-L')
plt.plot(x,fuzzymatching,linestyle='--',label='Fuzzy-matching')
plt.legend(loc='upper center', bbox_to_anchor=(0.6, 1.02),shadow=False, ncol=8)
plt.title('Score evolution for 30 epochs')
plt.xlabel("epochs")
plt.ylabel("score value")
plt.xticks(x)
plt.xlim(1,30)
plt.grid()
plt.savefig('scores.png')
