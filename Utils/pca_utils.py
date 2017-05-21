import os,sys,inspect
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import os 
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import scipy
from scipy.spatial import cKDTree as kdTree
from Core import *
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import normalize as sknorm
from sklearn.neighbors import NearestNeighbors
from scipy import stats
from scipy.spatial import ConvexHull

from Utils.ulpy import distinct_colors

#from leastsquareplane import getPlane

def readPointsFromFile(path):
    points = np.loadtxt(path)
    return points

def getPointsFromDatahandler(datahandler, property_id, building_number=0):
    bfps, bpoints, solids, property_area, mbb, top_dogs = datahandler.get_slice_from_property(property_id)
    offset = np.mean(property_area.points,0)
    points = bpoints[building_number]
    points[:,0:2] -= offset
    return points

def removeOutliers(points, mode='sor', max=2, k=8):
    if mode == 'median':
        z_data = points[:,2]
        mask = abs(z_data - np.median(z_data)) < max 
        return points[mask]
    elif mode == 'sor':
        kdtree = kdTree(points)
        distances, i = kdtree.query(kdtree.data, k=k, n_jobs=-1) 
        z_distances = stats.zscore(np.mean(distances, axis=1))
        sor_filter = abs(z_distances) < max
        print("SOR removing: ", len([bol for bol in sor_filter if bol == False]))
        return points[sor_filter]
    else:
        print("Undefined outlierremoval mode")

def removeOutliersIndices(points, indices, mode='sor', max=2, k=8):
    if mode == 'median':
        z_data = points[:,2]
        mask = abs(z_data - np.median(z_data)) < max 
        return points[mask]
    elif mode == 'sor':
        kdtree = kdTree(points)
        distances, i = kdtree.query(kdtree.data, k=k, n_jobs=-1) 
        z_distances = stats.zscore(np.mean(distances, axis=1))
        sor_filter = abs(z_distances) < max
        print("SOR removing: ", len([bol for bol in sor_filter if bol == False]))
        return indices[sor_filter]
    else:
        print("Undefined outlierremoval mode")

def calculateNomalsCurvatures(points, nneigbours=9, mode='ball_tree'):
    neigboursTable = NearestNeighbors(n_neighbors=nneigbours, algorithm=mode).fit(points)
    distances, indices = neigboursTable.kneighbors(points)

    normals = []
    curvatures = []

    for point_id in range(len(points)):
        neighbour_ids = indices[point_id]
        neighbour_points = points[neighbour_ids]

        covariance_matrix = np.cov(neighbour_points.T) #Numpy calculates the covariance matrix of the point neighbourhood
        eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
        eigen_pairs = [(np.abs(eigenvalues[i]), eigenvectors[:,i]) for i in range(len(eigenvalues))]
        eigen_pairs.sort(key=lambda x: x[0], reverse=True) #sort per eigenvalue
        normal = eigen_pairs[2][1] #the approximated normal is the eigenvector corresponding to the 3d smallest eigenvalue 
                        # 'as the 3d data spreads the least in that direction' <- pca 
        #If the normal is facing downwards its flipped. PCA does not take orientation in concern. However, due to the nature of the lidar data
        # we feel safe asuming that the normals of a rooftop point it at most horizontal
        if normal[2] < 0 :
            normal *= -1
        normals.append(normal)
        #Curvature or flatness aproximated based on the magnitude relationship between the normal and the other eigenvectors
        curvature = eigen_pairs[2][0] / (eigen_pairs[0][0] + eigen_pairs[1][0] + eigen_pairs[2][0]) 
        curvatures.append(curvature)

    return sknorm(np.array(normals)), np.array(curvatures) #return as normalized and np-arrays

BIG_CURVATURE = 10000
def findSmallestCurvatureIdx(C):
    min_curvature = min(C)
    if( min_curvature == BIG_CURVATURE ):
        print("Min curvature not found")
    min_idx = np.argwhere(C==min_curvature)[0][0]
    C[min_idx] = BIG_CURVATURE
    return min_idx

