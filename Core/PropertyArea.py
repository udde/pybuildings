

import os, sys, numpy as np, shapefile, triangle, shapely
from shapely.geometry import Polygon, LinearRing
from .GisPolygon import GisPolygon

class PropertyArea(GisPolygon):

    def __init__(self, id, points, parts, fnr, property_name, trakt, omrades_nr, blockenet):
   
        self.__fnr = fnr
        self.__property_name = property_name
        self.__trakt = trakt
        self.__omrades_nr = omrades_nr
        self.__blockenhet = blockenet
        super().__init__(id, points, parts)
    
    #Declare the members as properties with get/set functionality

    @property
    def fnr(self):
        return self.__fnr
    @property
    def property_name(self):
        return self.__property_name
    @property
    def trakt(self):
        return self.__trakt
    @property
    def omrades_nr(self):
        return self.__omrades_nr
    @property
    def blockenhet(self):
        return self.__blockenhet

    def __str__(self):
    #Override the standard print function to display an object nicely
        return "\n==== PROPERY AREA OBJECT ====\
                \nQGIS-ID: {}\
                \nFNR: {}\
                \nName: {}\
                \nTrakt: {}\
                \nOmrades Nr: {}\
                \nBlockenhet: {}\
        ".format(self.id, self.__fnr, self.__property_name, self.__trakt, self.__omrades_nr, self.__blockenhet)
def main():
    print()    

if __name__ == "__main__":
    sys.exit(int(main() or 0))