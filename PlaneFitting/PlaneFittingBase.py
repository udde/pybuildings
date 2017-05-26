
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

    def fitMultiPlaneGroups(self, points, regions):
        print()
        print("points: ", points)
        print("regions: ", regions)
        print()

        if regions == None:
            print("warning no regions object")

        if len(points) != len(regions):
            print("warning here length dosnt match!")

        plane_groups = []

        for innner_points, inner_regions in zip(points, regions):
            planes = []
            for region in inner_regions:
                points_in_region = innner_points[region]
                plane = self.fitPlane(points_in_region)
                planes.append(plane)
            plane_groups.append(planes)
        
        return plane_groups
