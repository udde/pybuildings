import os, sys
import numpy as np
import shapefile
from .PropertyArea import PropertyArea
from .BuildingFootprint import BuildingFootprint
from .PolygonTree import PolygonTree
from shapely.geometry import Polygon
from Utils.ulpy import Stopwatch
import copy


class ShapeFileHandler2(object):
    """description of class"""
    def __init__(self,file_path,type):
        
        self.__reader = shapefile.Reader(file_path)
        self.__gis_polygons = []
        if type == 'by':
            self.__gis_polygons = self.parse_buildings()
            self.__polygon_tree = PolygonTree(self.__gis_polygons,grow_regions = True)
        elif type == 'ay':
            self.__gis_polygons = self.parse_propertys()
            self.__polygon_tree = PolygonTree(self.__gis_polygons,grow_regions = False)
        
    @property
    def bounds(self):
        r = self.__reader
        xmin,ymin,xmax,ymax = self.__reader.bbox #xmin ymin xmax ymax
        return xmin,ymin,xmax,ymax

    def parse_buildings(self):
        shapes = self.__reader.shapes()
        records = self.__reader.records()
        data = []
        for idx in range(len(shapes)):
            
            #not a polygon?
            if shapes[idx].shapeType != 5:
                print("data at idx ", idx, "is not of type polygon.")

            
            #Fetch a propper name (str) if possible
            if type(records[idx][7]) == type("string"):
                
                name = records[idx][7]
                name_is_not_empty = len(name) > 1

            elif type(records[idx][7]) == type(b'bytes'):   #TODO: avkoda ordentligt ) 
                
                name = ""
                name_is_not_empty = False
                #try:
                #    name = self.__records[idx][7].decode()
                #    name_is_not_empty = name.count(' ') != len(name)      
           
                #except UnicodeDecodeError:
                #    name = str(self.__records[idx][7])
                #    name_is_not_empty = True
            else:
                
                name = ""
                name_is_not_empty = False

            if name_is_not_empty:
                pass

            data.append(BuildingFootprint(
                idx, # id         
                np.array([ [point[0],point[1]] for point in shapes[idx].points ], dtype=np.float64 ), #Points
                shapes[idx].parts, #parts
                records[idx][0], #Fnr
                name, #Name
                records[idx][1], #Type
                records[idx][3], #Obj_ID
                records[idx][12] #Usage
            ))
        return data

    def parse_propertys(self):
        shapes = self.__reader.shapes()
        records = self.__reader.records()
        data = []

        #0-FNR 5-trakt 6-blockenhet 7-omrade

        for id in range(len(shapes)):

            points = np.array([ [point[0],point[1]] for point in shapes[id].points ], dtype=np.float64 )
            #not a polygon?
            if shapes[id].shapeType != 5:
                print("data at idx ", idx, "is not of type polygon.")
            
            name = records[id][8]
            if type(name) != type("string"):
                name = "_"

            data.append(PropertyArea(
                id, # id         
                points, #Points
                shapes[id].parts, #parts
                records[id][0], #Fnr
                name, #Property name
                records[id][5], #trakt
                records[id][7], #områdes nr
                records[id][6] #blockenhet
            ))
        return data
    
    def get_by_id(self,id):
        return self.__gis_polygons[id]
    
    def get_by_fnr(self,fnr):
        pass
    
    def get_by_polygon(self,polygon: Polygon):
        ids = self.__polygon_tree.find_intersecting(polygon)
        intersecting_gis_polygons = []
        
        for id in ids:
            intersecting_gis_polygons.append(self.__gis_polygons[id])
        return intersecting_gis_polygons
    
    def get_all(self):
        return self.__gis_polygons

    def get_all_as_polygons(self):
        return [gis_polygon.polygonize()[0] for gis_polygon in self.__gis_polygons]

    def get_clusters(self,polygon: Polygon):
        
        ids, questionable_polygon_ids,mbb, top_dogs = self.__polygon_tree.get_bounding_slice_from_polygon(polygon)
        gis_polygons_to_return = []
        
        gis_polygons_to_return = [self.__gis_polygons[i] for i in ids]

        for id in questionable_polygon_ids:
            p = self.__gis_polygons[id].polygonize()[0]
            intersection = p.intersection(mbb)

            gis_polygon = copy.deepcopy(self.__gis_polygons[id])
            gis_polygon.set_geometry_from_polygon(intersection)
            gis_polygons_to_return.append(gis_polygon)
            #gedda.draw_auxiliary_polygon(intersection,face_color ='o')

        print("\nAll bounding slice certain ids: ")
        print(list(ids))
        print("\nAll bounding questioable  ids: ")
        print(list(questionable_polygon_ids))

        #for id in ids:
            #gedda.highlight(id)

        #gedda.update()
        
        return gis_polygons_to_return,mbb, top_dogs
