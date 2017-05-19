
class FeatureExtractionBase():
    def __init__(self):
        pass
    def setupGui(self, layout):
        raise NotImplementedError("Please Implement this method")
    def setupParams(self):
        raise NotImplementedError("Please Implement this method")
    def extractFeature(self, points):
        raise NotImplementedError("Please Implement this method")
    def extractMultiFeatures(self, points):
        self.setupParams()
        features = []
        for points in points:
            planes.append(self.extractFeature(points))
        return planes
