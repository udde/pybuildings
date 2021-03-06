from PyQt4.QtGui import *

class FeatureExtractionBase():
    def __init__(self):
        pass
    def setupGui(self, layout):
        raise NotImplementedError("Please Implement this method")
    def setupParams(self):
        raise NotImplementedError("Please Implement this method")
    def extractFeature(self, points, plane):
        raise NotImplementedError("Please Implement this method")

    def extractFeatureGroup(self, points, regions, planes):
        self.setupParams()
        features = []

        if len(regions) != len(planes):
            print()
            print()
            print("Warning,nr of  regions and planes dosnt match")
            print()
            print()

        for region, plane in zip(regions, planes):
            features.append(self.extractFeature(points[region], plane))

        return features

    def extractMultiFeatureGroups(self, all_points, all_regions_groups, all_plane_groups):

        features_groups = []

        ids = range(len(all_points))

        for points, regions, planes, idx in zip(all_points, all_regions_groups, all_plane_groups, ids):
            print("Extracting features from group {}".format(id))
            features_groups.append( self.extractFeatureGroup(points, regions, planes) )
        print()
        print("All features extracted")
        return features_groups
