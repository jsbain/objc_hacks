''' Set system wide gamma
Based in large part on https://github.com/thomasfinch/GammaThingy

Use at your own risk!  A reset should clear out a bad gamma setting.  
Do not delete the gamma file until gamma has been reset to default, otherwise
this script will be unable to achieve default gamma

'''
from objc_util import *
from ctypes import *
import os

# setup api calls
c.IOMobileFramebufferGetMainDisplay
c.IOMobileFramebufferGetMainDisplay.argtypes=[POINTER(c_int)]
c.IOMobileFramebufferGetMainDisplay.restype=c_int

c.IOMobileFramebufferGetGammaTable
c.IOMobileFramebufferGetGammaTable.argtypes=[c_int, POINTER(c_uint32)]
c.IOMobileFramebufferGetGammaTable.restype=c_int

c.IOMobileFramebufferSetGammaTable
c.IOMobileFramebufferSetGammaTable.argtypes=[c_int, POINTER(c_uint32)]
c.IOMobileFramebufferSetGammaTable.restype=c_int

# create gamma tables
data= (771*c_uint32)()
dataold= (771*c_uint32)()

#get the display, and old gamma table
connection=c_int(0)
c.IOMobileFramebufferGetMainDisplay(connection)
c.IOMobileFramebufferGetGammaTable(connection,pointer(data)[0])
c.IOMobileFramebufferGetGammaTable(connection,pointer(dataold)[0])

# if this is the first time running, save the original gamma table
if not os.path.exists('gamma'):
	#write out the file
	with open('gamma','wb') as f:
		for x in data:
			f.write(bytearray(data))
else:
	#read it back in
	with open('gamma','rb') as f:
		f.readinto(dataold)
		
def setScreenGammaTable(red=1,green=1,blue=1):
	'''set screen gamma table, using red, green and blue (floats between 0 and 1)
	This is based on GammaThingy, effectively shifts the table towards the beginning by a fractional amount for each color.
	'''
	#scale inputs to int8
	clamp = lambda n: max(min(1.0, n), 0.0)
	rs=int(255*clamp(red))
	bs=int(255*clamp(blue))
	gs=int(255*clamp(green))
	# shift original table
	for i in range(256):
		j=255-i
		r=j*rs>>8
		g=j*gs>>8
		b=j*bs>>8

		data[j + 0x001] = dataold[r + 0x001];
		data[j + 0x102] = dataold[g + 0x102];
		data[j + 0x203] = dataold[b + 0x203];
	#set the table
	c.IOMobileFramebufferSetGammaTable(connection,pointer(data)[0])
	
def resetGamma():
	'''resets gamma table back to the original'''
	c.IOMobileFramebufferSetGammaTable(connection,pointer(dataold)[0])

def _slider_action(sender):
	'''sets gamma based on slider values'''
	import ui
	if isinstance(sender,ui.Slider):
		v=sender.superview
		setScreenGammaTable(v['red'].value,v['green'].value,v['blue'].value)

def showGammaChooser():
	'''Show a popover gamma chooser'''
	import ui
	v=ui.View(frame=(0,0,210,310),bg_color='white')
	r=ui.Slider(frame=(5,5,200,44),name='red',bg_color='red')
	g=ui.Slider(frame=(5,55,200,44),name='green',bg_color='green')
	b=ui.Slider(frame=(5,115,200,44),name='blue', bg_color='blue')
	reset=ui.ButtonItem(title='reset')
	v.right_button_items=[reset]
	[v.add_subview(x) for x in (r,g,b)]
	[setattr(x,'value',1) for x in (r,g,b)]
	[setattr(x,'action',_slider_action) for x in (r,g,b)]
	def resetaction(sender):
		[setattr(x,'value',1) for x in (r,g,b)]
		resetGamma()
	reset.action=resetaction
	v.present('popover')

showGammaChooser()
