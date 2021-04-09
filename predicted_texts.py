import csv
from collections import defaultdict

texts=[]
with open('adadelta_translation copie.csv','r') as f_in:
    reader=csv.reader(f_in,delimiter=',')
    for row in reader:
        texts.append(row)

col_num=[0,1]
for i in range(2,len(texts[0]),4):
    col_num.append(i) 

with open('texts.csv','w') as f_out:
    writer=csv.writer(f_out)
    for row in texts:
        content=list(row[i] for i in col_num)
        writer.writerow(content)


