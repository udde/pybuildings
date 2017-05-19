import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
from Core import BuildingFootprint
from shapely.geometry import Polygon
import shapely
from matplotlib.collections import PatchCollection
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

class Plot2DHandler(object):
    """description of class"""
    
    __fig = None
    __ax = None
    
    def __init__(self):
        
        self.__fig, self.__ax  = plt.subplots(figsize=(20, 20))
        self.__ax.get_xaxis().set_visible(False)
        self.__ax.get_yaxis().set_visible(False)
        self.__fig.tight_layout(pad=0.3)
        self.canvas = FigureCanvas(self.__fig)
        
    @property
    def ax(self):
        return self.__ax


    def add_polygons(self,polygons: list):
        
        patches = []

        for i in range(0,len(polygons)):
        
            plg = matplotlib.patches.Polygon(list(polygons[i].exterior.coords))
            patches.append(plg)
        
        p = PatchCollection(patches, alpha=0.4)
        #colors = np.full((len(patches)),0.4)
        #p.set_array(np.array(colors))
        self.__ax.add_collection(p)
        self.__ax.autoscale()
        #self.__ax.set_aspect('equal')
    
    
    def add_building_footprints(self,bfps):
        
        patches = []

        for bfp in bfps:
        
            polygon = bfp.polygonize()[0]
            plg = matplotlib.patches.Polygon(list(polygon.exterior.coords))
            patches.append(plg)
        
        p = PatchCollection(patches, alpha=0.4)
        #colors = np.full((len(patches)),0.4)
        #p.set_array(np.array(colors))
        self.__ax.add_collection(p)


    def set_axis_limits(self,polygon: shapely.geometry.Polygon):
        xmin,ymin,xmax,ymax = polygon.bounds
        
        self.__ax.set_xlim(xmin-100,xmax+100)
        self.__ax.set_ylim(ymin-100,ymax+100)

       
    def add_area(self,polygon: shapely.geometry.Polygon,fcolor='none',lwidth = 1,a = None):
        
        area = matplotlib.patches.Polygon(list(polygon.exterior.coords), True, alpha = a, facecolor = fcolor,edgecolor = 'black', linewidth = lwidth,linestyle ='solid')
        self.__ax.add_patch(area)


    def show(self):
        
        self.__ax.set_aspect('equal')
        self.__ax.get_xaxis().get_major_formatter().set_useOffset(False)
        
        self.canvas.draw()
        #plt.show()
