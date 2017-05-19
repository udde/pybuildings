import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import Gui

from Gui.GuiUtils import emptyLayout
import csv
from Utils.pca_utils import *
from FeatureExtraction.CarlosSantos import CarlosSantosFeatureExtraction

class FeatureExtractionLayout(QVBoxLayout):

    def __init__(self, parent):
        QHBoxLayout.__init__(self, parent)
        self.model = {}
        self.method = None
        self.parent = parent
        self.setuplayout()

    def setuplayout(self):

        #Combo box for selecting the cluster method to use
        self.planes_combo = QComboBox()
        self.planes_combo.addItem("Select Method...", -1)
        self.planes_combo.addItem("Carlos Santos", 11)
        self.planes_combo.currentIndexChanged.connect(self.selectMethod)
        self.addWidget(self.planes_combo)

        #method/implementation gui goes here....
        self.implementationgroup = QGroupBox("Implementation")
        self.implementation = QVBoxLayout()
        self.addLayout(self.implementation)
        
        #Button to invoke get regions or multi regions using the selected implementation
        self.planes_button = QPushButton("Fit Planes")
        self.planes_button.setEnabled(self.method != None)
        self.planes_button.clicked.connect(self.setPlanes)
        self.addWidget(self.planes_button)
    
    def setFeatures(self):
        self.parent.setFeatures(
            self.method.fitMultiFeatures( self.parent.current_data['points'], self.parent.current_data['planes']), 
            self.method.fitMultiFeatures( self.parent.current_data['top_dog_points'], self.parent.current_data['top_dog_planes']) )


    def selectMethod(self, i):
        if i == 0:
            print("no method selected")
        if i == 1:
            self.method = CarlosSantosFeatureExtraction()
            self.method.setupGui(self.implementation)
        else:
            print("Plane Fitting method selected:", i)

        #Enable buttons
        self.planes_button.setEnabled(self.method != None and 'planes' in self.parent.current_data)

    
def printModel(model):
    for key in model:
        print(key, " : ", model[key])