import importlib
import matplotlib
importlib.reload(matplotlib)
matplotlib.use('Qt4Agg')
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Utils.PlotAnimator import *
"""
=========================
Simple animation examples
=========================

This example contains two animations. The first is a random walk plot. The
second is an image animation.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


points = np.array([[0,0],[0,1],[0,2],[1,1.8],[2,2],[2,1],[2,0],[1,0]])
a = np.array([[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[1,1],[1,2],[1,3],[1,4],[1,5],[1,6]])
b = np.array([[2,2],[2,3],[3,3],[3,2]])
c = np.array([[4,1],[4,2],[4,3],[4,4],[4,5],[4,6],[5,1],[5,2],[5,3],[5,4],[5,5],[5,6]])
points = np.vstack([a,b])
points = np.vstack([points,c])

ids = np.arange(points.shape[0])
plot = PlotAnimator()
plot.add_point_data(points)

#ids = [1,3,2,0]
plot.show()


plot.draw_all_points()
input("Press Enter to continue")

for i in range(len(ids)-1):
    this_id = ids[i]
    next_id = ids[i+1]
    plot.edge((this_id,next_id),EdgeStyle.NORMAL)

input("Press Enter to continue")
plot.delete_edge((2,3))

input("Press Enter to continue")
plot.edge((2,3),EdgeStyle.DEACTIVATED)

input("Press Enter to continue")
plot.point(1,PointStyle.CHOSEN)
input("Press Enter to continue")