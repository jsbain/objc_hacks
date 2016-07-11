try:
	from . import swizzlelog
except:
	import swizzlelog
from objc_util import *
swizzlelog.swizzlenop(ObjCClass('OMBasicPythonCompletionProvider'),'setFallbackCompletionProvider:')
