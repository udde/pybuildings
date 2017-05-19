from PyQt4.QtGui import QDialog, QVBoxLayout, QDialogButtonBox, QDateTimeEdit, QApplication
from PyQt4.QtCore import Qt, QDateTime
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from gui_sandbox import *
from Deadweight.Plot2DHandler import Plot2DHandler
import shapely

class Vestibule(QDialog):
    
    def __init__(self, parent = None):
        super(Vestibule, self).__init__(parent)

        self.__parent__ = parent
        self.__las = None
        self.__shapes = None
        self.__las_bbox = None
        self.__shapes_bbox = None

        self.__shapes_loaded = False
        self.__las_loaded = False
        self.__both_loaded = False

        self.__width = 500
        self.__height = 400

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
        #self.__select_layout.addItem(self.__h_spacer)
        self.__select_layout.addWidget(self.__btn_shp)
        self.__select_layout.addWidget(self.__btn_las)
        #self.__select_layout.addItem(self.__h_spacer)
        self.__main_layout.addLayout(self.__select_layout)

        # Plot widget
        self.__plot = Plot2DHandler()
        self.__canvas = self.__plot.canvas
        
        self.__main_layout.addWidget(self.__canvas)

        ## Proceed Buttons
        self.__btn_done = QPushButton("Proceed with the selected data")
        self.__btn_done.clicked.connect(self.accept)
        self.__btn_cancel = QPushButton("Cancel")
        self.__btn_cancel.clicked.connect(self.reject)
        #self.__main_layout.addWidget(self.__btn_done)
        #self.__main_layout.addWidget(self.__btn_cancel)

        ## Proceed Layout
        self.__proceed_layout = QHBoxLayout()
        self.__proceed_layout.addWidget(self.__btn_done)
        self.__proceed_layout.addWidget(self.__btn_cancel)
        self.__main_layout.addLayout(self.__proceed_layout)

        self.setLayout(self.__main_layout)

    # get current date and time from the dialog
    def dateTime(self):
        return self.datetime.dateTime()

    @property
    def shapes(self):
        return self.__shapes
    
    @property
    def las(self):
        return self.__las

    
    @staticmethod
    def getData(parent = None):
        
        dialog = Vestibule(parent)
        result = dialog.exec_()
        shapes = dialog.shapes
        las = dialog.las
        
        return (shapes, las, result == QDialog.Accepted)


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

                intersection = self.__las_bbox.intersection(self.__shapes_bbox)
                union = self.__las_bbox.union(self.__shapes_bbox)
                #self.__plot.add_area(union)
                #self.__plot.add_area(intersection,a = 0.0, fcolor = 'r')
                self.__plot.set_axis_limits(union)
            
            self.__plot.show()
            self.resize(self.__width+100, self.__height+320)

#import qdarkstyle
from Gui.ProgressBar import ProgressBarWidget as Pbar
def main():
    
    app = QApplication([])
    #app.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))
#    app.setStyleSheet("""
        
#        * {
#            color: black;
#            font-size: 13px;
#            font-family: "Lucida Sans Unicode", "Lucida Grande", sans-serif;
#        }
#        .Vestibule{
#        background-color: #555
#        }
#        .QListWidgetItem {
#            padding: 5px;
#        }
#        .QPushButton {

#            color: #333;
#border: 2px solid #555;
#border-radius: 11px;
#padding: 5px;
#background: qradialgradient(cx: 0.3, cy: -0.4,
#fx: 0.3, fy: -0.4,
#radius: 1.35, stop: 0 #fff, stop: 1 #888);
#min-width: 40px;
#            }
#        """)
    #app.setStyle("motif")
    #app.setStyle(QStyleFactory.create('Cleanlooks'))
    
    shapes, las, proceed = Vestibule.getData()
    #print("shapes: {},  las: {}, proceed: {}".format(shapes, las, proceed))
    
    if proceed:
        #pbar = Pbar()
        las.read_points()
        #mw = MainWindow()
    app.exec_()    


if __name__ == "__main__":
    
    sys.exit(int(main() or 0))