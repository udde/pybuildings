import numpy as np
from shapely.geometry import Polygon
import copy

class OpenGLObject(object):
    """description of class"""
    
    def __init__(self):
        
        self.__triangle_verts = np.zeros([0,3],dtype=np.float32)
        self.__triangle_normals = None
        self.__vertex_normals = None
        self.__centroids = None
        self.__object_center = None
        

    @property 
    def object_center(self):
        return self.__object_center

    @property
    def triangle_normals(self):
        return self.__triangle_normals
    
    @property
    def vertex_normals(self):
        return self.__vertex_normals
    
    @property
    def centroids(self):
        self.calculate_centroids()
        return self.__centroids
    
    @property
    def n_triangles(self):
        return int(self.__triangle_verts.shape[0]/3)
    
    @property
    def triangle_vertices(self):
        return self.__triangle_verts


    def add_triangles_by_verts(self,triangle_verts: np.ndarray):
        
        n_rows,n_cols = triangle_verts.shape
       
        if n_cols != 3:
            ValueError("Wrong number of columns: Input must be an Nx3 numpt array")
        if n_rows%3 != 0:
            ValueError("Wrong number of rows. Input rows must be 3 times the number of triangles")
        
        self.__triangle_verts = np.vstack([self.__triangle_verts,triangle_verts])
        self.calculate_normals()
        self.calculate_object_center() #TODO: is this really good?
    

    def calculate_object_center(self):
        self.__object_center = np.mean(self.__triangle_verts,0)
        
         
    def calculate_normals(self):
        
        triangle_normals = np.zeros([0,3])
        vertex_normals = np.zeros([0,3])
        #TODO: now alla normals are always re-calculated. 
        
        for i in range(0,self.__triangle_verts.shape[0],3):
            
            p0 = self.__triangle_verts[i,:]
            p1 = self.__triangle_verts[i+1,:]
            p2 = self.__triangle_verts[i+2,:]
            v1 = p1-p0
            v2 = p2-p0
            n = np.cross(v1,v2)
            n = n/np.linalg.norm(n)
            triangle_normals = np.vstack([triangle_normals,n])
            vertex_normals = np.vstack([vertex_normals,n,n,n])

        self.__triangle_normals = triangle_normals
        self.__vertex_normals = vertex_normals
    
        
    def calculate_centroids(self):
        centroids = np.zeros([0,3])
        #TODO: now alla centroids are always re-calculated. 
        for i in range(0,self.__triangle_verts.shape[0],3):
            p0 = self.__triangle_verts[i,:]
            p1 = self.__triangle_verts[i+1,:]
            p2 = self.__triangle_verts[i+2,:]
            c = np.mean(self.__triangle_verts[i:i+3,:],0)
            t = Polygon([p0,p1,p2,p0])
            
            centroids = np.vstack([centroids,c])
        self.__centroids = centroids
    
        
    def get_triangles_as_polygons(self):
        
        polygons = []
        for i in range(0,self.__triangle_verts.shape[0],3):
            
            p0 = self.__triangle_verts[i,:]
            p1 = self.__triangle_verts[i+1,:]
            p2 = self.__triangle_verts[i+2,:]
            polygons.append(Polygon([p0,p1,p2,p0]))
        
        return polygons

    def get_gl_vertex_data(self, new_origin = None):
        
        vertices = np.zeros(len(self.__triangle_verts), [('position', np.float32, 3),
                                                  ('normal', np.float32, 3)])
        
        if new_origin == None:
            new_origin = self.__object_center
        if new_origin == "inget":
            new_origin = [0,0]

        triangle_verts = copy.deepcopy(self.__triangle_verts)
        
        scale = 1
        triangle_verts[:,0:2] -= new_origin[0:2]
        triangle_verts *= scale

        vertices['position'] = triangle_verts
        vertices['normal'] = self.__vertex_normals
        
        return vertices
