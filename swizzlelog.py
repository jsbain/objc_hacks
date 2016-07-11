
import sys
try:
	from . import swizzle
except:
	import swizzle
from objc_util import *
def swizzlenop(cls,method):	
	'''swizzles instance method of cls to print args, then call original.
	cls is an ObjCClass.    method is selector name, including :'s
	'''
	from objc_util import ObjCInstance,parse_types
	def swizzled(self,sel,*args):
		return None
	swizzle.swizzle(cls,method,swizzled)

def swizzlelog(cls,method):	
	'''swizzles instance method of cls to print args, then call original.
	cls is an ObjCClass.    method is selector name, including :'s
	'''
	from objc_util import ObjCInstance,parse_types
	import time
	def swizzled(self,sel,*args):
		print('{}:{} called'.format(time.ctime(),method))
		print (args)
		argtypes=parse_types(ObjCInstanceMethod(ObjCInstance(self), method).encoding)[1][2:]
		newargs=[]
		for a,ty in zip(args,argtypes):
			if a is not None and ty is c_void_p:
				print (ObjCInstance(a))
				newargs.append(ObjCInstance(a))
			else:
				print(a)
				newargs.append(a)
		return ObjCInstanceMethod(ObjCInstance(self), 'original'+method)(*newargs)
	swizzle.swizzle(cls,method,swizzled,type_encoding=None,debug=True)
def unswizzle(cls,method):
	swizzle.unswizzle(cls,method)
def is_swizzled(cls,method):
	return swizzle.is_swizzled(cls,method)
	
	
	
#swizzlelog(ObjCClass("OMProgressHUD_PY3"),'showWithMessage:icon:duration:blockInteraction:')
#swizzlelog(ObjCClass('PA3PythonInterpreter'),'runScriptWithOptions:')
#swizzlelog(ObjCClass('PA3PythonInterpreter'),'runScriptWithFileAtPath_argv:')
#I2=ObjCClass('PA3PythonInterpreter').sharedInterpreter()
'''I2.runScriptWithOptions_(({ 'captureExceptions':0,
								'script':'print sys.argv[1:]\n',
								'scriptPath':"<string>",
								'argv':ns(['hello'])}))
								'''
