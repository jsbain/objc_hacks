# coding: utf-8
# coding: utf-8
# experiments with attributed strings

from objc import *
import ctypes

NSMutableAttributedString=ObjCClass('NSMutableAttributedString')
NSFontAttributeName=ns('NSFont')
UIFont=ObjCClass('UIFont')


import ui
v=ui.View(frame=(0,0,576,576),bg_color=(0.7,)*3)
txtsize=ui.Slider(bg_color=(1,1,1),frame=(0,50,300,50))
def slideraction(sender):
   d=NSMutableDictionary.new()
   sz=round(6+sender.value*72.0)
   f=UIFont.systemFontOfSize_(sz)
   d.setValue_forKey_(f,NSFontAttributeName)
   lblobj.setTypingAttributes_(d)
   txtsizelbl.text='FontSize={}'.format(sz)
txtsize.action=slideraction
txtsizelbl=ui.Label(frame=(0,0,300,20))

v.add_subview(txtsize)
v.add_subview(txtsizelbl)
lbl=ui.TextView(bg_color='white',frame=(0,150,300,300))
lbl.text='type here'
txtsizelbl.text='Font size={}'.format(lbl.font[1])
txtsize.value=(lbl.font[1]-6)/72.0
v.add_subview(lbl)
v.present('sheet')
lblobj=ObjCInstance(lbl._objc_ptr)
