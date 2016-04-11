Stupid Deep
===========

Some silly hackery with TensorFlow, especially the translation RNN example code.  

The TensorFlow translation example (https://www.tensorflow.org/versions/r0.7/tutorials/seq2seq/index.html) downloads an english-to-french aligned corpus. 
The french and english dictionaries are assumed to have one sentence per line. 
(https://github.com/tensorflow/tensorflow/blob/master/tensorflow/models/rnn/translate/data_utils.py) takes care of the cleaning up and conversion into a format TensorFlow can deal with, so the first order of business is writing a script that can do a similar task on my chat logs. 
According to the documentation for the training data, some sentences may not have corresponding translations. 

Vocabularies are generated from the files, and saved in a file with one word per line. 
There are some special symbols, like padding, end of sentence, and so on that are put in first. 
Sentences are then converted into strings of integers, where each integer is a vocabulary index. 

### Some concerns for chat corpuses
URLs should probably be stripped out, which probably also means removing chat text associated with them. 
Sometimes, a user says multiple things before the other user responds. These can be lumped together as one utterance. 
Conversations that only have one user, or one user and an away message, should be dropped entirely. 

So before generating the vocabularies and the data files, some work will have to be done to clean the chat corpuses. 
However, initial generation of the vocabularies will be useful for targeting the cleaning work. 

### Deep learning and _horror_vacuui_

Turns out that chatbots and question answering can be viewed as translation problems. 
Sort of. 
A chatbot transforms input chat messages into output chat messages. 
A question answering AI translates from questions to answers. 
There are, however, some problems with this idea. 
Translations change languages without changing meaning. 
Since word embeddings are supposed to capture some information about meaning, or at least relationships between symbols in a string, it makes some sense that meaning is preserved. 
However, question answering and conversation rely on each participant emitting sequences of symbols with different meanings, not the same meaning rephrased. 
On the other hand, it's not like NNs actually "know" what things "mean" anyway, so maybe this won't be a problem (for more info: http://organizations.utep.edu/portals/1475/nagel_bat.pdf ).

This, I think, more than other problems (utility monsters and the like) sits at the core of human aversion to "intelligent machines". 
There is no place in a neural network that knows French, or English, that recognizes a dog or a bike. 
The math in them is so simple that it can be explained to a child. 
They act without knowing, and so raise the possiblity that we also act without knowing. 
That consciousness is an epiphenomenon, that "being" as we experience it is not required and has no use. 
Clearly, this is not something that people want to directly grapple with, so they write a stupid chatbot to amuse themselves. 
