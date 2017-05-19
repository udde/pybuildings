from BuildingFootprint import BuildingFootprint
import numpy as np
import shapefile
from PolygonTree import PolygonTree
class ShapeDataHandler(object):
    """description of class"""
    def __init__(self,buildings_filepath,propertys_filepath):
        self.__building_reader = shapefile.Reader(buildings_filepath)
        self.__propertys_reader = shapefile.Reader(propertys_filepath)
        self.__building_polygons = self.parse_buildings()
        self.__property_polygons = self.parse_propertys()
        self.__building_polygon_tree = PolygonTree(self.__building_polygons)


    def parse_buildings(self):
        shapes = self.__building_reader.shapes()
        records = self.__building_reader.records()
        data = []
        for idx in range(len(shapes)):
            
            #not a polygon?
            if self.__shapes[idx].shapeType != 5:
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
                np.array([ [point[0],point[1]] for point in self.__shapes[idx].points ], dtype=np.float64 ), #Points
                self.__shapes[idx].parts, #parts
                self.__records[idx][0], #Fnr
                name, #Name
                self.__records[idx][1], #Type
                self.__records[idx][3], #Obj_ID
                self.__records[idx][12] #Usage
            ))
            return data
    def parse_propertys(self):
        shapes = self.__building_reader.shapes()
        records = self.__building_reader.records()
        data = []
        #TODO: implement
    def get_building_by_id(self,id):
        return self.__building_polygons[id]
    def get_building_by_fnr_br(self,fnr_br):
        #tries to find and return the right building
        for item in self.__building_polygons:
            if item.fnr_br == str(fnr):
                return item
        #print("didnt find building with fnr: ", fnr)
        return None
    def get_buildings_by_polygon_intersection(self,polygon):
        ids = self.__building_polygon_tree.intersects(polygon)
        building_footprints = []
        for id in ids:
            building_footprints.append(self.__building_polygons[id])
        return building_footprints
    
        
    



