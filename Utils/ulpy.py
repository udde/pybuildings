import sys
import time
import numpy as np
import shapely
from shapely.geometry import Polygon, Point
from shapely.affinity import rotate
from numpy import dot
import colorsys

class Stopwatch(object):
    def __init__(self):
        self.__timers = {}
        self.__latest = None
        self.__lap_starts = {}
        self.__lap_stops = {}
        pass
    def start(self,label):
        self.__timers[label] = time.time()
        
        self.__latest = label

    def stop_latest(self):
        lbl = self.__latest
        start = self.__timers[lbl]
        end = time.time()
        print(lbl, ":",white_spaces_until(lbl,50),(end - start)*1000," ms")


class AdvancedStopWatch(object):
    def __init__(self,n_timers,labels):
        self.__n_timers = n_timers
        self.__starts = {}
        self.__stops = {}
        self.__id2label = []
        self.__label2id = {}
        self.__meassured_tot_time = 0

        if not labels:
            auto_labels = [str(i) for i in range(n_timers)]
            self.set_labels(auto_labels)
        else:
            self.set_labels(labels)

    def set_labels(self,labels):
        if len(labels) != self.__n_timers:
            ValueError("Nr input labels differs from the number given in the constructor")
            
        for i in range(len(labels)):
            label = labels[i]
            self.__label2id[label] = i
            self.__id2label.append(label)
            self.__starts[label] = []
            self.__stops[label] = []
    def start_lap_id(self,id):
        self.__starts[self.__id2label[id]].append(time.time())
    def stop_lap_id(self,id):
        self.__stops[self.__id2label[id]].append(time.time())
    def start_lap(self,label):
        self.__starts[label].append(time.time())
    def stop_lap(self,label):
        self.__stops[label].append(time.time())
    def start_total(self):
        self.__total_start = time.time()
    def stop_total(self):
        self.__total_stop = time.time()
    def print_timers(self):
        print("\n=== STOPWATCH SUMMARY ===:")
        print("Label",white_spaces_until("LABEL",20),"LAPS",white_spaces_until("LAPS",20),"Avg time",white_spaces_until("Avg time",20),"Total Time", white_spaces_until("Total Time",20))
        for label in self.__id2label:
            self.print_lap_timer(label)
        print("TOTAL TIME: ",(self.__total_stop-self.__total_start)*1000)
        print("MEASSURED TIME: ",self.__meassured_tot_time)

    def print_lap_timer(self,label):
        starts = np.array(self.__starts[label])
        stops = np.array(self.__stops[label])
        diffs = stops-starts
        avg_time = np.mean(diffs)*1000
        n_laps = len(self.__starts[label])
        tot_time = np.sum(diffs)*1000
        self.__meassured_tot_time += tot_time
        print(label,white_spaces_until(label,20),n_laps,white_spaces_until(n_laps,20),avg_time,white_spaces_until(avg_time,20),tot_time, white_spaces_until(tot_time,20))
        
def white_spaces_until(strr,col):
    strr = str(strr)
    n_spaces = col-len(strr)
    ws = ""
    for i in range(0,n_spaces):
        ws = ws + " "
    return ws


def minimal_bounding_box(polygon: Polygon):
   

    polygon_center = polygon.centroid
    best_angle = 0
    orginal_bbox = shapely.geometry.box(*polygon.bounds)
    min_area = orginal_bbox.area
    best_bbox = orginal_bbox
    degrees = np.arange(1,360)
    for angle in degrees:
        p = rotate(polygon,angle,origin = polygon_center)
        bbox = shapely.geometry.box(*p.bounds)
        
        if bbox.area < min_area:
            best_angle = angle
            min_area = bbox.area
            best_bbox = bbox

    min_bbox = rotate(best_bbox,-best_angle,origin = polygon_center)
    return min_bbox
# Improved point in polygon test which includes edge
# and vertex points
def point_in_poly(x,y,poly):

   # check if point is a vertex
   if (x,y) in poly: return True

   # check if point is on a boundary
   for i in range(len(poly)):
      p1 = None
      p2 = None
      if i==0:
         p1 = poly[0]
         p2 = poly[1]
      else:
         p1 = poly[i-1]
         p2 = poly[i]
      if p1[1] == p2[1] and p1[1] == y and x > min(p1[0], p2[0]) and x < max(p1[0], p2[0]):
         return True
      
   n = len(poly)
   inside = False

   p1x,p1y = poly[0]
   for i in range(n+1):
      p2x,p2y = poly[i % n]
      if y > min(p1y,p2y):
         if y <= max(p1y,p2y):
            if x <= max(p1x,p2x):
               if p1y != p2y:
                  xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
               if p1x == p2x or x <= xints:
                  inside = not inside
      p1x,p1y = p2x,p2y

   if inside: return True
   else: return False

def point_in_rectangle(point, polygon):
    
    rectangle = np.array(polygon.exterior.coords)

    A = rectangle[0]
    B = rectangle[1]
    C = rectangle[2]
    P = point

    #vectors
    AB = B-A
    AP = P-A
    BC = C-B
    BP = P-B

    #Use dot-product to determine if the point is to the left and withi in range of the two CCW lines spanning the rectangle
    return 0 <= dot(AB, AP) <= dot(AB, AB) and 0 <= dot(BC, BP) <= dot(BC, BC)
      
def points_in_rectangle(points,polygon):

    rectangle = np.array(polygon.exterior.coords)
    
    A = rectangle[0]
    B = rectangle[1]
    C = rectangle[2]

    #Constants
    AB = B-A
    BC = C-B

    n_points = points.shape[0]

    #Point vectors
    A_rep = np.repeat(np.array([A]),n_points,0)
    B_rep = np.repeat(np.array([B]),n_points,0)

    AP = points-A_rep
    BP = points-B_rep

    #dot(AB, AP) 
    dot_AB_AP = np.einsum('i,ji',AB,AP)
    dot_BP_BC = np.einsum('i,ji',BC,BP)

    first = (dot_AB_AP >= 0) & (dot_AB_AP <= dot(AB, AB))
    second = (dot_BP_BC >= 0) & (dot_BP_BC <= dot(BC, BC))

    return first & second
def distinct_colors(n_colors):
    import colorsys
    N = n_colors
    HSV_tuples = [(x*1.0/N, 0.7, 0.7) for x in range(N)]
    RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
    return RGB_tuples