
import os, sys, numpy as np, shapefile, triangle, shapely
from shapely.geometry import Polygon, LinearRing

def counter_clockwise_vertices(points, segs):
    #TODO: make this a private class function
    #print("counter clockwise funciton")
    #print("segs len:", len(segs))
    sum = 0
    for i in range(len(segs)):

        first = segs[i][0]
        second = segs[i][1]

        dx = points[second][0] - points[first][0]
        dy = points[second][1] + points[first][1]

        sum += (dx*dy)
    
    return sum <= 0 

'''
This is a base class for handeling polygon-like objects with meta-data fetched from shape-files
'''
class GisPolygon():

    def __init__(self, id, points, parts):
        self.__id = id
        self.__points = points
        self.__parts = parts
        self.__n_parts = len(parts)
 
    #Declare the members as properties with get/set functionality
    @property
    def id(self):
        return self.__id
    @property
    def points(self):
        return self.__points
    @points.setter
    def points(self, points):
        self.__points = points
    @property
    def parts(self):
        return self.__parts
    
    def __str__(self):
       #Override the standard print function to display an object nicely
        return "QGIS-ID: {}".format(self.__id)

    def set_geometry_from_polygon(self, polygon:Polygon):
        #Changes the objects shape to an existing polygon, removes possible holes/parts
        if len(list(polygon.interiors)) != 0:
            raise Exception('border polygon added has interiors') 
        self.__points = polygon.exterior.coords
        self.__parts = [0]

    def triangulate(self, flags: str = 'pXqi'):

        total_edge_segments = np.array([], dtype=np.int).reshape(0,2) 
        holes = []
        centers = []
        #print(self.__id)
        if self.__n_parts == 1:
           
            segs = np.array([ [x,x+1] for x in range(len(self.__points) - 1) ])
            total_edge_segments = np.vstack((total_edge_segments, segs ))
            holes.append(False) # solo polygon cant be a hole.
        
        elif self.__n_parts > 1:
 
            parts = list(self.__parts)
            if parts[-1] != self.__n_parts:
                parts.append(len(self.__points))
            #print("Parts:",parts)
                    
            for i in range(self.__n_parts):
                
                subset = self.__points[parts[i]:parts[i+1]]
                #print("subset:" ,len(subset), subset)
                approx_center = np.mean(subset,0)  #TODO: better way to find a point within the polygon area
                centers.append(approx_center)
                #print("!")
                segs = np.array([], dtype=np.int).reshape(0,2)
                segs = np.array([ [x,x+1] for x in range(parts[i],parts[i+1]-1) ]) # -1 slutet
                #print("Segs:",segs)
                total_edge_segments = np.vstack((total_edge_segments, segs))
                holes.append(counter_clockwise_vertices(self.__points, segs))

        triangulation_params = {
            'segments': total_edge_segments,
            'vertices': self.__points
        }
        
        hole_points = np.array([centers[i] for i in range(len(centers)) if holes[i]])

        if len(hole_points) > 0:
            
            triangulation_params = {
                'segments': total_edge_segments,
                'vertices': self.__points,
                'holes': hole_points
            }

        if self.__id == 1072 or self.__id == 647 or self.__id == 1504 or self.__id == 1327 or self.__id == 1472:
            triangulated_data = triangle.triangulate(triangulation_params, '')

        else:
            triangulated_data = triangle.triangulate(triangulation_params, flags)
        
        return triangulated_data

    def triangulate_proper(self):
        #TODO: remove this? replaced OpenGL object?
        triangled_data = self.triangulate()
        pos = triangled_data['vertices']
        faces = (np.array(triangled_data['triangles']).flatten())
        all_pos = pos[faces]

        return all_pos

    def gl_ready_vertices(self, center=False):
        #TODO: remove this? replaced OpenGL object?
        triangled_data = self.triangulate()
        pos = triangled_data['vertices']
        #print(pos, np.shape(pos))
        faces = (np.array(triangled_data['triangles']).flatten())
        all_pos = pos[faces]
        
        #TODO
        if center:
            transl = all_pos[0]
            scale = 0.025
            all_pos -= transl
            all_pos *= scale

        vertices = np.zeros(len(all_pos), [('position', np.float32, 2)])
        vertices['position'] = all_pos
        
        return all_pos

    def polygonize(self):
        
        # solo polygon
        if self.__n_parts == 1:
            return [Polygon(self.__points)]
        
        #multiple
        elif self.__n_parts > 1:
            
            #print("Parts",type(self.__parts))
            parts = list(self.__parts)
            if parts[-1] != self.__n_parts:
                parts.append(len(self.__points))
            polygons = []

            for i in range(self.__n_parts): #check all parts
               
                subset = self.__points[parts[i]:parts[i+1]]
                segs = np.array( [ [x,x+1] for x in range(parts[i],parts[i+1]-1) ]) # -1 slutet
                
                #is subset a poly or hole?
                hole = counter_clockwise_vertices(self.__points, segs)

                if not hole:
                    
                    tmp_polygon = Polygon(subset)
                    internal_holes = []
                    
                    for j in range(self.__n_parts): #go through again and check for internal holes
                    
                        sub = self.__points[parts[j]:parts[j+1]]
                        sgs = np.array( [ [x,x+1] for x in range(parts[j],parts[j+1]-1) ])
                        hole = counter_clockwise_vertices(self.__points, sgs)
                        #print("Parts: ", parts)
                        #print("SUB: ", sub)
                        ring = LinearRing(sub)
                    
                        if hole and tmp_polygon.contains(ring):
                            internal_holes.append(sub)

                    polygons.append(Polygon(subset,internal_holes))

            return polygons

def main():
    print()    

if __name__ == "__main__":
    sys.exit(int(main() or 0))