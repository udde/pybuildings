import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import Gui
from Gui.GuiUtils import emptyLayout
import csv
from Utils.pca_utils import *
from Clustering.SunRegionGrowing import *
import Vendor.CarlosSantos.ConcaveHullSantos as csh
from FeatureExtraction.CarlosSantos import CarlosSantosFeatureExtraction
import random
import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import pylab as pl
import scipy as sp
import triangle


def main ():
    buildings_path = "by_get_shp/by_get"                   ##read points from datahandler
    propertys_path = "ay_get_shp/ay_get"
    las_path = "datafromndr/norrkoping.las"

    #points = readPointsFromFile("PolygonPoints.txt") # read strykjarnet from file
    #points = removeOutliers(points, mode='sor', max=2)
    #points = [points]

    data_handler = DataHandler(buildings_path,propertys_path,las_path)
    bfps, points, solids, property_area, mbb, top_dogs = data_handler.get_slice_from_property(1592) #Djupet 1593 #Diket 1592 1375 1343 1588 taet data: 1015 843 tre nivaer: 1594

    points = [points[i] for i in range(len(points)) if bfps[i].id in top_dogs]
    points = [points[0]]

    offset = np.mean(property_area.points,0)
    for p in points:
        p[:,0:2] -= offset

    rg = SunRegionGrowing()
    regions = rg.getMultiRegions(points)
    planes = []
    
    #fig = plt.figure()
    #ax = fig.add_subplot(111)

    f = open('myfile.csv', 'w')
    
    cs_fe = CarlosSantosFeatureExtraction()

    ax = a3.Axes3D(pl.figure())
    for region in regions[0]: # project points to planes

        planeq = getPlaneLSQ(points[0][region])
        csr = cs_fe.extractFeature(points[0][region], planeq)

        planes.append(planeq)
        hull = np.array(csh.concaveHull(points[0][region][:,0:2], 100))
        #for p in hull:
        #    p += offset
        hull0 = hull
        hull = np.hstack(( hull  , hull[:,0:1]  ))
        hull = elevatePointsToPlane(hull, planeq)
        
        for point in hull:
            x, y, z = point
            f.write(str(x)+",")
            f.write(str(y)+",")
            f.write(str(z)+"\n")

        f.write("\n")
        tri = a3.art3d.Poly3DCollection([hull])
        vtx = sp.rand(4,3)
        #tri = a3.art3d.Poly3DCollection([vtx])
        tri.set_color(colors.rgb2hex(sp.rand(3)))
        tri.set_edgecolor('k')
        #ax.add_collection3d(tri)

        #gör tianglelist av 2d hullet -> använd sedan 3d hullet!
        trianglelist = triangle.delaunay(hull0)

        for tri_ids in trianglelist:
            tri = a3.art3d.Poly3DCollection([hull[tri_ids]]) #3d hull
            tri.set_color(colors.rgb2hex(sp.rand(3)))
            tri.set_edgecolor('k')
            ax.add_collection3d(tri)

        for i in range(len(hull)):
            p0 = hull[i]
            p0down = np.array([p0[0], p0[1], 0])
            next = i+1
            if next == len(hull):
                next = 0
            p1 = hull[next]
            p1down = np.array([p1[0], p1[1], 0])

            tri = a3.art3d.Poly3DCollection([[p0, p0down, p1down]])
            
            tri.set_color('b')
            tri.set_edgecolor('k')
            ax.add_collection3d(tri)

            tri = a3.art3d.Poly3DCollection([[p0, p1down, p1]])

            tri.set_color('b')
            tri.set_edgecolor('k')
            ax.add_collection3d(tri)

        x = 10

    f.close()

    ax.view_init(elev=39, azim=-55)
    ax.set_xlim3d(-30, 30)
    ax.set_ylim3d(-30, 30)
    ax.set_zlim3d(0, 60)
    pl.show()
        #ax.plot(hull[:,0],hull[:,1])
    #fig.show()
    
    #printRegions(points, regions)
def axisEqual3D(ax):
       
    extents = np.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
    sz = extents[:,1] - extents[:,0]
    centers = np.mean(extents, axis=1)
    maxsize = max(abs(sz))
    r = maxsize/2
    for ctr, dim in zip(centers, 'xyz'):
        getattr(ax, 'set_{}lim'.format(dim))(ctr - r, ctr + r)

if __name__ == "__main__":
    main()