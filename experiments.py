# coding: utf-8
# experiments with gestureRecognizers
#. note this code may not work with 64bit code, due to bool encoding
import ui
from objc import *
import weakref


# Create a new Objective-C class to act as the gesturerecognizer delegate...
try:
   # If the script was run before, the class already exists.
   GRDelegate = ObjCClass('GRDelegate')
except:
   IMPTYPE = ctypes.CFUNCTYPE(c_char, c_void_p, c_void_p, c_void_p,c_void_p)
   def gestureRecognizer_shouldRecognizeSimultaneouslyWithGestureRecognizer_imp(self, cmd, gr, other_gr):
      return chr(1)
     
   imp = IMPTYPE(gestureRecognizer_shouldRecognizeSimultaneouslyWithGestureRecognizer_imp)
   # This is a little ugly, but we need to make sure that `imp` isn't garbage-collected:
   ui._retain_gr_delegate = imp
   NSObject = ObjCClass('NSObject')
   class_ptr = c.objc_allocateClassPair(NSObject.ptr, 'GRDelegate', 0)
   selector = sel('gestureRecognizer:shouldRecognizeSimultaneouslyWithGestureRecognizer:')
   c.class_addMethod(class_ptr, selector, imp, 'c0@0:0@0@0')
   c.objc_registerClassPair(class_ptr)
   GRDelegate = ObjCClass('GRDelegate')


class PinchView(ui.View):
   def __init__(self, *args, **kwargs):
      ui.View.__init__(self, *args, **kwargs)
      self.pinchgesture_recognizer_target = ui.Button()
      self.pinchgesture_recognizer_target.action = self.did_pinch
      
      self.pangesture_recognizer_target = ui.Button()
      self.pangesture_recognizer_target.action = self.did_pan
      
      self.gr_delegate=GRDelegate.alloc().init().autorelease()
      self.recognizers={}
      self_objc = ObjCInstance(self)     
      pinchobjctarget=ObjCInstance(self.pinchgesture_recognizer_target._objc_ptr)
      panobjctarget=ObjCInstance(self.pangesture_recognizer_target._objc_ptr)
 
      pinchrecognizer = ObjCClass('UIPinchGestureRecognizer').alloc()
      self.recognizers['pinch'] =         pinchrecognizer.initWithTarget_action_( pinchobjctarget, sel('invokeAction:')).autorelease()

      
      panrecognizer = ObjCClass('UIPanGestureRecognizer').alloc()
      self.recognizers['pan'] =            panrecognizer.initWithTarget_action_( panobjctarget, sel('invokeAction:')).autorelease()
      self.recognizers['pan'].setMinimumNumberOfTouches_(ctypes.c_uint(2))
      
      for r in self.recognizers.values():
         self_objc.addGestureRecognizer_(r)
         r.setDelegate_(self.gr_delegate)

   def did_pan(self,sender):
      state=self.recognizers['pan'].state()
      pan=self.recognizers['pan'].translationInView_( self.recognizers['pan'].view())
      panx=pan.x
      pany=pan.y
      print 'pan',panx,pany,state

   def did_pinch(self,sender):
      print 'pinch'
      state=self.recognizers['pinch'].state()
      scale=self.recognizers['pinch'].scale()
      if state==1:
         self.scale_began(scale)
      elif state==2:
         self.scale_changed(scale)
      else:# state==3:
         self.scale_ended(scale)

   def scale_began(self,scale):
      self_objc = ObjCInstance(self)
      touches=[ self.recognizers['pinch'].locationOfTouch_inView_( ctypes.c_uint(i), self.recognizers['pinch'].view() ) for i in (0,1)]
      dx=abs(touches[0].x-touches[1].x)
      dy=abs(touches[0].y-touches[1].y)
      if dy>3.0*dx:
         #vert
         pass
      elif dx>3.0*dy:
         #horiz
         pass
      else:
         pass

   def scale_changed(self,scale):
      self_objc = ObjCInstance(self)
      touches=[ self.recognizers['pinch'].locationOfTouch_inView_( ctypes.c_uint(i), self.recognizers['pinch'].view() ) for i in (0,1)]
      dx=abs(touches[0].x-touches[1].x)
      dy=abs(touches[0].y-touches[1].y)
      if dy>3.0*dx:
         #vert
         pass
      elif dx>3.0*dy:
         #horiz
         pass
      else:
         pass
   def scale_ended(self,scale):
      print 'pinch end'
v=ui.View(frame=(0,0,400,400))
p=PinchView(frame=(0,0,400,400))
v.add_subview(p)
v.present('sheet')