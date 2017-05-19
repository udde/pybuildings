from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui

class BuildingListWidget(QSplitter):

    def __init__(self, parent, data):
        
        QWidget.__init__(self, QtCore.Qt.Vertical)
        
        self.__parent__ = parent

        self.building_list_console = BuildingListConsole()
        self.building_list = BuildingList(self.building_list_console, data, self)

        self.addWidget(self.building_list)
        self.addWidget(self.building_list_console)
    

    def set_focus_building(self, data):
        self.__parent__.focus_building_id = data.id
    def set_focus_slice(self, data):
        self.__parent__.set_slice(data.id)

class BuildingList(QTreeWidget):
    
    def __init__(self, console, data_handler, parent):
        
        QListWidget.__init__(self)
        
        self.__parent__ = parent
        self.__data_handler = data_handler
        self.__console = console
        #self.setAlternatingRowColors(True)
        self.__property_data = self.__data_handler.get_all_propertys()

        for property in self.__property_data:
            item = QTreeWidgetItem([property.property_name])
            item.setData(0, QtCore.Qt.UserRole, property)
            self.addTopLevelItem(item)

        self.itemSelectionChanged.connect(lambda: self.selection_changed( ))
    

    def selection_changed(self, arg = None):
        
        self.__console.clear()
        data = self.selectedItems()[0].data(0, QtCore.Qt.UserRole)
        #self.__parent__.set_focus_building(data)
        self.__parent__.set_focus_slice(data)

        self.__console.append("Bld. name: " + data.property_name + "\n")
        self.__console.append("Bld. indx: " + str(data.id) + "\n")
        self.__console.append("FNR. nmbr: " + data.fnr + "\n")


class BuildingListConsole(QTextBrowser):
    
    def __init__(self):
        
        QTextBrowser.__init__(self)

        @property
        def __x(self):
            return self.__x

        self.clear