def findRegions(points, nneigbours=9, mode='ball_tree', maxangle = 30, curvaturefactor = 1, prints=False):
    
    normals, curvatures = calculateNomalsCurvatures(points, nneigbours, mode)
    normal_region_dot_threshold = np.cos(np.radians(maxangle))
    curvature_seed_threshold = 1.0/160 * curvaturefactor

    neigboursTable = NearestNeighbors(n_neighbors=nneigbours, algorithm=mode).fit(points)
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
        if (prints):
            print("Region {} starting at point ".format(i) ,min_curvature_idx)
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
        if (prints):
            print("Region {} found {} points".format(i,len(regions[i])))
        i += 1
    removeWallRegions(regions, normals, wallangle=80)
    large, small = separateRegions(regions, 5)
    for small_region_idx in small:
        for point_idx in regions[small_region_idx]:
            dists = pointToRegionsDistances(points[point_idx], points, [regions[i] for i in large])
            val, idx = min((val, idx) for (idx, val) in enumerate(dists))
            if (val < 3.250):
                #small_region = regions[small_region_idx]
                closest_large_region_idx = large[idx]
                regions[closest_large_region_idx].append(point_idx)

    r = regions
    large, small = separateRegions(regions, 5)
    
    return [regions[i] for i in large]

def printRegions(points_list, regions_list):
    clrs = ['blue','red','yellow','green','cyan','magenta','white', 'black', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray']
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    
    for i in range(len(points_list)):
        if len(regions_list) != len(points_list):
            print("points and regions dosnt match")
        
        regions = regions_list[i]
        points = points_list[i]
        clrs = distinct_colors(len(regions))

        R = regions
        P = points
        for ii in range(len(R)):

            ax.scatter(P[R[ii]][:,0],P[R[ii]][:,1],P[R[ii]][:,2], c=clrs[ii])

    extents = np.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
    sz = extents[:,1] - extents[:,0]
    centers = np.mean(extents, axis=1)
    maxsize = max(abs(sz))
    r = maxsize/2
    for ctr, dim in zip(centers, 'xyz'):
        getattr(ax, 'set_{}lim'.format(dim))(ctr - r, ctr + r)


    plt.show()

def removeWallRegions(regions, normals, wallangle=85): #wallangle "away" from [0,0,1] => verticalish => wall => remove
    normal_wall_dot_threshold = np.cos(np.radians(wallangle))
    mask = []
    up_vector = np.array([0,0,1])
    gone = 0
    for region in regions:
        region_normal = np.mean(normals[region], axis=0)
        angle = np.dot(region_normal, up_vector)
        if (angle < normal_wall_dot_threshold):
            regions.remove(region)
            gone += 1
    print("removing {} wall regions".format(gone))

class Region:
    def __init__(ids, points, normals):

        self.__ids = ids
        self.__normals = normals
        self.__normal = np.mean(normals[ids], axis=0)  
        self.__points = points[ids]
        
    def addPointsToRegion(self, ids):
        self.__ids += ids
        self.__points = np.vstack((self.__points,points[ids]))
    
    def recalculateNormal(self, normals):
        self.__normal = np.mean(normals[ids], axis=0)  
    
    @property
    def points(self):
        return self.__points[ids]
    
class PlaneEq:
    def __init__(self,a,b,c,d):
        self._a = a
        self._b = b
        self._c = c
        self._d = d
    def __str__(self):
     return "{:5.2f} X + {:5.2f} Y + {:5.2f} Z = -D".format(self._a,self._b,self._c,self._d)
    @property
    def normal(self):
        return np.array([self._a,self._b,self._c])
    @property
    def coefficients(self):
        return self._a, self._b, self._c, self._d
    @property
    def originPoint(self):
         return np.array([0, 0, -1*self._d/self._c]) #return point from x-y-origin intersecting the plance d=-(ax+by+cz)

def getPlaneLSQ(points):
    data = points
    X,Y = np.meshgrid(np.arange(-3.0, 3.0, 0.5), np.arange(-3.0, 3.0, 0.5))
    XX = X.flatten()
    YY = Y.flatten()
    A = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
    C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])    # coefficients
    #expressed using matrix/vector product
    Z = np.dot(np.c_[XX, YY, np.ones(XX.shape)], C).reshape(X.shape)
    #Plane
    a, b, c, d = C[0], C[1], -1., C[2]
    if (c < 0):
        return PlaneEq(a*-1,b*-1,c*-1,d*-1)
    return PlaneEq(a,b,c,d)
   
