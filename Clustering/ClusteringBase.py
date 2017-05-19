
class ClusteringBase():
    def __init__(self):
        self.model = {}
        self.regions = []
    
    def setupGui(self, layout):
        raise NotImplementedError("Please Implement this method")
    def setupParams(self):
        raise NotImplementedError("Please Implement this method")
    def getRegions(self, points):
        raise NotImplementedError("Please Implement this method")
    def getMultiRegions(self, points):
        self.setupParams()
        regions = []
        for points in points:
            regions.append(self.getRegions(points))
        return regions
