from objc_util import *
import ui
from objc_hacks import swizzle
def tableView_heightForRowAtIndexPath_(_self,_sel,tv,path):
	# next, get the pyobject
		tv_o=ObjCInstance(_self)
		#tv_py=tv_o.pyObject(restype=ctypes.py_object,argtypes=[])
		#first, get row/section
		indexPath=ObjCInstance(path)
		row=indexPath.row()
		section=indexPath.section()
		pyo=tv_o.pyObject(restype=c_void_p,argtypes=[])
		tv_py=ctypes.cast(pyo.value,ctypes.py_object).value
		if tv_py.delegate and hasattr(tv_py.delegate,'tableview_height_for_section_row'):
			return tv_py.delegate.tableview_height_for_section_row(tv_py,section,row)
		else:
			return tv_py.row_height

# set up the swizzle.. only needs to be do e once
def setup_tableview_swizzle():
	t=ui.TableView()
	t_o=ObjCInstance(t)
	if hasattr(t_o,'tableView_heightForRowAtIndexPath_'):
		return
	swizzle.swizzle(ObjCClass(t_o._get_objc_classname()),
								('tableView:heightForRowAtIndexPath:'),
								tableView_heightForRowAtIndexPath_,'f@:@@')



setup_tableview_swizzle()								

#create tableview and delegate
t=ui.TableView()
t.frame=(0,0,200,576)
d=ui.ListDataSource([str(x) for x in range(100)])
t.data_source=d
t.delegate=d

# create custom height callback, add to delegate.  
import random
heights=[random.randrange(11,72) for x in range(100)]
def tableview_height_for_section_row(tv,section,row):
	return heights[row]
d.tableview_height_for_section_row=tableview_height_for_section_row

# add an estimatedRowHeight. this is optional, but in theory improves performance
t_o=ObjCInstance(t)
t_o.estimatedRowHeight=44

t.present('sheet')
