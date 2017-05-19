import sys
import os
from PyQt4.QtGui import *
from PyQt4 import QtGui, QtCore
from Deadweight.ShapeFileHandler import ShapeFileHandler
from Core import LasFileHandler
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
import random
import shapely
from Deadweight.Plot2DHandler import *


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



class Vestibule(QDialog):

    def __init__(self, parent):
        
        super(Vestibule, self).__init__()
      
        self.__parent__ = parent
        self.__las = None
        self.__shapes = None
        self.__las_bbox = None
        self.__shapes_bbox = None

        self.__shapes_loaded = False
        self.__las_loaded = False
        self.__both_loaded = False

        self.__width = 400
        self.__height = 200

        self.resize(self.__width, self.__height)

        self.__main_layout = QVBoxLayout()

        self.__h_spacer = QSpacerItem(0,0,QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Select Buttons
        self.__btn_shp = QPushButton("Read Shapes from shp-files")
        self.__btn_shp.clicked.connect(self.read_shapes)
        self.__btn_las = QPushButton("Read Laser-data from las-files")
        self.__btn_las.clicked.connect(self.read_las)

        # Select Layout
        self.__select_layout = QHBoxLayout()
        self.__select_layout.addWidget(self.__btn_shp)
        self.__select_layout.addWidget(self.__btn_las)
        self.__main_layout.addLayout(self.__select_layout)


        # Plot widget
        self.__plot = Plot2DHandler()
        self.__main_layout.addWidget(self.__plot.canvas)


        #self.buttons = QDialogButtonBox(
        #    QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
        #    QtCore.Qt.Horizontal, self)
        
        #self.__main_layout.addWidget(self.buttons)


        ## Proceed Buttons
        self.__btn_done = QPushButton("Proceed with the selected data")
        self.__btn_done.clicked.connect(self.accept)
        self.__btn_cancel = QPushButton("Cancel")
        self.__btn_cancel.clicked.connect(self.reject)

        ## Proceed Layout
        self.__proceed_layout = QHBoxLayout()
        #self.__proceed_layout.addWidget(self.buttons)
        self.__proceed_layout.addItem(self.__h_spacer)
        self.__proceed_layout.addWidget(self.__btn_done)
        self.__proceed_layout.addItem(self.__h_spacer)
        self.__proceed_layout.addWidget(self.__btn_cancel)


        self.__main_layout.addLayout(self.__proceed_layout)
        self.setLayout(self.__main_layout)

        self.show()
    
    @property
    def shapes(self):
        return self.__shapes
    @property
    def las(self):
        return self.__las

    @staticmethod
    def get_shapes_and_las(parent= None):
        
        dialog = Vestibule(parent)
        result = dialog.exec_()
        dont_proceed = result != QDialog.Accepted
        shapes = dialog.shapes
        las = dialog.las
        print(dont_proceed, shapes, las)
        return dont_proceed, shapes, las
        


    def read_shapes(self):
        
        filename = QFileDialog.getOpenFileName(self,'Open Shape File', 'C:\\Users\\aut\\Source\\Repos\\SBG_Building_model_reconstruction\\TestRun\\by_get_shp')
        if not filename:
            pass
        else:
            self.__shapes = ShapeFileHandler(os.path.splitext(filename)[0])
            self.__shapes_loaded = True

            self.__plot.add_building_footprints(self.__shapes.get_all_buildings())
            self.__shapes_bbox = shapely.geometry.box(*self.__shapes.bounds)
            self.__plot.add_area(self.__shapes_bbox, a = 0.1, lwidth = 0.0, fcolor = 'b')
            self.__plot.set_axis_limits(self.__shapes_bbox)

            if self.__shapes_loaded and self.__las_loaded:
                intersection = self.__las_bbox.intersection(self.__shapes_bbox)
                union = self.__las_bbox.union(self.__shapes_bbox)
                #self.__plot.add_area(union)
                #self.__plot.add_area(intersection,a = 0.3, fcolor = 'r')
                self.__plot.set_axis_limits(union)
            
            self.__plot.show()
            self.resize(self.__width, self.__height+200)

    def read_las(self):
        
        filename = QFileDialog.getOpenFileName(self,'Open Las File', 'C:\\Users\\aut\\Source\\Repos\\SBG_Building_model_reconstruction\\TestRun\\datafromndr')
        if not filename:
            pass
        else:
            self.__las = LasFileHandler(filename)
            self.__las_loaded = True

            self.__las_bbox = shapely.geometry.box(* self.__las.bounds)
            self.__plot.add_area(self.__las_bbox, a = 0.2, lwidth = 0.0, fcolor = 'r')
            self.__plot.set_axis_limits(self.__las_bbox)

            if self.__shapes_loaded and self.__las_loaded:
                print("!")
                intersection = self.__las_bbox.intersection(self.__shapes_bbox)
                union = self.__las_bbox.union(self.__shapes_bbox)
                #self.__plot.add_area(union)
                #self.__plot.add_area(intersection,a = 0.0, fcolor = 'r')
                self.__plot.set_axis_limits(union)
            
            self.__plot.show()
            self.resize(self.__width+200, self.__height+380)


    def return_shp_las(self):

        return {'shapes': self.__shapes, 'las': self.__las}


def main():
    
    a = QApplication(sys.argv)

    dont_proceed, shapes, las = Vestibule.get_shapes_and_las()


    print("????")
    if dont_proceed:
        print("Dont_proceed")
        #Terminate program
        pass
    
    las.read_points()
    print("run main")
    mw = MainWindow(shapes, las) #gui main
    
    a.exec_()


if __name__ == "__main__":
    
    sys.exit(int(main() or 0))







