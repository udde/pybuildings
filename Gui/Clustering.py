import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import Gui

from Gui.GuiUtils import emptyLayout
import csv
from Utils.pca_utils import *
from Clustering.SunRegionGrowing import SunRegionGrowing

class ClusterLayout(QVBoxLayout):

    def __init__(self, parent):
        QHBoxLayout.__init__(self, parent)
        self.model = {}
        self.method = None
        self.parent = parent
        self.setuplayout()

    def setuplayout(self):

        #Combo box for selecting the cluster method to use
        self.clustercombo = QComboBox()
        self.clustercombo.addItem("Select Method...", -1)
        self.clustercombo.addItem("Region Growing", 11)
        self.clustercombo.addItem("Region Growing 2", 22)
        self.clustercombo.currentIndexChanged.connect(self.selectMethod)
        self.addWidget(self.clustercombo)

        #method/implementation gui goes here....
        self.implementationgroup = QGroupBox("Implementation")
        self.implementation = QVBoxLayout()
        self.addLayout(self.implementation)
        
        #Button to invoke get regions or multi regions using the selected implementation
        self.clusterbutton = QPushButton("Find regions")
        self.clusterbutton.setEnabled(self.method != None)
        self.clusterbutton.clicked.connect(self.setRegions)
        self.addWidget(self.clusterbutton)
    

    def setRegions(self):
        all = None
        if self.parent.__parent__.canvas_3d.render_params['top_dogs_only'] == False:
            all = self.method.getMultiRegions( self.parent.current_data['points'] )
        self.parent.setRegions( 
            all,
            self.method.getMultiRegions( self.parent.current_data['top_dog_points'] )    )

    def selectMethod(self, i):
        if i == 0:
            print("no method selected")
        if i == 1:
            self.method = SunRegionGrowing()
            self.method.setupGui(self.implementation)
        else:
            print("Cluster method selected:", i)

        #Enable buttons
        self.clusterbutton.setEnabled(self.method != None)

    
def printModel(model):
    for key in model:
        print(key, " : ", model[key])