
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

        if len(points) != len(planes):
            print()
            print()
            print("Warning,nr of  points and planes dosnt match")
            print()
            print()

        for points, plane in zip(points, planes):
            features.append(self.extractFeature(points, plane))

        return features

    def extractMultiFeatureGroups(self):
        pass