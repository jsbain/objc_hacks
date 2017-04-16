
import sys
try:
	from . import swizzle
except:
	import swizzle
from objc_util import *
import ctypes
from ctypes import *
from objc_util import _block_descriptor
import logging
import ui
logger = logging.getLogger('completion')
if not logger.handlers:
	hdlr = logging.FileHandler('completion.txt','w')
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr) 
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
logger.info('logging started')

from threading import Lock

CompletionImpType=CFUNCTYPE(None, c_void_p,c_short,c_void_p)

class completion_block_literal(Structure):
		_fields_ = [('isa', c_void_p), ('flags', c_uint), ('reserved', c_int), ('invoke', CompletionImpType), ('descriptor', _block_descriptor)]
from objc_util import parse_types
c._Block_layout.restype=c_void_p
c._Block_layout.argtypes=[c_void_p]
c._Block_extended_layout.restype=c_void_p
c._Block_extended_layout.argtypes=[c_void_p]
c._Block_signature.restype=c_char_p
c._Block_signature.argtypes=[c_void_p]

c._Block_copy.argtypes=[c_void_p]
c._Block_copy.restype=c_void_p

class Suggestion(dict):
	def __init__(self,casematches=True,fuzzy=False,isFuzzy=False,isKeyword=False,matchedRanges=0,name='apparent_endoding',rank=0,typ='function',underscores=False):
		
		self.update(
			{'caseMatches':casematches, 
			'fuzzy':fuzzy, 
			'isFuzzy':isFuzzy,    
			'isKeyword':isKeyword,    
			'matchedRanges':ObjCClass('NSMutableIndexSet').indexSetWithIndex_(matchedRanges),
			'name': name ,
			'rank':rank,
			'type': typ,
			'underscores': underscores})
import rlcompleterjb
import ui,time
def complete_later(blk,_requestid):
	ui.cancel_delays()
	blkcopy=c._Block_copy(c_void_p(blk))
	logger.debug(blk,blkcopy)
	b=cast(blkcopy,POINTER(completion_block_literal)).contents		
	
	s=Suggestion(matchedRanges=0, 
								name='poop')
	s2=Suggestion(matchedRanges=0, 
								name='pooperiffic')
	@ui.in_background
	def invoke():
		time.sleep(2)
		completiondictlist=ns([s,s2])
		on_main_thread(
		b.invoke)(c_void_p(blkcopy),c_short(_requestid),completiondictlist)
	#ui.delay(invoke,0.05)
	invoke()
		

comp=rlcompleterjb.Completer()
def complete(txt,_self):
	if txt:
		i=0
		matches=[]
		#matchRanges=ObjCInstanceMethod(ObjCInstance(_self), 'matchedRangesForPattern:inString:')
		while True:
			name=comp.complete(txt,i)
			i+=1
			if not name:
				return matches
			#ranges=matchRanges(name,txt)
			#logger.info(ranges)
			matches.append(
				Suggestion(matchedRanges=0, 
								name=name,
								underscores=('._' in name)))

def suggestCompletionsForPosition_inTextView_requestID_completion_(_self,_sel,position, tv, requestid, completion):
	with Lock():
		logger.debug('# # # # # suggestCompletion called # # # # #')
		def completion_block(_cmd,_requestid,completiondict):
			with Lock():
				try:
					logger.debug('    compl({},{})'.format(requestid,list(ObjCInstance(completiondict))))
					b=cast(completion,POINTER(completion_block_literal)).contents
					logger.debug(b.flags)
					b.invoke(c_void_p(completion),c_short(_requestid),c_void_p(completiondict))
				except Exception as e:
					logger.error(e)
					logger.error(e.__traceback__)
		blk=ObjCBlock(completion_block,
			restype=None,
			argtypes=[c_void_p, c_int, c_void_p])
		#originalmethod=ObjCInstanceMethod(ObjCInstance(_self), 'original'+'suggestCompletionsForPosition:inTextView:requestID:completion:')
		#logger.debug('   calling orig({},{},{},{})'.format(position, cast(tv,c_void_p), requestid,cast(completion,c_void_p)))
		#originalmethod(position, cast(tv,c_void_p), requestid,blk)
		#sugg=ns([Suggestion(),])
		
		if 0:
			sugg=ns(complete(str(ObjCInstance(tv).text())[0:position], c_void_p(_self)))
			if sugg:
				completion_block(completion,requestid, sugg.ptr)
		else:
			complete_later(completion,requestid)
		logger.debug('   done orig')
swizzle.swizzle(ObjCClass('PA2ConsoleCompletionProvider'),'suggestCompletionsForPosition:inTextView:requestID:completion:'
,suggestCompletionsForPosition_inTextView_requestID_completion_,type_encoding=None,debug=True)

def matchedRangesForPattern_inString_(_self,_sel,pattern, string):
	with Lock():
		#logger.debug(NSThread.currentThread())
		try:
			#logger.debug('     pattern: {}  string:{}'.format(ObjCInstance(pattern), ObjCInstance(string)))
			originalmethod=ObjCInstanceMethod(ObjCInstance(_self), 'original'+'matchedRangesForPattern:inString:')
			returnval= originalmethod(c_void_p(pattern),c_void_p(string))
			return returnval.ptr
		except Exception as e:
			logger.error(e)
			return None
			
#swizzle.swizzle(ObjCClass('PA2ConsoleCompletionProvider'),	'matchedRangesForPattern:inString:',	matchedRangesForPattern_inString_,	type_encoding=None,debug=True)


import requests
req=requests.get('http://google.com')
