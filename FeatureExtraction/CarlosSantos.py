import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import Gui
import copy
from Gui.GuiUtils import emptyLayout
import csv
from Utils.pca_utils import *
from PlaneFitting.LeastSquarePlaneFitting import *
from FeatureExtraction.FeatureExtractionBase import FeatureExtractionBase
from Clustering.SunRegionGrowing import *
import Vendor.CarlosSantos.ConcaveHullSantos as csh
import random
import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import pylab as pl
import scipy as sp
import triangle
from shapely.geometry import *

from Core.OpenGLObject import OpenGLObject

class CarlosSantosFeatureExtraction (FeatureExtractionBase):

    def __init__(self, kvalue = 100, simplificationfactor = 0.1 ):
        FeatureExtractionBase.__init__(self)
        self.model = { 
            'kvalue': kvalue,
            'simplificationfactor': simplificationfactor
        }
        self.setupParams()
    
    def setupParams(self):
        self.k_value = self.model['kvalue']
        self.simplification_factor = self.model['simplificationfactor']
        
    
    def setupGui(self, layout):
        emptyLayout(layout)
        
        self.k_value_layout = QHBoxLayout()
        self.k_value_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.k_value_slider.setMinimum(0)
        self.k_value_slider.setMaximum(90)
        self.k_value_slider.setValue(30)
        self.k_value_label = QtGui.QLabel("Hull K-value")
        self.k_value_label2 = QtGui.QLabel(str(30))
        self.k_value_slider.valueChanged.connect(self.k_value_changed)
        self.k_value_layout .addWidget(self.k_value_label)
        self.k_value_layout .addWidget(self.k_value_slider)
        self.k_value_layout .addWidget(self.k_value_label2)
        layout.addLayout(self.k_value_layout )

        self.simplification_layout = QHBoxLayout()
        self.simplification_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.simplification_slider.setMinimum(0)
        self.simplification_slider.setMaximum(90)
        self.simplification_slider.setValue(30)
        self.simplification_label = QtGui.QLabel("Simplification factor(HP):")
        self.simplification_label2 = QtGui.QLabel(str(30))
        self.simplification_slider.valueChanged.connect(self.simplification_changed)
        self.simplification_layout .addWidget(self.simplification_label)
        self.simplification_layout .addWidget(self.simplification_slider)
        self.simplification_layout .addWidget(self.simplification_label2)
        layout.addLayout(self.simplification_layout )


    def k_value_changed(self):
        self.k_value_label2.setText(str(self.k_value_slider.value()))
        self.model['kvalue'] = str(self.k_value_slider.value())

    def simplification_changed(self):
        self.simplification_label2.setText(str(self.simplification_slider.value()))
        self.model['simplificationfactor'] = str(self.simplification_slider.value())
    
    def extractFeature(self, points, planeq):
        self.setupParams()
        print()
        print("Extracting Feature...")
        print()

        hull2d = np.array(csh.concaveHull(points[:,0:2], self.k_value))
        print("... HULL DONE .... ")

        hull_polygon = Polygon(hull2d)
        simpler = hull_polygon.simplify(self.simplification_factor, preserve_topology=False)

        hull2d = [list(tuple) for tuple in list(simpler.exterior.coords)]

        total_edge_segments = np.array([], dtype=np.int).reshape(0,2)

        last = len(hull2d) - 1
        segs = np.array([ [x,x+1] for x in range(last) ])
        segs = np.vstack((segs, np.array([last, 0])))
        
        tridata = {'segments': segs, 'vertices': hull2d}
        tri_result = triangle.triangulate(tridata, 'pXq10F')

        verts_2d = tri_result['vertices']

        verts_3d = np.hstack(( verts_2d  , verts_2d[:,0:1]  ))
        verts_3d = elevatePointsToPlane(verts_3d, planeq)

        trianglelist = tri_result['triangles']
        
        new_segs = tri_result['segments']

        fullGlObject = OpenGLObject()
        roofGlObject = OpenGLObject()
        wallsGlObject = OpenGLObject()

        for triplet in trianglelist:
            roofGlObject.add_triangles_by_verts(verts_3d[triplet])
            fullGlObject.add_triangles_by_verts(verts_3d[triplet])

        for i, j in new_segs:

            p0 = verts_3d[i]
            p0down = np.array([p0[0], p0[1], 0])
            p1 = verts_3d[j]
            p1down = np.array([p1[0], p1[1], 0])

            wallsGlObject.add_triangles_by_verts(np.array([p0, p0down, p1down]))
            fullGlObject.add_triangles_by_verts(np.array([p0, p0down, p1down]))
            wallsGlObject.add_triangles_by_verts(np.array([p0, p1down, p1]))
            fullGlObject.add_triangles_by_verts(np.array([p0, p1down, p1]))

        return {"full": fullGlObject, "roof": roofGlObject, "walls": wallsGlObject}

