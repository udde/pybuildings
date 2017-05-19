import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import struct
import numpy as np
import shapely.geometry

from Deadweight.Plot3DHandler import Plot3DHandler
from Deadweight.Plot2DHandler import Plot2DHandler
from Deadweight.geompy import Point2d, Polygon2d, BoundingBox2d
from Utils.tempy import get_polygon_from_geojson
from Utils.tempy import get_peking_fanz
from Core import ShapeFileHandler2, BuildingFootprint, OpenGLObject, Solidator, LasFileHandler


np.set_printoptions(suppress=True)

#INIT READERS
solidator = Solidator()
sfh = ShapeFileHandler2("by_get_shp/by_get",'ay')
lasdata = LasFileHandler("datafromndr/norrkoping.las",8)
las_bb = shapely.geometry.box(*lasdata.bounds)
shape_bb = shapely.geometry.box(*sfh.bounds)

lasdata.printshit()

intersection = las_bb.intersection(shape_bb)
union = las_bb.union(shape_bb)

# POLYGONS
building_footprint = sfh.get_by_id(1999)
polygon = building_footprint.polygonize()[0]

bfps = sfh.get_all()

map = Plot2DHandler()
map.add_building_footprints(bfps)
map.add_area(las_bb)
map.add_area(shape_bb)
map.add_area(union)
map.add_area(intersection,a = 0.3,lwidth = 0, fcolor = 'r')
map.set_axis_limits(union)
map.show()


# POINT CLOUD
lasdata.read_points()
points,points_out,z_range = lasdata.get_points_from_polygon(polygon)

inliers, outliers = solidator.reject_outliers(points)

solid = solidator.extrude(inliers,building_footprint,z_range[0])
terrain,tri_ter = solidator.ground_maker(points_out,building_footprint)

#plotter = Plot3DHandler()


#plotter.show()

plotter = Plot3DHandler()
plotter.add_point_cloud(terrain,'b')
plotter.add_wall_polygons(tri_ter.get_triangles_as_polygons(),a=0.6,color ='g')
plotter.add_point_cloud(inliers,'b')
plotter.add_point_cloud(outliers,'r')
plotter.add_polygon(polygon,z_range[0])
plotter.add_wall_polygons(solid.get_triangles_as_polygons())
#plotter.add_normals(solid.vertex_normals,solid.triangle_vertices)
plotter.show()




