import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import importlib
import matplotlib
importlib.reload(matplotlib)
matplotlib.use('Qt4Agg')
import vispy
import numpy as np
import random
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui

from vispy import app, gloo
from vispy.util.transforms import perspective, translate, rotate
from vispy.geometry import meshdata as md
from vispy.geometry import generation as gen

from Deadweight.ShapeFileHandler import ShapeFileHandler
from Core.LasFileHandler import LasFileHandler

from Utils.pca_utils import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT

import Gui

from Core import DataHandler

class PlotObject():
    
    def __init__(self, parent=None):
        
        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        # self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar = NavigationToolbar2QT(self.canvas, None)
        # Just some button connected to `plot` method
        self.button = QtGui.QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        # set the layout
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.button)
        #self.setLayout(layout)
        self.plot()

    def plot(self):
        ''' plot some random stuff '''
        # random data
        data = [random.random()*10 for i in range(10)]

        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.hold(False)

        # plot data
        ax.plot(data, '*-')

        # refresh canvas
        self.canvas.draw()


class PipelineWidget(QWidget):
   
    def __init__(self, parent, data):
    
        QWidget.__init__(self)
        
        self.__parent__ = parent
        self.__data_handler = data
        self.current_data = {}
        self.setup_gui()
        self.resize(250, 150)

    def set_slice_from_property(self, property_id):
        self.current_data['bfps'], self.current_data['points'], self.current_data['solids'], self.current_data['property_area'], self.current_data['mbb'], self.current_data['top_dogs'] = self.__data_handler.get_slice_from_property(property_id)
        #self.__offset = np.mean(self.__property_area.points,0)

        self.current_data['top_dog_points'] = [self.current_data['points'][i] for i in range(len(self.current_data['bfps'])) if self.current_data['bfps'][i].id in self.current_data['top_dogs'] ]

    def setup_gui(self):
        #DATA GROUP
        self.data_group = QGroupBox("Data")
        self.data_layout = QVBoxLayout()
        self.data_group.setMaximumWidth(220)
        self.data_group.setLayout(self.data_layout)

        #self.bfp_checkbox = QCheckBox("Bfp blocks")
        #self.bfp_checkbox.setChecked(False)
        #self.bfp_checkbox.stateChanged.connect(lambda: self.bfps(self.bfp_checkbox.isChecked() ))
        
        #RENDER GROUP
        self.rendering_group = QGroupBox("Rendering")
        self.rendering_layout = QVBoxLayout()
        self.rendering_group.setMaximumWidth(220)
        self.rendering_group.setLayout(self.rendering_layout)
        # transparent checkbox
        self.transparent_checkbox = QCheckBox("Transparent buildings")
        self.transparent_checkbox.setChecked(False)
        self.transparent_checkbox.stateChanged.connect(lambda: self.transp(self.transparent_checkbox.isChecked()))
        self.rendering_layout.addWidget(self.transparent_checkbox)
        # top dogs checkbox
        self.topdogs_checkbox = QCheckBox("Top dogs only")
        self.topdogs_checkbox.setChecked(False)
        self.topdogs_checkbox.stateChanged.connect(lambda: self.dogs(self.topdogs_checkbox.isChecked()))
        self.rendering_layout.addWidget(self.topdogs_checkbox)
        # reset points 
        self.reset_points_button = QPushButton("reset points")
        self.reset_points_button.clicked.connect(lambda: self.reset_points())
        self.rendering_layout.addWidget(self.reset_points_button)

        #CLUSTERING GROUP
        self.cluster_group = QGroupBox("Clustering")
        self.cluster_layout = Gui.ClusterLayout(self)
        self.cluster_group.setMaximumWidth(220)
        self.cluster_group.setLayout(self.cluster_layout)
        
        #PLANE FITTING GROUP
        self.plane_group = QGroupBox("Plane Fitting")
        self.plane_layout = Gui.PlaneFittingLayout(self)
        self.plane_group.setMaximumWidth(220)
        self.plane_group.setLayout(self.plane_layout)

        #PLANE FITTING GROUP
        self.features_group = QGroupBox("Roof features creation")
        self.features_layout = Gui.RoofFeaturesLayout(self)
        self.features_group.setMaximumWidth(220)
        self.features_group.setLayout(self.features_layout)


        self.parent_layout = QHBoxLayout()
        self.pipeline_layout = QHBoxLayout()

        #self.pipeline_layout.addWidget(self.data_group)
        self.pipeline_layout.addWidget(self.rendering_group)
        self.pipeline_layout.addWidget(self.cluster_group)
        self.pipeline_layout.addWidget(self.plane_group)
        self.pipeline_layout.addWidget(self.features_group)

        self.parent_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.parent_layout.addLayout(self.pipeline_layout)

        self.setLayout(self.parent_layout)
    
    def setRegions(self, regions, topregions):
        self.current_data['regions'] = regions
        self.current_data['top_dog_regions'] = topregions
        self.__parent__.canvas_3d.regions()
        #TODO: #self.__parent__.canvas_3d.regions(regions, self.current_data['points'], self.current_data['topdogs'])
        pass

    def reset_points(self):
        self.__parent__.canvas_3d.points()

    def setPlanes(self, planes, topplanes):
        self.current_data['planes'] = planes
        self.current_data['top_dog_planes'] = topplanes
        self.__parent__.canvas_3d.planes()
        pass

    def setFeatures(self, features, topfeatures):
        self.current_data['features'] = features
        self.current_data['top_dog_features'] = topfeatures
        self.__parent__.canvas_3d.features()
        pass

    def transp(self, bool):
        self.__parent__.canvas_3d.render_params['transparent'] = bool
            
    def dogs(self, bool):
        self.__parent__.canvas_3d.render_params['top_dogs_only'] = bool
        self.__parent__.canvas_3d.updateCanvas()

    def bfps(self, bool):
        self.__parent__.canvas_3d.draw_model_transparent = bool

    def render_points(self, attr, value):
        #self.__parent__.canvas_3d.setup_bfps()
        pass


