'''Hijack the history up,button, such that long pressing shows 
the entire history in one table, rather than one line at a time.
Also adds the ability to save /load / and search history sessions.

Todo... copy multiple lines, to be able to copy a block of history to editor.

Warning: place in site-packages to avoid problems
'''
from objc_util import ObjCClass,ObjCInstance,UIApplication,NSRange,on_main_thread
import dialogs,ui,editor,os,json
HISTORY_FILE=os.path.join(os.path.dirname(__file__),'_history.json')
if not os.path.exists(HISTORY_FILE):
	with open(HISTORY_FILE,'w') as f:
		json.dump([],f)

cvc=UIApplication.sharedApplication().\
						keyWindow().rootViewController().\
						accessoryViewController().\
						consoleViewController()

def select_history(data):
	''' callback for longtap of history button.
	enumerate the console view controller's history, and present a list dialog to select.
	After the user selects a history item, write it to the console input
	'''
	if data.state==1:
		history = [str(h)[:-1] for h in cvc.history() or []]
	
		textField = cvc.promptEditorView().subviews()[0]
		
		txt = list_dialog('Select History',history)
		if txt:
			textField.text = txt
			textField.selectedRange=NSRange(len(txt),0)
class ThemedListDataSource(object):
	''' A list data source that adhere's to the current theme.
	Also, allows filtering the tableview
'''
	def __init__(self, items=None):
		self.tableview = None
		self.reload_disabled = False
		self.delete_enabled = True
		self.move_enabled = False
		self.filter=''
		self.action = None
		self.edit_action = None
		self.accessory_action = None
		
		self.tapped_accessory_row = -1
		self.selected_row = -1
		
		if items is not None:
			self.items = items
		else:
			self.items = ListDataSourceList([])
		self.text_color = None
		self.highlight_color = None
		self.font = None
		self.number_of_lines = 1
	
	def reload(self):
		if self.tableview and not self.reload_disabled:
			self.tableview.reload()
	
	@property
	def items(self):
		return self._items
	
	@items.setter
	def items(self, value):
		self._items = ui.ListDataSourceList(value, self)
		self.reload()
	
	@items.getter
	def items(self):
		'''only get fiiltered items'''
		return [i for i in reversed(self._items) if self.filter in i ]
		
	def textfield_did_change(self, textfield):
		'''callback when search field changes.  
		update filter and reload'''
		self.filter=textfield.text
		self.reload()
	def tableview_number_of_sections(self, tv):
		self.tableview = tv
		return 1
	
	def tableview_number_of_rows(self, tv, section):
		return len(self.items)
	
	def tableview_can_delete(self, tv, section, row):
		return self.delete_enabled
	
	def tableview_can_move(self, tv, section, row):
		return self.move_enabled
	
	def tableview_accessory_button_tapped(self, tv, section, row):
		self.tapped_accessory_row = row
		if self.accessory_action:
			self.accessory_action(self)
	
	def tableview_did_select(self, tv, section, row):
		self.selected_row = row
		if self.action:
			self.action(self)
	def tableview_cell_for_row(self, tv, section, row):
		item = self.items[row]
		cell = ui.TableViewCell()
		cell.text_label.number_of_lines = 0
		cell.text_label.text = str(item)
		cell.text_label.text_color =editor.get_theme_dict()['default_text']
		if self.highlight_color:
			bg_view = ui.View(background_color=self.highlight_color)
			cell.selected_background_view = bg_view
		if self.font:
			cell.text_label.font = self.font
		cell.background_color=editor.get_theme_dict()['background']
		editor.apply_ui_theme(cell,editor.get_theme_dict()['name'])
		return cell
	
class _ListDialogController (object):
	''' A copy of dialog's list dialog controller, except with the themed data source'''
	def __init__(self, title, items, multiple=False, done_button_title='Done'):
		self.items = items
		self.selected_item = None
		self.view = ui.TableView()
		ObjCInstance(self.view).estimatedRowHeight=25
		self.view.row_height=-1
		self.view.background_color=editor.get_theme_dict()['background']
		self.view.tint_color=editor.get_theme_dict()['default_text']
		self.view.separator_color=editor.get_theme_dict()['separator_line']
		self.view.name = title
		self.view.allows_multiple_selection = multiple
		if multiple:
			done_button = ui.ButtonItem(title=done_button_title)
			done_button.action = self.done_action
			self.view.right_button_items = [done_button]
		ds = ThemedListDataSource(items)
		ds.action = self.row_selected
		self.view.data_source = ds
		self.view.delegate = ds
		self.view.frame = (0, 0, 500, 500)
	
	def done_action(self, sender):
		selected = []
		for row in self.view.selected_rows:
			selected.append(self.items[row[1]])
		self.selected_item = selected
		self.view.close()
		
	def row_selected(self, ds):
		if not self.view.allows_multiple_selection:
			self.selected_item = self.view.data_source.items[ds.selected_row]
			self.view.close()
		

def list_dialog(title='', items=None, multiple=False, done_button_title='Done'):
	''' copy of list_dialog from dialogs module, with themed mode, and with extra buttonitems to load and save history'''
	if not items:
		items = []
	c = _ListDialogController(title, items, multiple, done_button_title=done_button_title)
	c.idxNew=0
	#editor.apply_ui_theme(c.view,editor.get_theme_dict()['name'])
	save=ui.ButtonItem(title='Save')
	save.action=save_history

	load=ui.ButtonItem(title='Load')
	load.action=load_history

	copy=ui.ButtonItem(title='Copy')
	copy.action=copy_history

	searchField=ui.TextField()
	searchField.placeholder='Search'
	searchField.frame=(0,0,180,32)
	searchField.clear_button_mode='always'
	editor.apply_ui_theme(searchField)
	searchBarButton=ui.ButtonItem()
	ObjCInstance(searchBarButton).customView=searchField
	
	searchField.delegate=c.view.data_source
	c.view.right_button_items=[save,load,copy]
	c.view.left_button_items=[searchBarButton]

	editor.present_themed(c.view,editor.get_theme_dict()['name'],style='popover')

	c.view.wait_modal()
	return c.selected_item
	
def load_history(sender):
	'''Load previously saved history file into current history session'''
	with open(HISTORY_FILE,'r') as f:
		old_hist=json.load(f)
		cvc.history=old_hist

	#print (ObjCInstance(sender).view().superview().delegate())
	#sender.c.view.data_source._items=history
	#sender.c.idxNew=len(history)
	#sender.c.view.reload()
	
def save_history(sender):
	''' save current history session to the end of _history.py
	We probably should do some sort of size check, or perhaps 
	only write non duplicate lines'''
	with open(HISTORY_FILE,'r') as f:
		old_hist=json.load(f)
	with open(HISTORY_FILE,'w') as f:
		new_hist=[str(h)[:-1] for h in reversed(list(cvc.history()))]
		json.dump(old_hist+new_hist,f)


def copy_history(sender):
	raise NotImplementedError()
	
def add_long_press_history():	
	'''add the longtap gesture to the button.  '''
	#there must be a cleaner way to get this button...
	up=cvc.promptEditorView().superview().subviews()[1].subviews()[0]
	up.gestureRecognizers=[] 
	import gestures
	g=gestures.Gestures()
	g.add_long_press(up,select_history)
	# save some stuff
	gestures._saved=[save_history, load_history, list_dialog, _ListDialogController, select_history ]
if __name__=='__main__':
	import history_popup
	from importlib import reload
	reload(history_popup)
	history_popup.add_long_press_history()
	
