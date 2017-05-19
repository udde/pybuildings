import sys
from PyQt4 import QtGui, QtCore

app = QtGui.QApplication(sys.argv)

class Data():
    def __init__(self, title:str):
        self.title = title

class Tree(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)

        self.setFixedSize(450, 520)
        self.setWindowTitle("okej")

        self.treeWidget = QtGui.QTreeWidget(self)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.move(25,25)
        self.treeWidget.resize(400, 400)
        
        data = Data("Parent Item 1")
        item = QtGui.QTreeWidgetItem(["Hello World1"])
        item.setData(0,QtCore.Qt.UserRole, data)
        item.addChild(QtGui.QTreeWidgetItem(["Hello10"]))
        item.addChild(QtGui.QTreeWidgetItem(["Hello11"]))
        item.addChild(QtGui.QTreeWidgetItem(["Hello12"]))
        item.addChild(QtGui.QTreeWidgetItem(["Hello13"]))

        self.treeWidget.addTopLevelItem(item)
        
        data = "Parent Item 2"
        item = QtGui.QTreeWidgetItem(["Hello World2"])
        item.setData(0,QtCore.Qt.UserRole, "bogus")
        item.addChild(QtGui.QTreeWidgetItem(["Bogus"]))
        #item.addChild(QtGui.QTreeWidgetItem(["Hello21"]))
        #item.addChild(QtGui.QTreeWidgetItem(["Hello22"]))
        #item.addChild(QtGui.QTreeWidgetItem(["Hello23"]))

        self.treeWidget.addTopLevelItem(item)

        self.treeWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        
        self.treeWidget.itemSelectionChanged.connect(self.on_change)
        self.treeWidget.itemExpanded.connect(self.on_change)
    
    def on_change(self, itemex):
        print("pased:",itemex,itemex.data(0, QtCore.Qt.UserRole))
        getSelected = self.treeWidget.selectedItems()
        
        #howmany = len(getSelected)
        #if howmany == 0:
        #    return
        #print("SElected: ", howmany)
        
        #only a parent
        if howmany == 1 and getSelected[0].childCount() > 0:
            
            print("Selected Parent Node {} :".format(getSelected[0].text(0)))

            n_childs = getSelected[0].childCount()
            print("{} Children: ".format(n_childs))
            
            for i in range(n_childs):
                #self.treeWidget.setItemSelected(getSelected[0].child(i), True)
                print(getSelected[0].child(i))

        #all nodes
        
        for item in getSelected:
            if not not item.data(0, QtCore.Qt.UserRole):
                print("!")
                print("{}, data: ".format(item.text(0)), item.data(0, QtCore.Qt.UserRole))

                item.data(0, QtCore.Qt.UserRole).removeChild(item.child(0))

                item.data(0, QtCore.Qt.UserRole).addChild(QtGui.QTreeWidgetItem(["Hello20"]))
                item.data(0, QtCore.Qt.UserRole).addChild(QtGui.QTreeWidgetItem(["Hello21"]))
                item.data(0, QtCore.Qt.UserRole).addChild(QtGui.QTreeWidgetItem(["Hello22"]))
                item.data(0, QtCore.Qt.UserRole).addChild(QtGui.QTreeWidgetItem(["Hello23"]))

                item.setExpanded(True)




        #for item in getSelected:
        #    if item.data(0, QtCore.Qt.UserRole):
        #        print("Data: ", item.data(0, QtCore.Qt.UserRole))


        #getSelected = self.treeWidget.selectedItems()
        #if getSelected:
        #    print("Selected: ")
        #    baseNode = getSelected[0]
        #    getChildNode = baseNode.text(0)
            
        #    for item in getSelected:
        #        print(item)




tree = Tree()
tree.show()

sys.exit(app.exec_())