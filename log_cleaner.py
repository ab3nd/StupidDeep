#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#Generates a corpus for training an encoder/decoder RNN from chat log files. 

#The training data consists of files with one chat utterance per line. 
#One file is what the other person said, the other file is what I said in 
#response. 
#
#This script also generates vocabulary files, with one line per unique word,
#for both the other user's utterances and mine. 
import os
import BeautifulSoup as bs
import re
import io

#This is so that I can check this file into github without checking in personal information 
#It contains a single list called "names", that is the strings that represent my name on chat clients. 
from namelist import my_names

#Directory where pidgin keeps its logfiles. 
#On my system, this is a symlink to dropbox, and all my logs are actually there. 
#See http://gizmosmith.com/2012/09/10/cross-system-chat-log-sync/
log_dir = os.path.expanduser("~/.purple/logs")

#Users who never say anything useful to me. 
ignore_users = ["nickserv", "chanserv", "aolsystemmsg"]

#Paths for writing the data files
them_data_path = "./them_data.txt"
me_data_path = "./me_data.txt"

class LogParser:
	def __init__(self):
		self.parser = None

	def parse(self, path):
		#Sort out what we're parsing
		if path.endswith(".html"):
			#HTML format logs, parse with HTML parser
			self.parser = HTMLParser()
		elif path.endswith(".txt"):
			#Text format log, parse with text parser
			self.parser = TxtParser()
		elif path.endswith(".png") or path.endswith(".jpg"):
			#Image, don't bother parsing
			self.parser = None
		else:
			#Unknown format, tell the user
			self.parser = None
			print "Unknown format {0}".format(path)

		#If we're working on something
		if self.parser is not None:
			with open(path, 'r') as infile:
				raw_data = infile.read()
				self.parser.parse(raw_data)

	def getData(self):
		if self.parser is not None:
			return self.parser.getData()
		else:
			return None

class HTMLParser(LogParser):
	def __init__(self):
		#A chat has participants and a chronolgically ordered list of utterances.
		#Each utterance is a pair consisting of who said it and what they said. 
		self.chat = {}
		self.chat['participants'] = set()
		self.chat['content'] = []
	
	def parse(self, data):
		soup = bs.BeautifulSoup(data, convertEntities=bs.BeautifulSoup.HTML_ENTITIES)

		# The speaker is in bold tags
		speakers = soup.findAll('b')
		# These get ignored when parsing out the message
		pass_tags = ['body', 'span', 'html', 'pre', 'em', 'p']

		for speaker in speakers:
			uname = None
			message = None
			#If it's not a name, which ends in a colon, or a pose, which starts with asterisks, skip it
			if (speaker.text.endswith(":") or speaker.text.startswith("***")):
				if re.search("AUTO-REPLY", speaker.text):
					continue
				else:
					uname = speaker.next.strip(" *:")
					#Try to get the rest of the string
					message = ""
					item = speaker.next.next
					#Append text into the message until we hit a br tag
					while item is not None:
						if isinstance(item, bs.NavigableString):
							message += item
						else:
							if item.name == 'br':
								#Hit the end of the line, time to stop adding to the message
								break
							elif item.name == 'a':
								#Deals with malformed stuff like "<a href="https://twitter.com/BettyBowers/status/698636904632176640">35 minutes ago<br /></a>"
								if item.string is not None: 
									message += item.string + " "
							elif item.name == 'img':
								#Not parsing images
								pass
							elif item.name in pass_tags:
								#Could have other tags in it, get it when we get to the string
								pass
							else:
								#Use the debugger to figure out this case
								import pdb; pdb.set_trace()
						item = item.next

			#This deals with OTR error messages so that the unecrypted message text can still be used
			elif speaker.text.startswith("The following message received from"):
				#Recover username and message
				uname = re.search("from (.*) wasnotencrypted", speaker.text)
				message = re.search(": \[(.*)\]", speaker.text)
				if uname and message:
					uname = uname.group(1)
					message = message.group(1)

			#Now we have both a username and a message
			if uname and message:
				#This converts user@gmail.com/637c5c0c names to just the e-mail address
				uname = re.split("\/", uname)[0]
				#Usernames are normalized to lowercase
				self.chat["participants"].add(uname.lower())
				self.chat["content"].append((uname.lower(), message))
		
	def getData(self):
		return self.chat

