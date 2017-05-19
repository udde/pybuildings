import importlib
import matplotlib
importlib.reload(matplotlib)
matplotlib.use('Qt4Agg')

import os,sys,inspect
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from shapely.geometry import Polygon, Point, LineString

from Utils.ulpy import Stopwatch, AdvancedStopWatch

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from Utils.PlotAnimator import *
import Vendor.CarlosSantos.ConcaveHullSantos as csh


def main():
   
    for path in sys.path:
        path = path.encode('UTF-8')
        print(path)

    plotter = PlotAnimator()
    timer = Stopwatch()
    a_polygon = generateLetterPolygon('A')
    points = generateTestDataFromPolygon(a_polygon)
    plotter.add_point_data(points)
    plotter.show()
    plotter.draw_all_points()
    
    timer.start("Santos fixar hull")
    hull = csh.concaveHull(points, 20)

    timer.stop_latest()
    plotter.draw_extra_edges(np.array(hull))
    
    print(hull)
    x = 0


def generateTestDataFromPolygon(polygon,stepSize=2):
    points_in_polygon = None
    if 10 == 11:
        pass
    #file_name = "a_data.npy"
    #my_file = Path(file_name)
    #if my_file.is_file():
        #file exists! Praise the lauwd!!!!             
        #points_in_polygon = np.load(file_name)
    else:
        min_x = int(round(polygon.bounds[0]))
        min_y = int(round(polygon.bounds[1]))
        max_x = int(round(polygon.bounds[2]))
        max_y = int(round(polygon.bounds[3]))

        points = np.zeros([0,2])
        for x in range(min_x,max_x,stepSize):
            for y in range(min_y,max_y,stepSize):
                points = np.vstack([points, np.array([x,y]) + np.random.rand(1,2)])

        points_in_polygon = np.array([p for p in points if polygon.contains(Point(p))])
        #np.save(file_name, points_in_polygon)

    return points_in_polygon

def generateLetterPolygon(letter):
    exterior = [
        [-25, 0],
        [-5, 50.6],
        [5, 50.6],
        [25, 0],
        [14, 0],
        [9.85, 11.4],
        [-9.85, 11.4],
        [-14, 0],
        [-25, 0]
    ]
    interior = [
        [-6.76, 20],
        [0, 38.8],
        [6.76, 20]
    ]
    return Polygon(exterior, [interior])

def genereate_simple_test_data():
    a = np.array([[-0.1,-0.1],[0,1],[0,2],[0,3],[0,4],[-0.1,5.1],[1,0],[1,1],[1,2],[1,3],[1,4],[1,5]])
    b = np.array([[2,2],[2,3],[3,3],[3,2]])
    c = np.array([[4,0],[4,1],[4,2],[4,3],[4,4],[4,5],[5.1,-0.1],[5,1],[5,2],[5,3],[5,4],[5.1,5.1]])
    points = np.vstack([a,b])
    points = np.vstack([points,c])
    return points

main()
ang = input("ZzzzZZzZz...")
















