#!/usr/bin/python

#Builds a vocabulary file given a corpus file
#A vocabulary file is a file with each word that occurs in the corpus on 
#its own line. Words are not repeated. Punctuation is treated as a word, 
#So a sentence ending with "...asked him knowingly." would get tokenized into
#[..., "asked", "him", "knowingly", "."]. That way "knowingly" and "knowingly." 
#don't end up listed as seperate words. 

