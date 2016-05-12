#!python3
print('#########')
import sys, os
import tableview_rowheight, ui, objc_util,swizzle
def relpath(path):
   return path[path.find('Pythonista'):]
# first, make aure we have the right versions of all files
print (relpath(__file__))
print (relpath(tableview_rowheight.__file__))
print (relpath(swizzle.__file__))
print (relpath(ui.__file__))
print (relpath(objc_util.__file__))

v=ui.View(frame=(0,0,200,320))
t=ui.TableView(frame=(0,0,200,320))
v.add_subview(t)
d=ui.ListDataSource([str(x) for x in range(100)])
t.data_source=t.delegate=d
to=objc_util.ObjCInstance(t)
# first, lets check we have the right objects
print(to) 
print(d)
print(to.tableView_heightForRowAtIndexPath_) 
print(t.row_height)
print (to.rowHeight())
to.estimatedRowHeight=44
NSIndexPath=objc_util.ObjCClass('NSIndexPath')
path=NSIndexPath.indexPathForRow_inSection_(0,0)
print('no delegate yet: should return -1')
print(to.tableView_heightForRowAtIndexPath_(to,path))
t.row_height=24
print('no delegate yet: should return 24')
print(to.tableView_heightForRowAtIndexPath_(to,path))
# next... set up delegate
@objc_util.on_main_thread
def tableview_height_for_section_row(tv,section,row):
   #print ('tableview_height_for_section_row called:',tv,section,row)
   #print(objc_util.ObjCClass('NSThread').currentThread())
   return 10+(row/5)**2 if row<50 else 10+((100-row)/5)**2

d.tableview_height_for_section_row=tableview_height_for_section_row
print(to.tableView_heightForRowAtIndexPath_(to,path))
print('make sure we can still get # rows and the actual cells')
print(to.tableView_numberOfRowsInSection_(to,0))
print(to.tableView_cellForRowAtIndexPath_(to,path))



v.present('fullscreen')
