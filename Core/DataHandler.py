import os
import sys
import struct
import numpy as np
import shapely.geometry
import scipy.interpolate

from .Solidator import Solidator
#from Plot3DHandler import Plot3DHandler
#from Plot2DHandler import Plot2DHandler
from .LasFileHandler import LasFileHandler
from .ShapeFileHandler2 import ShapeFileHandler2
from .OpenGLObject import OpenGLObject
from .BuildingFootprint import BuildingFootprint
from shapely.geometry import Point, Polygon
from Utils.ulpy import Stopwatch
from scipy.spatial import Delaunay

class DataHandler(object):
    """description of class"""
    def __init__(self,buldings_path,propertys_path,las_data_path):
        
        #INIT READERS
        self.__solidator = Solidator()
        self.__buildings = ShapeFileHandler2(buldings_path,'by')
        self.__propertys = ShapeFileHandler2(propertys_path,'ay')
        self.__lasdata = LasFileHandler(las_data_path,1)
        

        #Calculate intersection of data sets
        las_bb = shapely.geometry.box(*self.__lasdata.bounds)
       
        shape_bb = shapely.geometry.box(*self.__buildings.bounds)
        intersection = las_bb.intersection(shape_bb)
        union = las_bb.union(shape_bb)

        #Read point cloud
        self.__lasdata.read_points()
        #self.__lasdata.read_points()
        #self.__lasdata.read_points()
        #self.__lasdata.read_points()

    def get_single_at_id(self, id):
        return self.__buildings.get_by_id(id)
    def get_all_buildings(self):
        return self.__buildings.get_all()
    def get_all_propertys(self):
        return self.__propertys.get_all()
              
    def get_slice_from_property(self,property_id):

        from Deadweight.PolygonPlotter import PolygonPlotter
        import Utils.ulpy as ulpy
        import shapely
        from shapely.geometry import Polygon 
        
        #JUST FOR DEBUG TODO: Remove
        #gedda = PolygonPlotter(self.__buildings.get_all_as_polygons())
  
        #Hämta polygonen för fastigheten
        property_area = self.__propertys.get_by_id(property_id)
        property_polygon = property_area.polygonize()[0]
        
        #Använd denna polygon för att hitta "building cluster"
        bfps,mbb, top_dogs = self.__buildings.get_clusters(property_polygon)
        points, points_out, z_range = self.__lasdata.get_points_from_polygon(mbb,rectangle_mode = True)
        #gedda.set_view_from_polygon(mbb)
        
        colors = ulpy.distinct_colors(len(bfps))
        bfp_points = []
        bfp_polys = []
        
        for i in range(len(bfps)):
            bfp = bfps[i]
            polygon = bfp.polygonize()[0]
            bfp_polys.append(polygon)
            
            #print("Shape of points: ",points.shape)
            mask = np.array([polygon.intersects(Point(x)) for x in points])
            mask = np.where(mask)
            bfp_points.append(points[mask])
            #gedda.draw_points(bfp_points[-1],color = 'r')
            #gedda.update()
            points = np.delete(points,mask,0)

        ground_points = points
        ground_level = np.min(ground_points)-2
        solids = []
        
        for i in range(len(bfps)):
            bfp = bfps[i]
            solids.append(self.__solidator.extrude(bfp_points[i],bfp,ground_level))

        #gedda.draw_points(ground_points,'b')
        #gedda.update()

        return bfps,bfp_points,solids,property_area,mbb, top_dogs

    def __construct_ground(bfp_polygons,ground_points,mbb):

        X = ground_points[:,0]
        Y = ground_points[:,1]
        Z = ground_points[:,2]

        interpolator = scipy.interpolate.interp2d(X,Y,Z)

        #coords = np.array(mbb.exterior.coords)
        #z_vals = interpolator(coords[:,1],coords[:,2])
        #coords_3d = np.hstack(coords,z_vals)

        for bp in bfp_polys:
            coords = np.array(polygon.exterior.coords)
            z_vals = interpolator(coords[:,0],coords[:,1])
            coords_3d = np.hstack([coords,z_vals]) #TODO: updaterda bfp?
            np.vstack([ground_points,coords_3d])

        res = Delaunay(ground_points[:,0:2], qhull_options='QJ')
        tri_verts = np.zeros([0,3])
        
        for tids in res.simplices:
            verts = ground_points[tids,:]
            p = Polygon(verts)
            #gedda.draw_auxiliary_polygon(p,a = 0.2)
            tri_verts = np.vstack([tri_verts,verts])

        print(tri_verts)

  