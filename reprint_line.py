from objc_util import *
app=UIApplication.sharedApplication()
rootVC = app.keyWindow().rootViewController()
cvc=rootVC.accessoryViewController().consoleViewController()
tv=cvc.view().subviews()[0]
ts=tv.textStorage()
@on_main_thread
def reprint_line(text):
	end_char=ts.length()
	r=ts.paragraphRangeForCharacterRange_(NSRange(end_char-1))
	p= ts.paragraphs()[r.location-1]
	ts.replaceCharactersInRange_withString_(p.range(),ns(text+'\n'))
	tv.setNeedsLayout()
if __name__=='__main__':
	import time,console
	console.clear()
	print('Starting download')
	print('downloading')
	for i in range(0,100,10):
		time.sleep(0.5)
		p=reprint_line('downloading {}%'.format(i))
	reprint_line('Complete!')

