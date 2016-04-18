#!/usr/bin/python
'''
Created on Nov 18, 2011
Watches pidgin over Dbus and responds to incoming messages. 
'''

import dbus 
from dbus.mainloop.glib import DBusGMainLoop
import gobject
from pickle import Unpickler
import random
import re

aliases = ["Me", "orphrey@gmail.com/[A-F0-9]{8}", "ab3nd", "honest.abe.robot@gmail.com/[A-F0-9]{8}"]

def isMe(name):
    for alias in aliases:
        if re.match(alias, name):
            return True
    return False


class StupidResponder():
    def __init__(self):
        #This is where you'd load the model and whatnot. 
        pass

    def getResponse(self, message):
        #No idea what to say
        return "Insect! I cannot bear your words! They are TOO TINY!"
    
    
def got_msg_cb(account, sender, message, conversation, flags):
    print sender
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