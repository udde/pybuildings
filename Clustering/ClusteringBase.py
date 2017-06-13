
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
        ids = range(len(points))
        for points, id  in zip(points, ids):
            print("Generating reagions for points group {}".format(id))
            regions.append(self.getRegions(points))
        print()
        print("All regions generated")
        return regions
