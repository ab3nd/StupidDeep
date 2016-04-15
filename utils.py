#!/usr/bin/python

#utility functions for dealing with data generated from my chat logs. 

#Stupid tokenizer is stupid, and munges URLs real hard
def tokenize(inputStr):
	#Put space before commas, periods, semicolons
	for char in ['.', ':', ',', ';', '?', '!', '(', ')', '\\', '/', '\"']:
		inputStr = inputStr.replace(char, ' {0} '.format(char))
	tok = inputStr.split();
	return tok

#Initialize a vocabulary from a file
#Vocabulary files have one word per line
#returns a pair of a dictionary mapping strings to integers, 
#and a list with all the strings at their integer indexes (for reverse lookups)
def init_vocab(vocab_path):
	reverse_vocab = []
	#TODO, check if the vocabulary file exists
	with open(vocab_path, "rb")	as infile:
		reverse_vocab.extend(infile.readlines())
	reverse_vocab = [line.strip() for line in reverse_vocab]
	vocab = dict([(x,y) for (y,x) in enumerate(reverse_vocab)])
	return vocab, reverse_vocab

#Convert a string to a list with the IDs of all of the vocabulary tokens in the string. 
#If a token isn't in the vocabulary, it gets set to <<UNK>>
def str_to_IDs(sentence, vocab):
	words = tokenize(sentence)
	return [vocab.get(w, '<<UNK>>') for w in words]

#Convert corpus files (human-readable strings) into files containing lists of token IDs
def create_ID_data(data_path, vocab_path):
	#Generate name for output file
	basename = data_path.split('.')[0]
	#TODO Check that vocab path exists and data path exists
	#Load vocabulary 
	vocab, _ = init_vocab(vocab_path)
	#Convert file
	with open(data_path, 'r') as inFile, open(basename+".ids", 'w') as outFile:
		for line in inFile.readlines():
			IDs = str_to_IDs(line, vocab)
			outFile.write(" ".join([str(identifier) for identifier in IDs]) + "\n")
