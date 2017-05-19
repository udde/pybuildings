## -*- coding: utf-8 -*-
## Copyright (c) 2015, Vispy Development Team.
## Distributed under the (new) BSD License. See LICENSE.txt for more info.

#"""
#Demonstration of PolygonVisual, EllipseVisual, RectangleVisual
#and RegularPolygon
#"""

#from vispy import app
#app.use_app("pyqt5")
#import sys
#from vispy.scene import SceneCanvas
#from vispy.scene.visuals import Polygon, Ellipse, Rectangle, RegularPolygon, XYZAxis
#from vispy.color import Color

#white = Color("#ecf0f1")
#gray = Color("#121212")
#red = Color("#e74c3c")
#blue = Color("#2980b9")
#orange = Color("#e88834")

#canvas = SceneCanvas(keys='interactive', title='Polygon Example',
#                     show=True)
#v = canvas.central_widget.add_view()
#v.bgcolor = white
#v.camera = 'panzoom'

#import numpy as np
#from ShapeFileHandler import ShapeFileHandler

#read_data = ShapeFileHandler("by_get_shp/by_get").get_all_buildings()
#dxdy = read_data[2].points[0]
#polygons = []

#data = []
#for building in read_data[1:2]:

#    if building.fnr_br == '10002489162':
#        print("Found: ", building)
#        print(building.points)

#    data.append (building.points - dxdy)
#    try:
#        poly = Polygon((building.points ), color=orange, parent=v.scene)
#        print("polypos:",poly.pos)
#    except AssertionError:
#        print("COuld not triangulate object: ", building)
#        print(building.points)
#        continue
#    #polygons.append(Polygon(points, color=orange, parent=v.scene))


#axis = XYZAxis(parent=v.scene)

#if __name__ == '__main__':
#    if sys.flags.interactive != 1:
#        app.run()
