#!/usr/bin/python

#Builds a vocabulary file given a corpus file
#A vocabulary file is a file with each word that occurs in the corpus on 
#its own line. Words are not repeated. Punctuation is treated as a word, 
#So a sentence ending with "...asked him knowingly." would get tokenized into
#[..., "asked", "him", "knowingly", "."]. That way "knowingly" and "knowingly." 
#don't end up listed as seperate words. 

#Because the script that generated my corpus uses <<SEND>> to indicate that 
#a user sent an instant message, the tokenizer splits on spaces first, and then 
#continues to attempt to split tokens after that, but avoiding <<SEND>> tokens. 

import sys
import re

infiles = ["me_data.txt", "them_data.txt"]

for file in infiles:
	basename = file.split('.')[0]

	with open(file, 'r') as inFile:
		vocab = {}

		#Tokenize each line and read into a file
		for line in inFile:
			#TODO detect URLs and spare them

			#Put space before commas, periods, semicolons
			for char in ['.', ':', ',', ';', '?', '!', '(', ')', '\\', '/', '\"']:
				line = line.replace(char, ' {0} '.format(char))
			tok = line.split();

			#Keep a count
			for token in tok:
				if token in vocab.keys():
					vocab[token] += 1
				else:
					vocab[token] = 1

		#Done reading the file, now print the words and counts to csv
		#First, convert the dictionary to a list of tuples, and sort it
		vocabList=[]
		for key in vocab.keys():
			vocabList.append((key, vocab[key]))
		vocabList =sorted(vocabList, key=lambda x:x[1])

		with open(basename + "_counts.csv", 'w') as countsFile, open(basename + "_vocab.txt", 'w') as vocabFile:
			for item in vocabList:
				countsFile.write("{0},{1}\n".format(item[0], item[1]))
				vocabFile.write("{0}\n".format(item[0]))