def getPlaneSimple(points, normals, eqform=True):
    plane_center_point = np.mean(points, axis=0)
    plane_normal = np.mean(normals, axis=0)

    if eqform: # d = -(ax+by+cz). abc being the normal components, xyz a point in the plane
        a, b, c = plane_normal
        d = -(np.dot(plane_normal, plane_center_point))
        return a, b, c, d
    else:
        return plane_center_point, plane_normal  

def convexHull(points_, plot=False):
    points = points_[:,0:2]
    hull = ConvexHull(points)
    area = hull.area
    howmany = len(points)
    density = howmany/area
    #print("Convex area: {}, n points: {}, ratio: {}".format(area, howmany, density))

    if plot:
        plt.plot(points[:,0], points[:,1], 'o')
        for simplex in hull.simplices:
            plt.plot(points[simplex, 0], points[simplex, 1], 'k-')
        plt.show()

    return hull, density

def pointPlaneDistance(point, planeq):
    plane_point = planeq.originPoint
    points_vector = point - plane_point
    plane_normal = planeq.normal
    distance = np.dot(plane_normal, points_vector)
    return distance

def avgPlaneDistance(points, planeq):
    a,b,c,d = planeq.coeficients
    howmany = len(points)
    sum = 0.0
    for p in points:
        sum += abs(pointPlaneDistance(a,b,c,d,p))
    return sum/howmany

def projectPointToPlane(point, planeq):
    dist = pointPlaneDistance(point, planeq)
    return point - dist * planeq.normal

def projectPointsToPlane(points, region, planeq):
    for idx in region:
        points[idx] = projectPointToPlane(points[idx], planeq)

def elevatePointsToPlane(points, planeq):
    a,b,c,d = planeq.coefficients
    points = np.hstack((points,np.zeros([points.shape[0],1])))
    
    for point in points:
        x = point[0]
        y = point[1]
        point[2] = -1*(d+a*x+b*y)/c
    return points

#def elevatePointsToPlane(allpoints, region, planeq):
#    a,b,c,d = planeq.coefficients
#    for idx in region:
#        x = allpoints[idx][0]
#        y = allpoints[idx][1]
#        allpoints[idx][2] = -1*(d+a*x+b*y)/c

def elevatePointsToPlane(points, planeeq):
    a,b,c,d = planeeq.coefficients
    for i in range(len(points)):
        x = points[i][0]
        y = points[i][1]
        points[i][2] = -1*(d+a*x+b*y)/c
    return points

def elevatePointsToPlanes(points, regions):
    for region in regions:
        region_pts = points[region]
        a,b,c,d = getPlane(region_pts)
        for idx in region:
            x = points[idx][0]
            y = points[idx][1]
            points[idx][2] = -1*(d+a*x+b*y)/c

def separateRegions(regions, limit=5):
    large = []
    small = []
    for id in range(len(regions)):
        if len(regions[id]) > limit:
            large.append(id)
        else:
            small.append(id)
    return large, small

def mergeRegion(points, planes, regions, region):
    
    for id in region:
        point = points[id]
        plane = planes[id]
        rd = pointToRegionDistance(point, points, regions)
        pd = pointPlaneDistance(point, plane)

def centerPoint3D(points):
    return np.mean(points, axis=0)


def pointToRegionsDistances(p0, points, regions, kd=3):

    region_distances = []

    for rid in range(len(regions)):
        region = regions[rid]
        data = np.insert([points[i] for i in region], 0, p0, axis=0) #prepending the search point to the region
        kdtree = kdTree(data)
        distances, i = kdtree.query(p0, k=2)
        region_distances.append(distances[1]) # distances[0][0] will be to the point itself
    return region_distances


        
        
def mergeSmallRegions(points, regions, planes, limit = 5):
    large, small = separateRegions(regions,limit)

    for region_id in small:
        for id in regions[region_id]:
            dr = pointToRegionsDistance(points[id], points, regions)
    pass
