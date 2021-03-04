import csv

def write2file(array):
	with open('results.csv','w') as csvfile:
		writer = csv.writer(csvfile)
		for r in array:
			writer.writerow(r)
	

tab = [('SN', 'Name', 'Quotes'),
	(1, 'Linus Torvalds', 'Linux Kernel'),
	(2, 'Tim Berners-Lee', 'World Wide Web'),
	(3, 'Guido van Rossum', 'Python Programming')]
	
write2file(tab)