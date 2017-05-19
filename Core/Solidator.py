import numpy as np
from shapely.geometry import Polygon
from .BuildingFootprint import BuildingFootprint
from .OpenGLObject import OpenGLObject
from scipy.spatial import Delaunay
class Solidator(object):
    """This class makes solid 3D objects from point cloud data and polygon baseobjects"""
    
    def __init__(self):
       pass


    def extrude(self,point_cloud,bfp: BuildingFootprint,ground_level = 0):
        
        polygon = bfp.polygonize()[0] #TODO: gör för alla polygoner i en bfp
        points = point_cloud
        avg_heigt = points[:,2].mean()

        #Walls
        footprint_coords = np.array(list(polygon.exterior.coords))
        n_fp_coords = footprint_coords.shape[0]
        n_wall_triangles = (n_fp_coords-1)*2
        lower_ring = np.concatenate([footprint_coords, np.full([n_fp_coords,1],ground_level)],1)
        upper_ring = np.concatenate([footprint_coords, np.full([n_fp_coords,1],avg_heigt)],1)
        walls = np.zeros([n_wall_triangles * 3,3])
        
        for i in range(n_fp_coords-1):
                 
            p0 = lower_ring[i,:]        #  p2---p3
            p1 = lower_ring[i+1,:]      #  |    |
            p2 = upper_ring[i+1,:]      #  |    |
            p3 = upper_ring[i,:]        #  p1---p0

            i = i*6
            walls[i:i+3] = [p0,p2,p1]
            walls[i+3:i+6] = [p0,p3,p2]
            
        #Top & bottom
        bottom_triangle_verts = bfp.triangulate_proper()
        n_bottom_tri_verts = bottom_triangle_verts.shape[0]
        
        bottom = np.concatenate([bottom_triangle_verts, np.full([n_bottom_tri_verts,1],ground_level)],1)
        top = np.concatenate([bottom_triangle_verts, np.full([n_bottom_tri_verts,1],avg_heigt)],1)
        triangle_verts = np.vstack([walls,bottom,top])
        
        solid = OpenGLObject()
        solid.add_triangles_by_verts(triangle_verts)    
        
        return solid
    
    def ground_maker(self,ground_points,bfp: BuildingFootprint):
        ground_points, _ = self.reject_outliers(ground_points,1)
        avg_ground = ground_points[:,2].min()
        polygon = bfp.polygonize()[0]
        footprint_coords = np.array(list(polygon.exterior.coords))
        n_fp_coords = footprint_coords.shape[0]
        base = np.concatenate([footprint_coords, np.full([n_fp_coords,1],avg_ground)],1)

        all_points = np.vstack([ground_points,base])

        center = np.mean(all_points,0)
        del_points = all_points - center
        res = Delaunay(del_points[:,0:2], qhull_options='QJ')
        tri_verts = np.zeros([0,3])
        for tids in res.simplices:
            verts = del_points[tids,:]
            tri_verts = np.vstack([tri_verts,verts])
        tri_verts = tri_verts+center
        solid = OpenGLObject()
        solid.add_triangles_by_verts(tri_verts) 
        return all_points,solid
    
    def reject_outliers(self,data, m=2):
        
        if not data.shape[1] ==3:
            ValueError("data must have 3 collumns")
        
        mask =  abs(data[:,2] - np.mean(data[:,2])) < m * np.std(data[:,2])
        inliers = data[mask]
        outliers = data[mask==False]
        
        return inliers,outliers
    