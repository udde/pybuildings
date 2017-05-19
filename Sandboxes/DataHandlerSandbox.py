import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import numpy as np
from Core import DataHandler
from Gui import *
np.set_printoptions(suppress=True)

buildings_path = "by_get_shp/by_get"
propertys_path = "ay_get_shp/ay_get"
las_path = "datafromndr/norrkoping.las"
data_handler = DataHandler(buildings_path,propertys_path,las_path)

#promblem propertys 1180
bfps,bfp_points,solids,property_area,mbb,top_dogs = data_handler.get_slice_from_property(1343)
stop = 1
#bfps = data_handler.get_buildings_in_property(1)
#map = gui_sandbox.MainWindow(data_handler)
#for bfp in bfps:
#    print(bfp)

