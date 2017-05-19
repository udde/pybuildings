
import os, sys
import numpy as np
import shapefile
from Core import BuildingFootprint
from Core.PolygonTree import PolygonTree
import shapely.geometry
from Utils.ulpy import Stopwatch

def counter_clockwise_vertices( points, segs):

    #print("counter clockwise funciton")
    #print("segs len:", len(segs))
    sum = 0
    for i in range(len(segs)):

        first = segs[i][0]
        second = segs[i][1]

        dx = points[second][0] - points[first][0]
        dy = points[second][1] + points[first][1]

        sum += (dx*dy)
    #print(sum)
    return sum <= 0 

class ShapeFileHandler():

    def __init__(self, file_path,type = 'by'):
        print("\n==== READING SHAPE FILE ===")
        timer = Stopwatch()
        self.__file_path = file_path
        self.__reader = shapefile.Reader(self.__file_path)
        self.__shapes = self.__reader.shapes() #fetch data
        self.__records = self.__reader.records() #fetch meta data
        self.__data = []
        self.__named_only = []
        self.__type = type

        timer.start("Parsing all shapes and records to bfps")
        if self.__type == 'by':
            self.parseBuildings()
        elif self.__type == 'ay':
            self.parsePropertys()

        timer.stop_latest()
        self._polygon_tree = PolygonTree(self.__data)

        temp_data = self.__data
        
        test = shapely.geometry.box(*(self.__data[1999].polygonize()[0].bounds))
        test_res = self._polygon_tree.intersects(self.__data[1999].polygonize()[0])
        print("RESULT:")
        print(test_res)

    @property
    def bounds(self):
        xmin,ymin,xmax,ymax = self.__reader.bbox #xmin ymin xmax ymax

        return xmin,ymin,xmax,ymax
    def parseBuildings(self):
        for idx in range(len(self.__shapes)):
            
            #not a polygon?
            if self.__shapes[idx].shapeType != 5:
                print("data at idx ", idx, "is not of type polygon.")

            
            #Fetch a propper name (str) if possible
            if type(self.__records[idx][7]) == type("string"):
                
                name = self.__records[idx][7]
                name_is_not_empty = len(name) > 1

            elif type(self.__records[idx][7]) == type(b'bytes'):   #TODO: avkoda ordentligt ) 
                
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

            #the named objects BFP: __init__(self, id,  points, parts,fnr, building_name, building_type, object_id, usage):
            if name_is_not_empty:
                
                self.__named_only.append(BuildingFootprint(
                    idx, # id
                    np.array([ [point[0],point[1]] for point in self.__shapes[idx].points ], dtype=np.float64 ), #Points
                    self.__shapes[idx].parts, #parts
                    self.__records[idx][0], #Fnr    
                    name, #Name
                    self.__records[idx][1], #Type
                    self.__records[idx][3], #Obj_ID
                    self.__records[idx][12] #Usage
                ))

            #all objects BFP: __init__(self, id, points, parts, fnr, building_name, building_type, object_id, usage):
            self.__data.append(BuildingFootprint(
                idx, # id         
                np.array([ [point[0],point[1]] for point in self.__shapes[idx].points ], dtype=np.float64 ), #Points
                self.__shapes[idx].parts, #parts
                self.__records[idx][0], #Fnr
                name, #Name
                self.__records[idx][1], #Type
                self.__records[idx][3], #Obj_ID
                self.__records[idx][12] #Usage
            ))
            
    def get_all_buildings(self):
        return self.__data

    def get_all_named_buildings(self):
        return self.__named_only

    def get_single_from_FNR(self, fnr):
        #tries to find and return the right building
        for item in self.__data:
            if item.fnr_br == str(fnr):
                return item
        #print("didnt find building with fnr: ", fnr)
        return None

    def get_single_at_id(self, id: int):
        #tries to find and return the right building
        if id < 0 or id >= len(self.__data):
            #print("id ", id, " out of bounds")
            return None
        return self.__data[id]


def main():

    sh = ShapeFileHandler("by_get_shp/by_get")
    building = sh.get_single_at_id(1342)
    

if __name__ == "__main__":
    sys.exit(int(main() or 0))