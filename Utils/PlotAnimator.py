#import importlib
#import matplotlib
#importlib.reload(matplotlib)
#matplotlib.use('Qt4Agg')


import numpy as np
import matplotlib.pyplot as plt
import msvcrt
class Colors():
    LIGHT_GREY = '#f2f2f2'
    GREY = '#c5cbd6'
    ORANGE = '#e89061'
    FIRE = '#ff630f'
    YELLOW = '#ffe41e'
    MAGENTA = '#d658ef'
    PLUM = '#84578e'

class EdgeStyle():
    DEACTIVATED = {"color": Colors.GREY, "linestyle": 'dashed'}
    NORMAL = {"color": Colors.GREY, "linestyle": 'solid'}
    HIGLIGHT = {"color": Colors.YELLOW, "linestyle": 'solid',"linewidth": 2.0}
    LOWLIGHT = {"color": Colors.PLUM, "linestyle": 'solid'}
    CHOSEN = {"color": Colors.FIRE, "linestyle": 'solid',"linewidth": 2.0}

class PointStyle():
    DEACTIVATED = {"linestyle": 'None',"markeredgewidth":0,"color": Colors.GREY, "marker": 'x'}
    NORMAL = {"linestyle": 'None',"markeredgewidth":0, "color": Colors.GREY, "marker": 'o'}
    HIGHLIGHT = {"linestyle": 'None',"markeredgewidth":0,"color": Colors.YELLOW, "marker": 'o'}
    LOWLIGHT = {"linestyle": 'None',"markeredgewidth":1,"color": Colors.MAGENTA, "markeredgecolor":Colors.MAGENTA, "marker": 'x'}
    CHOSEN = {"linestyle": 'None',"markeredgewidth":1,"color": Colors.FIRE, "marker": 'o',"markersize": 10}

class PlotAnimator(object):
    """description of class"""


    def __init__(self):
        self.__fig = plt.figure()
        self.__ax = self.__fig.add_subplot(111)
        self.__points = np.zeros([0,2])
        
        self.__edges = dict()
        self.__point_handles = dict()
        plt.ion()


    def add_point_data(self,points):
        self.__points = np.vstack([self.__points,points])
        xmax = np.max(self.__points[:,0]) + 1
        xmin = np.min(self.__points[:,0]) - 1
        ymax = np.max(self.__points[:,1]) + 1
        ymin = np.min(self.__points[:,1]) - 1
        self.__ax.set_xlim([xmin,xmax])
        self.__ax.set_ylim([ymin,ymax])

    def edge(self,point_ids, style = EdgeStyle.NORMAL):
        point_ids = tuple(point_ids)
        points = self.__points[np.array(point_ids)]
        if not point_ids in self.__edges:
            
            list_of_line_handles = self.__ax.plot(points[:,0],points[:,1],**style)
            self.__edges[point_ids] = list_of_line_handles[0]
        else:
            self.delete_edge(point_ids)
            list_of_line_handles = self.__ax.plot(points[:,0],points[:,1],**style)
            self.__edges[point_ids] = list_of_line_handles[0]
    def edge_multi(self,edge_list,style = EdgeStyle.NORMAL):
        for edge in edge_list:
            self.edge(tuple(edge),style)

    def delete_edge(self,point_ids):
        point_ids = tuple(point_ids)
        line_handle = self.__edges[point_ids]
        line_handle.remove()
        del self.__edges[point_ids]
    def delete_all_edges(self):
        for key, val in list(self.__edges.items()):
            val.remove()
            del self.__edges[key]

    def draw_all_points(self,style = PointStyle.NORMAL):
        self.__ax.plot(self.__points[:,0],self.__points[:,1],**style)

    def draw_extra_edges(self,points):
        
        self.__ax.plot(points[:,0],points[:,1])
    def draw_extra_points(self,points,style = PointStyle.DEACTIVATED):
        self.__ax.plot(points[:,0],points[:,1],**style)
    def point(self,point_id,style = PointStyle.NORMAL):
        
        point = self.__points[point_id]

        if point_id in self.__point_handles:
            self.delete_point(point_id)
                        
        list_of_point_handles = self.__ax.plot(point[0],point[1],**style)
        self.__point_handles[point_id] = list_of_point_handles[0]
    def point_multi(self,point_ids,style = PointStyle.NORMAL):
        for pid in point_ids:
            self.point(pid,style)
    def reset_all_points(self):
        all_point_ids = np.arange(len(self.__points))
        
        self.point_multi(all_point_ids,PointStyle.NORMAL)
    def delete_point(self,point_id):
        
        point_handle = self.__point_handles[point_id]
        point_handle.remove()
        del self.__point_handles[point_id]
    def start_round(self):
        pass
    def show(self):
        self.__fig.show()
    def wait_for_input(self):
        input_char = msvcrt.getch()