class MainWindow(QMainWindow):
    """
        this is the mainWondow for the program gui
    """

    def __init__(self, data_handler):
        
        QMainWindow.__init__(self)

        self.__data_handler = data_handler

        self.resize(1400, 840)
        self.setWindowTitle('gui main window')

        self.pipelineWidget = PipelineWidget(self, data_handler)

        self.canvas_map = Gui.Map2D(data_handler, self)
        self.canvas_map.create_native()
        self.canvas_map.native.setParent(self)

        self.canvas_3d = Gui.Canvas3D(data_handler, self, self.pipelineWidget.current_data)
        self.canvas_3d.create_native()
        self.canvas_3d.native.setParent(self)

        self.listWidget = Gui.BuildingListWidget(self, data_handler)
        

        self.setupLayout()
        #self.__focus_building_id = 0

        self.set_slice(1593)
        self.show()
 
    #Is called from the property list
    def set_slice(self, id):
        print("selected property id: ", id)
        self.pipelineWidget.set_slice_from_property(id)
        self.canvas_3d.setCanvasData()
             
    @property
    def focus_building_id(self):
        return self.__focus_building_id

    @focus_building_id.setter
    def focus_building_id(self, id_to_focus):
        self.__focus_building_id = id_to_focus
        self.canvas_map.set_selected(self.__focus_building_id)
        #self.canvas_3d.set_selected(self.__focus_building_id)

    def setupLayout(self):
        
        self.verticalSplitter = QSplitter(QtCore.Qt.Vertical)

        self.horizontalSplitter = QSplitter(QtCore.Qt.Horizontal)

        self.mapListSplitter = QSplitter(QtCore.Qt.Vertical)

        self.mapListSplitter.addWidget(self.listWidget)
        self.mapListSplitter.addWidget(self.canvas_map.native)

        self.horizontalSplitter.addWidget(self.mapListSplitter)
        
        self.horizontalSplitter.addWidget(self.canvas_3d.native)

        self.verticalSplitter.addWidget(self.horizontalSplitter)
        self.verticalSplitter.addWidget(self.pipelineWidget)
        self.setCentralWidget(self.verticalSplitter)


if __name__ == "__main__":
    appQt = QApplication(sys.argv)
    
    #value = Vestibule(None)

    #filename = ("by_get_shp/by_get")

    #shapes = ShapeFileHandler(filename)

    #las_dir_path = os.path.dirname(os.path.realpath(__file__))
    #las_dir_path = las_dir_path + '/datafromndr' 
    #las_file_path = las_dir_path + "/norrkoping.las"
    #las = LasFileHandler(las_file_path,8)
    
    #las.read_points()
    #las.read_points()
    
    #mw = MainWindow(shapes, las) #gui main

    buildings_path = "by_get_shp/by_get"
    propertys_path = "ay_get_shp/ay_get"
    las_path = "datafromndr/norrkoping.las"
    data_handler = DataHandler(buildings_path,propertys_path,las_path)

    mw = MainWindow(data_handler)

    sys.exit(appQt.exec_())