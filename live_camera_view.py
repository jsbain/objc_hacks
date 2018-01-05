# coding: utf-8
from objc_util import *
import ui
AVCaptureStillImageOutput=ObjCClass('AVCaptureStillImageOutput')


class LiveCameraView(ui.View):
   ''' device=1== front, device=2==back
   image_capture_handler= callable fcn(sender)
      gets called once image is captured, and stored in .image attribute
   '''
   def __init__(self,device=1, capture_handler=None, *args, **kwargs):
      ui.View.__init__(self,*args,**kwargs)
      self._session=ObjCClass('AVCaptureSession').alloc().init()
      self._session.setSessionPreset_('AVCaptureSessionPresetHigh');
      inputDevices=ObjCClass('AVCaptureDevice').devices()
      self._inputDevice=inputDevices[device]
      deviceInput=ObjCClass('AVCaptureDeviceInput').deviceInputWithDevice_error_(self._inputDevice, None);
      if self._session.canAddInput_(deviceInput):
         self._session.addInput_(deviceInput)
      #stillSettings = [AVVideoCodecJPEG:AVVideoCodecKey]
      self._stillImageOutput=AVCaptureStillImageOutput.new()
      # .outputSettings = stillSettings
      if(self._session.canAddOutput_(self._stillImageOutput)):
         self._session.addOutput_(self._stillImageOutput)


      self._previewLayer=ObjCClass('AVCaptureVideoPreviewLayer').alloc().initWithSession_(self._session)
      self._previewLayer.setVideoGravity_( 
         'AVLayerVideoGravityResizeAspectFill')
      rootLayer=ObjCInstance(self).layer()
      rootLayer.setMasksToBounds_(True)
      self._previewLayer.setFrame_(
         CGRect(CGPoint(0, 0), CGSize(self.width,self.height)))
      rootLayer.insertSublayer_atIndex_(self._previewLayer,0)

      self._previewLayer.connection().videoOrientation=      ObjCClass('UIDevice').currentDevice().orientation()
      self._session.startRunning()
      b=ui.Button(image=ui.Image.named('iow:ios7_camera_outline_32'))
      self.add_subview(b)
      self.capture_handler=capture_handler
      b.action=self.capture_photo
      self._handler_blk=ObjCBlock(self.handler,restype=None,argtypes=[c_void_p, c_void_p, c_void_p])
   def will_close(self):
      self._session.stopRunning()
      print('closed')
   def layout(self):
      self._previewLayer.connection().videoOrientation=      ObjCClass('UIDevice').currentDevice().orientation()
      self._previewLayer.setFrame_(
         CGRect(CGPoint(0, 0), CGSize(self.width,self.height)))
      if not self._session.isRunning():
         self._session.startRunning()
   def handler(self,_blk,buff,err):
         data=ObjCInstance(buff)
         imageData = AVCaptureStillImageOutput.jpegStillImageNSDataRepresentation_(data)
         image = ui.Image.from_data(nsdata_to_bytes(imageData))
         self.image=image
         if callable(self.capture_handler):
            self.capture_handler(self)
   def capture_photo(slf,sender):
      self=sender.superview
      connection = self._stillImageOutput.connectionWithMediaType('vide')

      self._stillImageOutput.captureStillImageAsynchronouslyFromConnection(
         connection, 
         completionHandler=self._handler_blk
         )
      
if __name__=='__main__':
   blueview=ui.View(bg_color='blue',frame=(0,0,576,576))
   b1=ui.Button(title='take photo')
   blueview.add_subview(b1)
   shield=ui.View(frame=blueview.bounds)
   blueview.add_subview(shield)
   shield.hidden=True
   shield.bring_to_front()
   iv=ui.ImageView(frame=(100,100,200,200))
   blueview.add_subview(iv)
   def take_photo(sender):     
      def cont(sender):
         #stuff to do once image is taken
         camera.will_close() #stop session
         shield.hidden=True
         shield.remove_subview(camera)
         iv.image=camera.image
      shield.hidden=False
      camera=LiveCameraView(frame=(0,0,400,400),capture_handler=cont)
      shield.add_subview(camera)
      camera.layout() #force orientation
   b1.action=take_photo
   blueview.present('sheet')
   blueview.wait_modal()

