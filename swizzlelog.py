
import sys
try:
	from . import swizzle
except:
	import swizzle
from objc_util import *
import ctypes
from ctypes import cast, POINTER, c_int, CFUNCTYPE
import logging
from objc_util import _block_descriptor

logger = logging.getLogger('swizzle')
if not logger.handlers:
	hdlr = logging.FileHandler('swizzlelog.txt','w')
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)
logger.debug('logging started')
def swizzlenop(cls,method):	
	'''unswizzles instance method of cls to print args, then call original.
	cls is an ObjCClass.    method is selector name, including :'s
	'''
	from objc_util import ObjCInstance,parse_types
	def swizzled(self,sel,*args):
		return None
	swizzle.swizzle(cls,method,swizzled)
from threading import Lock

def clsptr(c):
   try:
      return ObjCClass(c).ptr
   except:
      return None
allclasses=[clsptr(c) for c in ObjCClass.get_names()]
def isclass(obj):
	ptr=ctypes.cast(obj,ctypes.POINTER(c_int))
	if ptr[0] in allclasses:
		return True
def swizzlelog(cls,method):	
	'''swizzles instance method of cls to print args, then call original.
	cls is an ObjCClass.    method is selector name, including :'s
	'''
	from objc_util import ObjCInstance,parse_types
	import time,ui
	logger.debug('{} swizzled'.format(method))
	def swizzled(self,sel,*args):
		with Lock():
			logger.debug('# # # # # {} # # # # #'.format(method))
			logger.debug('   self:{}'.format(self))			
			logger.debug('   args:{}'.format(args))
			argtypes=parse_types(
				ObjCInstanceMethod(
					ObjCInstance(self), 
					method).encoding
					)[1][2:]
			newargs=[]
			argidx=0
			for a,ty in zip(args,argtypes):
				argidx+=1
				if a is not None and ty is c_void_p:
					logger.debug('    {}\n       {}\n      {}'.format(argidx,ObjCInstance(a),ty))
					newargs.append(ObjCInstance(a))
				elif a is not None and ty is ObjCBlock:
					def block_logger(_cmd,requestid,matches):
						logger.debug('__logger_block: call to {}({}). args: {}, {}'.format(ObjCInstance(a),_cmd,requestid,matches))

						#logger.debug('{}'.format(signature))
						#invoke=cast(bb.ptr,POINTER(block_literal)).contents.invoke
						#invoke(_cmd, requestid, matches)
					blk=ObjCBlock(block_logger, restype=None,argtypes=[c_void_p, c_int,c_void_p])
					newargs.append(blk)
				else:
					logger.debug('    {}\n       {}\n     {}'.format(argidx,(a),ty))
					#ui.delay(p,1)
					newargs.append(a)
			selfinstance=ObjCInstance(self)
			logger.debug(('self=',selfinstance))
			try:
				originalmethod=ObjCInstanceMethod(ObjCInstance(self), 'original'+method)
				#logger.debug(originalmethod)
			except AttributeError:
				import console
				console.hud_alert(method)
				logger.debug('     attrib error, returning none')
				return None
			if originalmethod:
				logger.debug(('     newargs',newargs))
				returnval=originalmethod(*newargs)
				logger.debug(('  =====>',returnval))
			if isinstance(returnval,ObjCInstance):
				return returnval.ptr
			else:
				return returnval
	swizzle.swizzle(cls,method,swizzled,type_encoding=None,debug=True)
def unswizzle(cls,method):
	swizzle.unswizzle(cls,method)
def is_swizzled(cls,method):
	return swizzle.is_swizzled(cls,method)
unswizzle=swizzlenop
	
	
#swizzlelog(ObjCClass("OMProgressHUD_PY3"),'showWithMessage:icon:duration:blockInteraction:')
#swizzlelog(ObjCClass('PA3PythonInterpreter'),'runScriptWithOptions:')
#swizzlelog(ObjCClass('PA3PythonInterpreter'),'runScriptWithFileAtPath_argv:')
#I2=ObjCClass('PA3PythonInterpreter').sharedInterpreter()
'''I2.runScriptWithOptions_(({ 'captureExceptions':0,
								'script':'print sys.argv[1:]\n',
								'scriptPath':"<string>",
								'argv':ns(['hello'])}))
								'''
