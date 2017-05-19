import importlib
import matplotlib
importlib.reload(matplotlib)
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
import numpy as np
from shapely.geometry import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


class PolygonPlotter(object):
    """description of class"""
    def __init__(self,polygons):
        self.__color_liu_compl_yellow = list(np.array([253,239,93])/255)
        self.__color_liu_compl_orange = list(np.array([255,100,66])/255)
        self.__color_liu_compl_purple = list(np.array([137,129,211])/255)
        self.__color_liu_compl_grey = list(np.array([206,126,145])/255)

        self.__color_liu_turk = list(np.array([23,199,210])/255)
        self.__color_liu_green = list(np.array([0,207,181])/255)
        self.__color_liu_blue = list(np.array([0,185,231])/255)
        self.__polygons = polygons
        self.__fig, self.__ax  = plt.subplots(figsize=(20, 20))
        self.__ax.get_xaxis().set_visible(False)
        self.__ax.get_yaxis().set_visible(False)
        self.__fig.tight_layout(pad=0.3)
        self.canvas = FigureCanvas(self.__fig)

        self.__add_polygons(polygons)


    def __add_polygons(self,polygons):
        patches = []

        for i in range(0,len(polygons)):
        
            polygon = matplotlib.patches.Polygon(list(polygons[i].exterior.coords))
            patches.append(polygon)
        
        self.__patches = PatchCollection(patches, facecolor = self.__color_liu_blue)
        self.__ax.add_collection(self.__patches)

    def draw_auxiliary_polygon(self,polygon,face_color = None,a = 1.0,edge_color='black',line_width = 3,line_style = 'solid'):
        if not face_color:
            face_color = self.__color_liu_green
        if face_color == 'y':
            face_color = self.__color_liu_compl_yellow
        elif face_color == 'o':
            face_color = self.__color_liu_compl_orange
        elif face_color =='p':
            face_color = self.__color_liu_compl_purple

        coords = list(polygon.exterior.coords)
        hl_area = matplotlib.patches.Polygon(coords, True, alpha = a, facecolor=face_color, edgecolor = edge_color,linewidth = line_width,linestyle =line_style)
        self.__ax.add_patch(hl_area)

    def highlight(self,id,color = 'y'):
        if color == 'y':
            face_color = self.__color_liu_compl_yellow
        elif color == 'o':
            face_color = self.__color_liu_compl_orange
        elif color =='p':
            face_color = self.__color_liu_compl_purple

        polygon = self.__polygons[id]
        coords = list(polygon.exterior.coords)
        hl_area = matplotlib.patches.Polygon(coords, True, facecolor = face_color, edgecolor = 'black',linestyle ='solid')
        self.__ax.add_patch(hl_area)
    
    
    def autoscale_view(self):
        self.__ax.set_aspect('equal')
        self.__ax.get_xaxis().get_major_formatter().set_useOffset(False)
        self.__ax.autoscale_view(tight=False)
        
        ylim = self.__ax.axes.get_ylim()
        xlim = self.__ax.axes.get_xlim()
        self.set_axis(xlim,ylim,factor = 0.1)

    def set_axis(self,xlim,ylim,factor):
        
        y_padding = (ylim[1]-ylim[0])*factor
        x_padding = (xlim[1]-xlim[0])*factor
        ylim = [ylim[0]-y_padding,ylim[1]+y_padding]
        xlim = [xlim[0]-x_padding,xlim[1]+x_padding]
        self.__ax.axes.set_ylim(ylim)
        self.__ax.axes.set_xlim(xlim)

    def set_view_from_polygon(self,polygon):
        bbox = polygon.bounds

        xlim = [bbox[0],bbox[2]]
        ylim = [bbox[1],bbox[3]]

        self.set_axis(xlim,ylim,0.4)

    def draw_points(self,points,color = 'r'):
        points = np.array(points)
        self.__point_patches = self.__ax.scatter(points[:,0],points[:,1],c = color,zorder=10)
        
    def show_figure(self):

        self.autoscale_view()
        plt.ion()
        plt.show()
        plt.draw()
        plt.pause(0.001)
        input("Press [enter] to continue.")

    def update(self):
        plt.draw()
        plt.pause(0.001)
        input("Press [enter] to continue.")