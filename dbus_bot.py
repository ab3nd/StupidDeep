'''
Created on Nov 18, 2011
Watches pidgin over Dbus and responds to incoming messages. 
'''

import dbus 
import util
from dbus.mainloop.glib import DBusGMainLoop
import gobject
from pickle import Unpickler
import random
import re

class StupidResponder():
    def __init__(self):
        #Load the file of all conversations
        inFile = open("./all_convos.pickle")
        all_convos = Unpickler(inFile).load()
        self.callResp = {}
        
        #Build a dictionary of what they said and my response
        for convo in all_convos:
            for ii in range(0, len(convo)-2):
                if not util.isMe(convo[ii][0]) and util.isMe(convo[ii+1][0]):
                    #Found a pair of lines with their line and my response
                    call = convo[ii][1].lower()
                    call = util.cleanRefs(call)
                    response = convo[ii+1][1]
                    if(len(call.split()) < 5):
                        if not call in self.callResp.keys():
                            self.callResp[call] = [util.cleanRefs(response)]
                        else:
                            self.callResp[call].append(util.cleanRefs(response))

    def getResponse(self, message):
        #Clean up to match keys
        message = message.lower()
        message = re.sub("<[^>]*>", "", message)
        message = util.cleanRefs(message)
        #Return random message
        if message in self.callResp.keys():
            return random.choice(self.callResp[message])
        #No idea what to say
        #return "Insect! I cannot bear your words! They are TOO TINY!"
        return None
        
    
    
def got_msg_cb(account, sender, message, conversation, flags):
    reply = responder.getResponse(message)
    if reply != None:
        purple.PurpleConvImSend(purple.PurpleConvIm(conversation), reply)


if __name__ == '__main__':
    
    #load a response generator
    responder = StupidResponder()
    
    #Connect to pidgin on Dbus
    main_loop = DBusGMainLoop()
    session_bus = dbus.SessionBus(mainloop = main_loop)
    obj = session_bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
    purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")

    #Add the callback
    session_bus.add_signal_receiver(got_msg_cb, dbus_interface="im.pidgin.purple.PurpleInterface", signal_name="ReceivedImMsg")
    
    #Listen
    loop = gobject.MainLoop()
    loop.run()