
class PlaneFittingBase():
    def __init__(self):
        pass
    def setupGui(self, layout):
        raise NotImplementedError("Please Implement this method")
    def setupParams(self):
        raise NotImplementedError("Please Implement this method")
    def fitPlane(self, points):
        raise NotImplementedError("Please Implement this method")
    def fitMultiPlanes(self, points):
        self.setupParams()
        planes = []
        for points in points:
            planes.append(self.fitPlane(points))
        return planes
