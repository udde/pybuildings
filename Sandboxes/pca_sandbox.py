import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import csv
from Utils.pca_utils import *
import Core

def main ():
    #points = readPointsFromFile("PolygonPoints.txt")            ##read strykjarnet from file

    buildings_path = "by_get_shp/by_get"                   ##read points from datahandler
    propertys_path = "ay_get_shp/ay_get"
    las_path = "datafromndr/norrkoping.las"
    data_handler = DataHandler(buildings_path,propertys_path,las_path)
    property_id = 1343
    points = getPointsFromDatahandler(data_handler, property_id, 2)
    
    points = removeOutliers(points, mode='sor', max=2)
    planes = []

    ang = 40
    curv = 0.8
    normals, curvatures = calculateNomalsCurvatures(points)
    regions = findRegions(points, maxangle=ang, curvaturefactor=curv, prints=False)
    #removeWallRegions(regions, normals, wallangle=80)


    printRegions(points, [region for region in regions[:] if len(region) > 0])

    for region in regions: # project points to planes
        planeq = getPlaneLSQ(points[region])
        planes.append(planeq)
        projectPointsToPlane(points, region, planeq)

    printRegions(points, [region for region in regions[:] if len(region) > 0])
    #large, small = separateRegions(regions, 8)

    #for region in [regions[i] for i in large]:
    #    planeq = getPlaneLSQ(points[region])
    #    planes.append(planeq)
    #    #projectPointsToPlane(points, region, planeq)

    #printRegions(points, [regions[i] for i in large])


    #for small_region_idx in small:

    #    for point_idx in regions[small_region_idx]:
    #        dists = pointToRegionsDistances(points[point_idx], points, [regions[i] for i in large])
    #        val, idx = min((val, idx) for (idx, val) in enumerate(dists))
    #        if (val < 3.250):
    #            #small_region = regions[small_region_idx]
    #            closest_large_region_idx = large[idx]
    #            regions[closest_large_region_idx].append(point_idx)
    
    #for i in large:
    #    projectPointsToPlane(points, regions[i], planes[i])
    
    #large, small = separateRegions(regions, 8)
    #printRegions(points, [regions[i] for i in large])
    #printRegions(points, [regions[i] for i in small])

    #_ , density = convexHull(points)
    #print ("Density: ",density)


if __name__ == "__main__":
    # execute only if run as a script
    main()