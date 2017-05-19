def emptyLayout(layout):
    for i in reversed(range(layout.count())):
        
        #print(i)
        #print(layout.children())
        
        if layout.itemAt( i ) != None and layout.itemAt( i ).layout() != None:
            layout_to_remove = layout.itemAt( i ).layout()
            print("layout remove, recursive")
            emptyLayout(layout_to_remove)
            layout.removeItem(layout_to_remove)
            layout_to_remove.setParent(None)
        
        if layout.itemAt( i ) != None and layout.itemAt( i ).widget() != None:
            widget_to_remove = layout.itemAt( i ).widget()
            print("widget remove")
            layout.removeWidget( widget_to_remove )
            widget_to_remove.setParent( None )