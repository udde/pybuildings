

import os, sys, numpy as np, shapefile, triangle, shapely
from shapely.geometry import Polygon, LinearRing
from .GisPolygon import GisPolygon

class BuildingFootprint(GisPolygon):

    def __init__(self, id, points, parts, fnr, building_name, building_type, object_id, usage):
   
        self.__fnr_br = fnr
        self.__building_name = building_name
        self.__building_type = building_type
        self.__object_id = object_id
        self.__usage = usage
        super().__init__(id, points, parts)
    

    #Declare the members as properties with get/set functionality

    @property
    def fnr_br(self):
        return self.__fnr_br
    @property
    def building_name(self):
        return self.__building_name
    @property
    def building_type(self):
        return self.__building_type
    @property
    def usage(self):
        return self.__usage
    @property
    def object_id(self):
        return self.__object_id
    
    def __str__(self):
       #Override the standard print function to display an object nicely
        return "\n==== BUILDING FOOTPRINT OBJECT ====\
                \nQGIS-ID: {}\
                \nFNR: {}\
                \nName: {}\
                \nType: {}\
                \nOBJ_ID: {}\
                \nUsage: {}\
        ".format(self.id, self.__fnr_br, self.__building_name, self.__building_type, self.__object_id, self.__usage)

    
def main():
    print()    

if __name__ == "__main__":
    sys.exit(int(main() or 0))