def main ():

    buildings_path = "by_get_shp/by_get"                   ##read points from datahandler
    propertys_path = "ay_get_shp/ay_get"
    las_path = "datafromndr/norrkoping.las"

    points = readPointsFromFile("PolygonPoints.txt") # read strykjarnet from file
    #points = removeOutliers(points, mode='sor', max=2)
    all_points = [points]

    data_handler = DataHandler(buildings_path,propertys_path,las_path)
    bfps, points, solids, property_area, mbb, top_dogs = data_handler.get_slice_from_property(1592) #Korpen: 1558, Sprutan: 1509, Djupet 1593 #Diket 1592 1375 1343 1588 taet data: 1015 843 tre nivaer: 1594 

    all_points = points
    #all_points = [points[i] for i in range(len(points)) if bfps[i].id in top_dogs]
    #all_points = [points[0]]


    #Cant hull or triangulate if vertices area at E6 scale 
    offset = np.mean(property_area.points,0)
    for p in points:
        p[:,0:2] -= offset

    rg = SunRegionGrowing()
    all_regions_groups = rg.getMultiRegions(all_points)
    
    
    planemaker = LeastSquarePlaneFitting()
    
    
    all_plane_groups = planemaker.fitMultiPlaneGroups(all_points, all_regions_groups)
    

    cs_fe = CarlosSantosFeatureExtraction()
    all_fetures_groups = cs_fe.extractMultiFeatureGroups(all_points, all_regions_groups, all_plane_groups)

    ax = a3.Axes3D(pl.figure())
    colors = [[1,0,0],[0,1,0], [0,0,1], [0.65, 0.65, 0], [0, 0.65, 0.65], [0.65, 0, 0.65], [0.43, 0.43, 0.43]]
    cid = 0

    

    #for points, regions, planes in zip(all_points, all_regions_groups, all_plane_groups): 
    
        
    for features_group in all_fetures_groups:
        for feature in features_group:
            roofPolys = feature["roof"].get_triangles_as_polygons()
            wallPolys = feature["walls"].get_triangles_as_polygons()
            #vertexdata = feature.get_gl_vertex_data()

            tri = a3.art3d.Poly3DCollection([poly.exterior.coords for poly in wallPolys])
            tri.set_facecolor(colors[3])
            ax.add_collection3d(tri)
            tri = a3.art3d.Poly3DCollection([poly.exterior.coords for poly in roofPolys])
            tri.set_facecolor(colors[6])
            ax.add_collection3d(tri)
            cid += 1

        #for region, plane in zip(regions, planes):
        #    pass
        #    planeq = plane
        #    theshit = cs_fe.extractFeature(points[region], planeq)

        #    polys = theshit.get_triangles_as_polygons()
        #    vertexdata = theshit.get_gl_vertex_data()

        #    tri = a3.art3d.Poly3DCollection([poly.exterior.coords for poly in polys])
        #    tri.set_facecolor(colors[cid % len(colors)])
        #    cid += 1
        #    ax.add_collection3d(tri)

    ax.view_init(elev=39, azim=-55)
    ax.set_xlim3d(-30, 30)
    ax.set_ylim3d(-30, 30)
    ax.set_zlim3d(0, 60)
    pl.show()

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