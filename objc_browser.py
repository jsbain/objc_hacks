''' a ui browser for objc classes and methods.
	design: tableview, typing in search filters in real time
	select row: nav view push a new methodBrowser
	
	then dig deeper.
	when selecting a class, show methods
	select a method: install swizzle
	
	TODO: indicate when a method is swizzled
	'''
from objc_util import *
import ui
try:
	from . import swizzlelog
except:
	import swizzlelog

class table_browser(ui.View):
	def __init__(self,items, *args,**kwargs):
		ui.View.__init__(self,*args,**kwargs)
		self.height=700
		self.width=320
		self.items=items
		self.tv=ui.TableView(frame=self.bounds)
		self.tv.delegate=self
		self.tv.data_source=self
		self.add_subview(self.tv)
		self.filter=''
		self.filtereditems=[x for x in self.items if self.filter in x.lower()]
	def tableview_number_of_rows(self, tv, section):
		return len(self.filtereditems)

	def tableview_cell_for_row(self,tv,section,row):
		cell=ui.TableViewCell()
		cell.accessory_type='disclosure_indicator'
		cell.text_label.text=self.filtereditems[row]
		return cell

class class_browser(table_browser):
	def __init__(self,items=ObjCClass.get_names(''), *args,**kwargs):
		table_browser.__init__(self,items,*args,**kwargs)
		self.nv=ui.NavigationView(self)
		self.nv.frame=self.frame
		#self.nv.push_view(self.tv)
		self.nv.navigation_bar_hidden=True
		self.tv.y+=40
		self.tv.height-=40
		self.sb=ui.View(frame=(0,0,320,40),bg_color=(0.75,.75,.75))
		self.s=ui.TextField(frame=(20,4,280,32),bg_color='red')
		self.sb.add_subview(self.s)
		self.add_subview(self.sb)
		#self.s=ObjCClass('UISearchBar').alloc().init()
		#ObjCInstance(self.tv).tableHeaderView = ObjCInstance(self.sb)
		self.s.delegate=self
		self.s.corner_radius=16
		self.s.bg_color=(.9,.9,.0)
		self.s.border_color=(0,0,0)
		self.s.placeholder='\U0001F50E Search'
		ObjCInstance(self.s)
	def textfield_did_change(self,textfield):
		self.filter=textfield.text.lower()
		self.filtereditems=[x for x in self.items if self.filter in x.lower()]
		self.tv.reload()
	def textfield_did_begin_editing(self,textfield):
		self.nv.navigation_bar_hidden=True
	def tableview_number_of_sections(self,tv):
		self.nv.navigation_bar_hidden=True
	def tableview_did_select(self,tv,section,row):
			py_methods=[]
			self.nv.navigation_bar_hidden=False
			objc_class_ptr=ObjCClass(self.filtereditems[row]).ptr
			num_methods = c_uint(0)
			method_list_ptr = c.class_copyMethodList(objc_class_ptr, byref(num_methods))
			for i in range(num_methods.value):
				selector = c.method_getName(method_list_ptr[i])
				sel_name = c.sel_getName(selector)
				if not isinstance(sel_name,str):
					sel_name = sel_name.decode('ascii')
				py_method_name = sel_name
				if '.' not in py_method_name:
					py_methods.append(py_method_name)
			c.free(method_list_ptr)
			m=method_browser(items=py_methods,name=self.filtereditems[row])
			import clipboard,console
			clipboard.set('ObjCClass("'+self.filtereditems[row]+'")')
			console.hud_alert('{} copied to clipboard'.format(clipboard.get()))
			m.x=self.width
			def slide():
				m.x=0
			self.nv.push_view(m)	
			#3ui.animate(slide,.2)
class method_browser(table_browser):
	def _init__(self,items,classname):
		table_browser.__init__(self,items)
		self.right_button_items=[ui.ButtonItem()]
		self.right_button_items[0].title='blah'
	def tableview_did_select(self,tv,section,row):
		import clipboard
		import console

		methodname=self.items[row]

		clipboard.set(methodname)		
		swizzlelog.swizzlelog(ObjCClass(self.name), methodname)

		console.hud_alert('{} copied to clipboard, and swizzle installed'.format(methodname))
		tv.reload()
	def tableview_can_delete(self, tableview, section, row):
		methodname=self.items[row]
		if 'original'+methodname in self.items:
			return True
	def tableview_cell_for_row(self,tv,section,row):
		cell=ui.TableViewCell()
		cell.accessory_type='disclosure_indicator'
		methodname=self.items[row]
		cell.text_label.text=methodname
		if swizzlelog.is_swizzled(ObjCClass(self.name),	methodname):	
			cell.text_label.text_color='red'
		return cell
	def tableview_delete(self, tv, section, row):
		methodname=self.items[row]
		# hmm... this does not seem to really work
		swizzlelog.unswizzle(ObjCClass(self.name),	methodname)
		import console
		console.hud_alert('{} unswizzled swizzle'.format(methodname))
		tv.reload()
v=class_browser()
vv=ui.View()

v.nv.present('sheet')


