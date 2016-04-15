#!/usr/bin/python

#Heavily based on the translation example from google's tensorflow tutorials

import tensorflow as tf
import utils
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os
import random
import sys
import time

tf.app.flags.DEFINE_float("learning_rate", 0.5, "Learning rate.")
tf.app.flags.DEFINE_float("learning_rate_decay_factor", 0.99,
                          "Learning rate decays by this much.")
tf.app.flags.DEFINE_float("max_gradient_norm", 5.0,
                          "Clip gradients to this norm.")
tf.app.flags.DEFINE_integer("batch_size", 64,
                            "Batch size to use during training.")
tf.app.flags.DEFINE_integer("size", 1024, "Size of each model layer.")
tf.app.flags.DEFINE_integer("num_layers", 3, "Number of layers in the model.")
tf.app.flags.DEFINE_integer("en_vocab_size", 40000, "English vocabulary size.")
tf.app.flags.DEFINE_integer("fr_vocab_size", 40000, "French vocabulary size.")
tf.app.flags.DEFINE_string("data_dir", "/tmp", "Data directory")
tf.app.flags.DEFINE_string("train_dir", "/tmp", "Training directory.")
tf.app.flags.DEFINE_integer("max_train_data_size", 0,
                            "Limit on the size of training data (0: no limit).")
tf.app.flags.DEFINE_integer("steps_per_checkpoint", 200,
                            "How many training steps to do per checkpoint.")
tf.app.flags.DEFINE_boolean("decode", False,
                            "Set to True for interactive decoding.")
tf.app.flags.DEFINE_boolean("self_test", False,
                            "Run a self-test if this is set to True.")

FLAGS = tf.app.flags.FLAGS


# We use a number of buckets and pad to the closest one for efficiency.
# See seq2seq_model.Seq2SeqModel for details of how they work.
_buckets = [(5, 10), (10, 15), (20, 25), (40, 50)]

def load_data_files(sourcePath, targetPath):
	#A list of lists, each list is one bucket
	data_set = [[] for _ in buckets]

	with open(sourcePath, "r") as sourceFile and open(targetPath, "r") as targetFile:
		source, target = sourceFile.readline(), targetFile.readline()
		counter = 0
		while source and target:
			#Just to indicate something's happening
			counter += 1
			if counter % 1000 == 0:
				print "Reading line {0}".format(counter)
				sys.stdout.flush()
			#Each line of a data file is a list of numbers with spaces between them. 
			sourceIDs = [int(x) for x in source.split()]
			targetIDs = [int(x) for x in target.split()]
			#TODO Should I append <<SEND>> symbols here?
			#Put the data into the proper bucket
			for bucket_id, (source_size, target_size) in enumerate(_buckets):
				if len(sourceIDs) < source_size and len(targetIDs) < target_size:
					data_set[bucket_id].append([sourceIDs, targetIDs])
					break
			source, target = sourceFile.readline(), targetFile.readline()
	return data_set

def train(in_data_path, out_data_path):
	#Prepare the data

	with tf.Session() as sess:
		model = create_model(sess, False)

		#read the data into the buckets
		#TODO seperate the training and the dev set, you're asking for overfitting here
		dev_set = load_data_files(in_data_path, out_data_path)
 		train_set = load_data_files(in_data_path, out_data_path)
    	train_bucket_sizes = [len(train_set[b]) for b in xrange(len(_buckets))]
    	train_total_size = float(sum(train_bucket_sizes))
		# A bucket scale is a list of increasing numbers from 0 to 1 that we'll use
	    # to select a bucket. Length of [scale[i], scale[i+1]] is proportional to
	    # the size if i-th training bucket, as used later.
	    train_buckets_scale = [sum(train_bucket_sizes[:i + 1]) / train_total_size
	                           for i in xrange(len(train_bucket_sizes))]

	    # This is the training loop.
	    step_time, loss = 0.0, 0.0
	    current_step = 0
	    previous_losses = []
	    while True:
	      # Choose a bucket according to data distribution. We pick a random number
	      # in [0, 1] and use the corresponding interval in train_buckets_scale.
	      random_number_01 = np.random.random_sample()
	      bucket_id = min([i for i in xrange(len(train_buckets_scale))
	                       if train_buckets_scale[i] > random_number_01])

	      # Get a batch and make a step.
	      start_time = time.time()
	      encoder_inputs, decoder_inputs, target_weights = model.get_batch(
	          train_set, bucket_id)
	      _, step_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,
	                                   target_weights, bucket_id, False)
	      step_time += (time.time() - start_time) / FLAGS.steps_per_checkpoint
	      loss += step_loss / FLAGS.steps_per_checkpoint
	      current_step += 1

	      # Once in a while, we save checkpoint, print statistics, and run evals.
	      if current_step % FLAGS.steps_per_checkpoint == 0:
	        # Print statistics for the previous epoch.
	        perplexity = math.exp(loss) if loss < 300 else float('inf')
	        print ("global step %d learning rate %.4f step-time %.2f perplexity "
	               "%.2f" % (model.global_step.eval(), model.learning_rate.eval(),
	                         step_time, perplexity))
	        # Decrease learning rate if no improvement was seen over last 3 times.
	        if len(previous_losses) > 2 and loss > max(previous_losses[-3:]):
	          sess.run(model.learning_rate_decay_op)
	        previous_losses.append(loss)
	        # Save checkpoint and zero timer and loss.
	        checkpoint_path = os.path.join(FLAGS.train_dir, "translate.ckpt")
	        model.saver.save(sess, checkpoint_path, global_step=model.global_step)
	        step_time, loss = 0.0, 0.0
	        # Run evals on development set and print their perplexity.
	        for bucket_id in xrange(len(_buckets)):
	          if len(dev_set[bucket_id]) == 0:
	            print("  eval: empty bucket %d" % (bucket_id))
	            continue
	          encoder_inputs, decoder_inputs, target_weights = model.get_batch(
	              dev_set, bucket_id)
	          _, eval_loss, _ = model.step(sess, encoder_inputs, decoder_inputs,
	                                       target_weights, bucket_id, True)
	          eval_ppx = math.exp(eval_loss) if eval_loss < 300 else float('inf')
	          print("  eval: bucket %d perplexity %.2f" % (bucket_id, eval_ppx))
	        sys.stdout.flush()


def main(_):
	train("stupid_deep_data/them_data.ids", "stupid_deep_data/me_data.ids")

if __name__ == "__main__":
	tf.app.run()