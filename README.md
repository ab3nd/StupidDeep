Some silly hackery with TensorFlow, especially the translation RNN. 

Turns out that chatbots and question answering can be viewed as translation problems. Sort of. 

The TensorFlow translation example (https://www.tensorflow.org/versions/r0.7/tutorials/seq2seq/index.html) downloads an english-to-french aligned corpus. 
The french and english dictionaries are assumed to have one sentence per line. 
(https://github.com/tensorflow/tensorflow/blob/master/tensorflow/models/rnn/translate/data_utils.py) takes care of the cleaning up and conversion into a format TensorFlow can deal with, so the first order of business is writing a script that can do a similar task on my chat logs. 


