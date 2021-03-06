import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import Gui

from Gui.GuiUtils import emptyLayout
import csv
from Utils.pca_utils import *
from PlaneFitting.LeastSquarePlaneFitting import LeastSquarePlaneFitting

class PlaneFittingLayout(QVBoxLayout):

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
        self.planes_combo.addItem("Least Square", 11)
        self.planes_combo.addItem("Region Growing 2", 22)
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
    
    def setPlanes(self):

        all = None
        if self.parent.__parent__.canvas_3d.render_params['top_dogs_only'] == False:
            all = self.method.fitMultiPlaneGroups( self.parent.current_data['points'], self.parent.current_data['regions'])
        
        self.parent.setPlanes( 
            all,
            self.method.fitMultiPlaneGroups( self.parent.current_data['top_dog_points'], self.parent.current_data['top_dog_regions'])
        )

    def selectMethod(self, i):
        if i == 0:
            print("no method selected")
        if i == 1:
            self.method = LeastSquarePlaneFitting()
            self.method.setupGui(self.implementation)
        else:
            print("Plane Fitting method selected:", i)

        #Enable buttons
        self.planes_button.setEnabled(self.method != None and 'regions' in self.parent.current_data)

    
def printModel(model):
    for key in model:
        print(key, " : ", model[key])