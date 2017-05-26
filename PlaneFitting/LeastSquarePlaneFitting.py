import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import Gui
import copy
from Gui.GuiUtils import emptyLayout
import csv
from Utils.pca_utils import *
from PlaneFitting.PlaneFittingBase import PlaneFittingBase
from Clustering.SunRegionGrowing import *

class LeastSquarePlaneFitting(PlaneFittingBase):

    def __init__(self):
        PlaneFittingBase.__init__(self)
        self.model = { }
        self.setupParams()
    
    def setupParams(self):
        pass
    
    def setupGui(self, layout):
        emptyLayout(layout)
        
        label = QLabel("No adjustable parameters")
        layout.addWidget(label)

    def fitPlane(self, points):
        self.setupParams()

        data = points
        A = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
        C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])
        a, b, c, d = C[0], C[1], -1., C[2]
        return PlaneEq(a*-1,b*-1,c*-1,d*-1)

def main ():

    buildings_path = "by_get_shp/by_get"                   ##read points from datahandler
    propertys_path = "ay_get_shp/ay_get"
    las_path = "datafromndr/norrkoping.las"
    #data_handler = DataHandler(buildings_path,propertys_path,las_path)
    #bfps, points, solids, property_area, mbb, top_dogs = data_handler.get_slice_from_property(1593) #Djupet 1593 #Diket 1592 1375 1343 1588 taet data: 1015 843 tre nivaer: 1594

    #points = [points[i] for i in range(len(points)) if bfps[i].id in top_dogs]
    
    points = readPointsFromFile("PolygonPoints.txt") # read strykjarnet from file
    points = removeOutliers(points, mode='sor', max=2)
    points = [points]
    #print(len(points), " in top dogs... sending to regiongrowing")
    rg = SunRegionGrowing()
    regions = rg.getMultiRegions(points)

    l = []
    for region in regions[0]:
        print("region of: ", len(region))
        l += region
    print(len(points), " points")
    n = sum([len(region) for region in regions[0]])
    print("n: ", n)
    for i in range(len(l)-1):
        if l[i] in l[0:i] or l[i] in l[i+1:]:
            print(l[i], " is duplicate")
    
    #printRegions(points, regions)
    #printRegions([points[0]], [regions[0]])

    #regions to file
    f = open('regions_points.csv', 'w')
    for region in regions[0]:
        for idx in region:
            x, y, z = points[0][idx]
            if idx == region[-1]:
                f.write("{},{},{}\n\n".format(x,y,z))
            else:
                f.write("{},{},{}\n".format(x,y,z))
        #f.write("\n")

    pf = LeastSquarePlaneFitting()

    regions_planes = pf.fitMultiPlaneGroups(points, regions)


    for inner_points, inner_regions, inner_planes in zip(points, regions, regions_planes):
        for region, plane in zip(inner_regions, inner_planes):
            inner_points[region] = elevatePointsToPlane(inner_points[region], plane)

    #for region in regions[0]: # project points to planes
    #    planeq = pf.fitPlane(points[0][region])
    #    planes.append(planeq)
    #    projectPointsToPlane(points[0], region, planeq)

    printRegions(points, regions)
    #printRegions(points, [region for region in regions if len(region) > 0])

if __name__ == "__main__":
    main()