class TxtParser(LogParser):
	def __init__(self):
		#A chat has participants and a chronolgically ordered list of utterances.
		#Each utterance is a pair consisting of who said it and what they said. 
		self.chat = {}
		self.chat['participants'] = set()
		self.chat['content'] = []
	
	def parse(self, data):
		currentUtterance = ""
		lines = data.split("\n")
		currentUtterance = lines[1]
		for line in lines[2:]:
			if line.startswith("("):
				#Parse current utterance
				if re.search("AUTO-REPLY", currentUtterance):
					#Skip auto-reply lines
					continue
				matches = re.match("\([0-9:AMP ]*\) ([^:]*): (.*)", currentUtterance)
				if not matches:
					# Poses, rather than messages
					matches = re.match("\([0-9:AMP ]*\) \*\*\*([^ ]*) (.*)", currentUtterance)
				if not matches:
					#Probably status notification. This does miss it if people enter a newline and then
					#start that line with a parenthetical statement, but that's rare. 
					pass
				if matches:
					#We got something, add it to the chat. 
					self.chat["participants"].add(matches.group(1).lower())
					#Messages get converted to unicode because the HTML parser also gives me unicode
					self.chat["content"].append((matches.group(1).lower(), matches.group(2)))
				currentUtterance = line
			else:
				currentUtterance += line

	def getData(self):
		return self.chat

def generate_training_data(conversation, my_names):
	otherSpeaker = None
	currentSpeaker = None
	myBuffer = ""
	theirBuffer = ""

	#If neither participant is in my names, it's a conversation that was 
	#logged on a computer that I'm not on. 
	inConvo = False
	for meName in my_names:
		for pName in conversation["participants"]:
			if pName.startswith(meName):
				inConvo = True

	if not inConvo:
		#print conversation["participants"]
		return

	#Iterate over the messages sent
	#For as long as they continue to talk, append their utterances to the buffer, seperated by <<SEND>> tokens.
	#When the next person starts talking
	#For as long as they continue to talk, append their utterances to a second buffer, with <<SEND>> tokens. 
	#When the first person starts talking again, write the utterances to both files. 
	for message in conversation["content"]:
		if message[0] in my_names and currentSpeaker is None:
			#Ignore my first utterances if I started the conversation
			continue
		else:
			if otherSpeaker is None and currentSpeaker is None and not (message[0] in my_names):
				#This is the other speaker's first utterance
				otherSpeaker = message[0]
				currentSpeaker = otherSpeaker
				theirBuffer += message[1] + "<<SEND>>"
			elif message[0] == otherSpeaker and currentSpeaker == otherSpeaker:
				#They are talking, and this message is from them
				theirBuffer += message[1] + "<<SEND>>"
			elif message[0] in my_names and currentSpeaker == otherSpeaker:
				#I'm starting to respond
				currentSpeaker = message[0]
				myBuffer += message[1] + "<<SEND>>"
			elif message[0] in my_names and currentSpeaker in my_names:
				#I'm continuing to respond
				myBuffer += message[1] + "<<SEND>>"
			elif message[0] == otherSpeaker and currentSpeaker in my_names:
				#I'm done responding, and they are starting to speak again. 
				#Write corresponding lines to files
				try:
					with open(them_data_path, 'a') as themFile, open(me_data_path, 'a') as meFile:
						themFile.write(theirBuffer.strip() + "\n")
						meFile.write(myBuffer.strip() + "\n")
				except:
					print "=========================="
					print theirBuffer
					print "--------------------------"
					print myBuffer


				#Empty out the buffers
				myBuffer = theirBuffer = ''
				#Update to who is now speaking
				currentSpeaker = message[0]
				theirBuffer += message[1] + "<<SEND>>"
			else:
				#Failed to fit any of the cases, attempt to debug
				print "I can't follow this"
				import pdb; pdb.set_trace()

def generate_vocabulary_files():
	pass

if __name__ == '__main__':
	lp = LogParser()

	for root, dirs, files in os.walk(log_dir):
	 	for file in files:
	 		splitDir = root.split('/')
	 		me = splitDir[-2]
	 		them = splitDir[-1]

	 		#Remove multi-user chats
	 		if them.endswith(".chat"):
	 			continue
	 		elif them in ignore_users:
	 			continue
	 		else:
	 			lp.parse(os.path.join(root, file))
	 			convo = lp.getData()
	 			if convo is not None:
		 			if len(convo["participants"]) != 2:
		 				#We only want conversations between two participants
		 				continue
		 			#Now we're getting somewhere. 
		 			generate_training_data(convo, my_names)


	 