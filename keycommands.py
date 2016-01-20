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
def handleCommandH(_cmd,_sel):
	print 'hi'	
CmdHHandler=create_objc_class('CmdHHandler',
											ObjCClass('UIResponder'),			
											[handleCommandH])
CmdHHandler_obj=CmdHHandler.new()
CmdHHandler_imp=c.method_getImplementation(CmdHHandler_obj.handleCommandH.method)
class_addMethod(UIApplication.ptr,sel('handleCommandH'),CmdHHandler_imp,'v@:')


#create a new keyCommand---command-h
# and append to keycommands
UIKeyModifierCommand=1<<20
mykey=UIKeyCommand.keyCommandWithInput_modifierFlags_action_(
																				'h',UIKeyModifierCommand,
																				sel('handleCommandH'))
keycommands.append(mykey)
__keycommands_obj=ns(keycommands)


#create replacement implementation
#   in ios9 this can maybe use addKeyCommand instead of swizzling
#   note __keycommands_obj must hang around in globals, there is probably a more robust way to do this.  
def replacement_keyCommands(_self,_cmd):
		return __keycommands_obj.ptr
replacement=create_objc_class('replacement',
											ObjCClass('UIResponder'),			
											[replacement_keyCommands])
replacement_obj=replacement.new()
newimp=c.method_getImplementation(replacement_obj.keyCommands.method)
oldimp=c.method_setImplementation(app.keyCommands.method,newimp)

print 'testing if keycommand was added'
assert(sel_getName(app.keyCommands()[-1].action())=='handleCommandH') #was key added?
print 'testing that action was added'
assert(hasattr(app,'handleCommandH'))
print 'testing action:'
app.handleCommandH()
