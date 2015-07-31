# coding: utf-8
import objc
reload(objc)
from objc import *
import ui,console


w=ObjCClass('UIApplication').sharedApplication().keyWindow()
main_view=w.rootViewController().view()
      
def get_toolbar(view):
   #get main editor toolbar, by recursively walking the view
   sv=view.subviews()
   
   for i in range(sv.count()-1):
      v=sv.objectAtIndex_(ns(i))
      if v._get_objc_classname()=='OMTabViewToolbar':
         return v
      tb= get_toolbar(v)
      if tb:
         return tb
         
tb=get_toolbar(main_view)
execbtn=ui.Button(frame=(tb.size().width-tb.rightItemsWidth()-40,22,40,40))
execbtn.flex='R'
execbtn.image=ui.Image.named('iow:ios7_play_32')
execbtn_obj=ObjCInstance(execbtn._objc_ptr)
tb.addSubview_(execbtn_obj)

def run_script(sender):
   import editor
   execfile(editor.get_path())
execbtn.action=run_script

#hang onto these objects
import imp
keep=imp.new_module('keep')
keep.execbtn=execbtn
sys.modules['keep']=keep