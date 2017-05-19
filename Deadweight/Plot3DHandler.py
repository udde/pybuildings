import importlib
import matplotlib
importlib.reload(matplotlib)
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy as np
import os,sys,inspect
from Deadweight.geompy import Polygon2d
import shapely.geometry
import matplotlib.collections
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PatchCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
#from shapely.geometry import Polygon
class Plot3DHandler(object):
    """description of class"""
    __fig = None
    __ax = None
    def __init__(self):
        
        self.__fig = plt.figure()
        self.__ax = self.__fig.add_subplot(111, projection='3d')
        #self.__ax = Axes3D(self.__fig)
        type(self.__ax)
    @property
    def ax(self):
        return self.__ax
    def add_polygon(self,polygon: shapely.geometry.Polygon,z_val):
        
        bfp = list(polygon.exterior.coords)
        verts = []
        verts.append(bfp)
        poly = matplotlib.collections.PolyCollection(verts,facecolor = 'r', alpha = 0.4)
        self.__ax.add_collection3d(poly,zs = z_val)
    
    def add_polygon_3d(self, data):
        self.__ax.add_collection3d(data)

    def add_wall_polygons(self,polygons,color='b',a=0.2):
        points = []

        for i in range(0,len(polygons)):    
            points.append(polygons[i].exterior.coords)
            
        polys = Poly3DCollection(points,alpha = a,facecolor = color)
        self.__ax.add_collection3d(polys)
                
    def add_point_cloud(self,points,color = 'b'):
        points = np.array(points)
        patchcol = self.__ax.scatter(points[:,0],points[:,1],points[:,2],c = color)
    def add_normals(self,normals,centroids):

        t = 8
        X = centroids[:,0]
        Y = centroids[:,1]
        Z = centroids[:,2]
        U = normals[:,0]
        V = normals[:,1]
        W = normals[:,2]


        self.__ax.quiver(X, Y, Z, U, V, W,length=6,pivot='tail')
    def show(self):

        self.axisEqual3D()
        plt.show()
    def axisEqual3D(self):
       
        extents = np.array([getattr(self.__ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
        sz = extents[:,1] - extents[:,0]
        centers = np.mean(extents, axis=1)
        maxsize = max(abs(sz))
        r = maxsize/2
        for ctr, dim in zip(centers, 'xyz'):
            getattr(self.__ax, 'set_{}lim'.format(dim))(ctr - r, ctr + r)

