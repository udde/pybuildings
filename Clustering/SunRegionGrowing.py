import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import Gui

from Gui.GuiUtils import emptyLayout
import csv
from Utils.pca_utils import *
from Clustering.ClusteringBase import ClusteringBase




class SunRegionGrowing(ClusteringBase):

    def __init__(self, maxangle = 30, curvaturefactor = 0.7, nneigbours=9, mode='ball_tree', wallangle=80, regionsize=10, mergedist=2.0):
        ClusteringBase.__init__(self)
        self.model = {
            'mode': mode,
            'nneighbours': nneigbours,
            'maxangle': maxangle,
            'curvaturefactor': curvaturefactor,
            'wallangle': wallangle,
            'regionsize': regionsize,
            'mergedist' : mergedist,
        }
        self.setupParams()
    
    def setupParams(self):
        #print("Applying the model: ", self.model)
        self.nneigbours = self.model['nneighbours']
        self.maxangle = self.model['maxangle']
        self.mode = self.model['mode']
        self.curvaturefactor = self.model['curvaturefactor']
        self.wallangle = self.model['wallangle']
        self.small_region_max_size = self.model['regionsize']
        self.distance_for_merge = self.model['mergedist']
    
    def setupGui(self, layout):
        emptyLayout(layout)

        self.angle_layout = QHBoxLayout()
        self.angle_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.angle_slider.setMinimum(0)
        self.angle_slider.setMaximum(90)
        self.angle_slider.setValue(30)
        self.angle_label = QtGui.QLabel("Max angle:")
        self.angle_label2 = QtGui.QLabel(str(30))
        self.angle_slider.valueChanged.connect(self.maxangle_changed)
        self.angle_layout .addWidget(self.angle_label)
        self.angle_layout .addWidget(self.angle_slider)
        self.angle_layout .addWidget(self.angle_label2)
        layout.addLayout(self.angle_layout )

        self.curvature_layout = QHBoxLayout()
        self.curvature_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.curvature_slider.setMinimum(0)
        self.curvature_slider.setMaximum(20.0)
        self.curvature_slider.setValue(10.0)
        self.curvature_label = QtGui.QLabel("Max curvature:")
        self.curvature_label2 = QtGui.QLabel(str(self.curvaturefactor))
        self.curvature_slider.valueChanged.connect(self.curvature_changed)
        self.curvature_layout.addWidget(self.curvature_label)
        self.curvature_layout.addWidget(self.curvature_slider)
        self.curvature_layout.addWidget(self.curvature_label2)
        layout.addLayout(self.curvature_layout)

        self.mode_combo = QComboBox()
        self.modes = ['ball_tree', 'kd_tree', 'brute', 'auto']
        self.mode_combo.addItems(self.modes)
        self.mode_combo.currentIndexChanged.connect(self.select_method)
        layout.addWidget(self.mode_combo)

        self.neigbour_layout = QHBoxLayout()
        self.neigbour_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.neigbour_slider.setMinimum(0)
        self.neigbour_slider.setMaximum(25)
        self.neigbour_slider.setValue(self.nneigbours)
        self.neigbour_label = QtGui.QLabel("n neighbours:")
        self.neigbour_label2 = QtGui.QLabel(str(self.nneigbours))
        self.neigbour_slider.valueChanged.connect(self.neigbour_changed)
        self.neigbour_layout.addWidget(self.neigbour_label)
        self.neigbour_layout.addWidget(self.neigbour_slider)
        self.neigbour_layout.addWidget(self.neigbour_label2)
        layout.addLayout(self.neigbour_layout)

        self.regionsize_layout = QHBoxLayout()
        self.regionsize_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.regionsize_slider.setMinimum(0)
        self.regionsize_slider.setMaximum(25)
        self.regionsize_slider.setValue(self.small_region_max_size)
        self.regionsize_label = QtGui.QLabel("Region size:")
        self.regionsize_label2 = QtGui.QLabel(str(self.small_region_max_size))
        self.regionsize_slider.valueChanged.connect(self.regionsize_changed)
        self.regionsize_layout.addWidget(self.regionsize_label)
        self.regionsize_layout.addWidget(self.regionsize_slider)
        self.regionsize_layout.addWidget(self.regionsize_label2)
        layout.addLayout(self.regionsize_layout)

        self.mergedist_layout = QHBoxLayout()
        self.mergedist_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.mergedist_slider.setMinimum(0)
        self.mergedist_slider.setMaximum(25)
        self.mergedist_slider.setValue(self.distance_for_merge)
        self.mergedist_label = QtGui.QLabel("Merge distance:")
        self.mergedist_label.setMaximumWidth(100)
        self.mergedist_label2 = QtGui.QLabel(str(self.distance_for_merge))
        self.mergedist_slider.valueChanged.connect(self.mergedist_changed)
        self.mergedist_layout.addWidget(self.mergedist_label)
        self.mergedist_layout.addWidget(self.mergedist_slider)
        self.mergedist_layout.addWidget(self.mergedist_label2)
        layout.addLayout(self.mergedist_layout)

    def maxangle_changed(self):
        self.angle_label2.setText(str(self.angle_slider.value()))
        self.model['maxangle'] = self.angle_slider.value()
    def curvature_changed(self):
        realvalue = self.curvature_slider.value()/10.0
        self.curvature_label2.setText(str(realvalue))
        self.model['curvaturefactor'] = realvalue
    def select_method(self, i):
        self.model['mode'] = self.modes[i]
    def neigbour_changed(self):
        self.neigbour_label2.setText(str(self.neigbour_slider.value()))
        self.model['nneighbours'] = self.neigbour_slider.value()
    def regionsize_changed(self):
        self.regionsize_label2.setText(str(self.regionsize_slider.value()))
        self.model['regionsize'] = self.regionsize_slider.value()
    def mergedist_changed(self):
        self.mergedist_label2.setText(str(self.mergedist_slider.value()))
        self.model['mergedist'] = self.mergedist_slider.value()

    def getRegions(self, points):
        
        self.setupParams()

        normals, curvatures = calculateNomalsCurvatures(points, self.nneigbours, self.mode)
        normal_region_dot_threshold = np.cos(np.radians(self.maxangle))
        curvature_seed_threshold = 1.0/160 * self.curvaturefactor

        neigboursTable = NearestNeighbors(n_neighbors=self.nneigbours, algorithm=self.mode).fit(points)
        distances, indices = neigboursTable.kneighbors(points)
    
        neigbourhoods = np.array(indices)
        backlog = set(np.arange(len(points)))
        regions = []
        seeds = []
        neigbours = []

        i = 0  
        while len(backlog) != 0:
            regions.append([])
            seeds.append([])
            neigbours.append([])
            #find point with smallest curvature
            min_curvature_idx = findSmallestCurvatureIdx(curvatures)
            regions[i].append(min_curvature_idx)
            seeds[i].append(min_curvature_idx)
            backlog.remove(min_curvature_idx)

            k = 0
            while k < len(seeds[i]):
                #store n neighbours of all k seeds in the i:th round
                neigbours[i].append(neigbourhoods[seeds[i][k]])

                j = 0
                while j < len(neigbours[i][k]):
                    #all j neighbour indexes/points
                    p = neigbours[i][k][j]

                    if p in backlog and np.dot(normals[p],normals[seeds[i][k]]) > normal_region_dot_threshold:
                        regions[i].append(p)
                        if curvatures[p] < curvature_seed_threshold:
                            seeds[i].append(p)
                        backlog.remove(p)
                        curvatures[p] = BIG_CURVATURE
                    j += 1
                k += 1
            i += 1
        #extra step to remove "vertical" regions that are likely to be from wall urfaces
        removeWallRegions(regions, normals, wallangle=self.wallangle)

        #TODO(done!): join small regions or singles to larger regions!
        removeWallRegions(regions, normals, self.wallangle)
        large, small = separateRegions(regions, self.small_region_max_size)
        for small_region_idx in small:
            for point_idx in regions[small_region_idx]:
                dists = pointToRegionsDistances(points[point_idx], points, [regions[i] for i in large])
                if len(dists) > 0:
                    val, idx = min((val, idx) for (idx, val) in enumerate(dists))
                    if (val < self.distance_for_merge):
                        #small_region = regions[small_region_idx]
                        closest_large_region_idx = large[idx]
                        regions[closest_large_region_idx].append(point_idx)

        #large, small = separateRegions(regions, self.small_region_max_size)

        for region in [regions[i] for i in small]:
            if len(region) == 0:
                print("one empty here!")
        print(len(small), " small regions was not joined, too small and isolated")
        print("returning ", len(large), " regions. calculated from ", len(points), " points")
        return [regions[i] for i in large]
        return regions

def main ():

    buildings_path = "by_get_shp/by_get"                   ##read points from datahandler
    propertys_path = "ay_get_shp/ay_get"
    las_path = "datafromndr/norrkoping.las"
    data_handler = DataHandler(buildings_path,propertys_path,las_path)
    bfps, points, solids, property_area, mbb, top_dogs = data_handler.get_slice_from_property(1594) #Djupet 1593 #Diket 1592 1375 1343 1588 taet data: 1015 843 tre nivaer: 1594

    offset = np.mean(property_area.points,0)
    for p in points:
        p[:,0:2] -= offset

    points = [points[i] for i in range(len(points)) if bfps[i].id in top_dogs]
    
    #points = readPointsFromFile("PolygonPoints.txt") # read strykjarnet from file
    #points = removeOutliers(points, mode='sor', max=2)
    points = [points[0]]
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
    printRegions([points[0]], [regions[0]])

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


    planes = []
    for region in regions[0]: # project points to planes
        planeq = getPlaneLSQ(points[0][region])
        planes.append(planeq)
        projectPointsToPlane(points[0], region, planeq)

    printRegions(points, regions)
    #printRegions(points, [region for region in regions if len(region) > 0])

if __name__ == "__main__":
    main()