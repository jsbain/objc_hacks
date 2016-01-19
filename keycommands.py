# coding: utf-8
from objc_util import *

c.method_setImplementation.restype = c_void_p
c.method_setImplementation.argtypes = [c_void_p, c_void_p]


c.method_getImplementation.restype = c_void_p
c.method_getImplementation.argtypes = [c_void_p]


app=ObjCClass('UIApplication').sharedApplication()
UIKeyCommand=ObjCClass('UIKeyCommand')
keycommands=list(app.keyCommands())

# create button handler to encapsulate the action
def __myaction(sender):
	print 'hi'	
__btn=ui.Button()
__btn.action=__myaction
btnobj=ObjCInstance(__btn)

#create a new keyCommand---command-h
# and append to keycommands
UIKeyModifierCommand=1<<20
mykey=UIKeyCommand.alloc().initWithInput_modifierFlags_action_(
					'h',UIKeyModifierCommand,btnobj.invokeAction_.method)
keycommands.append(mykey)
__keycommands_obj=ns(keycommands)

#create replacement implementation
def replacement_keyCommands(_self,_cmd):
		return __keycommands_obj.ptr
replacement=create_objc_class('replacement',
											ObjCClass('UIResponder'),			
											[replacement_keyCommands])
replacement_obj=replacement.new()
newimp=c.method_getImplementation(replacement_obj.keyCommands.method)
oldimp=c.method_setImplementation(app.keyCommands.method,newimp)