#!python2

import tableview_rowheight, ui, objc_util
# create a tableview and delegate and datasource, per usual
#tableview_rowheight.setup_tableview_swizzle(False)
t=ui.TableView(frame=(0,0,200,576))
d=ui.ListDataSource([str(x) for x in range(100)])
t.data_source=t.delegate=d

# here i will just create height that grows then shrinks again
def tableview_height_for_section_row(tv,section,row):
	return 10+(row/5)**2 if row<50 else 10+((100-row)/5)**2

d.tableview_height_for_section_row=tableview_height_for_section_row

# this is optional, but speeds up initial display and scrolling
# set to nominal or average height
t_o=objc_util.ObjCInstance(t)
t_o.estimatedRowHeight=44

t.present('sheet')
