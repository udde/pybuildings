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
from scipy.spatial import ConvexHull
from sklearn.neighbors import NearestNeighbors
import msvcrt
from Utils.PlotAnimator import *
import math
from scipy.spatial.ckdtree import cKDTree
from pathlib import Path


class EdgeNeighbors():
    def __init__(self,edge_list):
        self.edge_list = edge_list
        self.neighbor_table = self.create_neighbor_table(edge_list)
    
    def create_neighbor_table(self,edge_list):
        n_edges = len(edge_list)
        last_id = n_edges-1
        ids = np.arange(n_edges)
        neighbor_table = np.ones([n_edges,2],dtype = np.int32)*-1

        for i in range(n_edges):
            if i==0:
                predecessor = last_id
                successor = i+1
            elif i == last_id:
                predecessor = i-1
                successor = 0
            else:
                predecessor = i-1
                successor = i+1
            neighbor_table[i,:] = [predecessor,successor]

        return neighbor_table

    def replace_edge_with_two_new(self,edge_to_replace,first_new_edge,second_new_edge):
        self.neighbor_table = np.vstack([self.neighbor_table,[-1,-1]])
        self.neighbor_table = np.vstack([self.neighbor_table,[-1,-1]])
        
        #Connecty existing edges to new
        pred_effected_edge = self.neighbor_table[edge_to_replace,0]
        succ_effected_edge = self.neighbor_table[edge_to_replace,1]
        self.neighbor_table[pred_effected_edge,1] = first_new_edge
        self.neighbor_table[succ_effected_edge,0] = second_new_edge

        self.neighbor_table[first_new_edge,0] = pred_effected_edge #predecessor
        self.neighbor_table[first_new_edge,1] = second_new_edge

        self.neighbor_table[second_new_edge,0] = first_new_edge
        self.neighbor_table[second_new_edge,1] = succ_effected_edge

        #Delete replaces edge
        self.neighbor_table[edge_to_replace,:] = [-1.-1]

    def insert_edge_pre(self,edge_point_ids,edge_id):
        self.neigbor_table[edge_id]
    def get_predecessor(self,id):
        return self.neighbor_table[id,0]

    def get_successor(self,id):
        return self.neighbor_table[id,1]

def main():
    #Generate test data
    a_polygon = generateLetterPolygon('A')
    points = generateTestDataFromPolygon(a_polygon)
    #points = genereate_simple_test_data()

    #Run the algorithm
    concaveList = algorithm(points)
    

def algorithm(point_data):

    timer = Stopwatch()
    plotter = PlotAnimator()
    
    

    #1. PARAMETERS
    THRESHOLD = 3
    SAMPLE_DIST = 2
    N_NEIGHBOURS = 14
    #2. INITIALIZE
    #2.1 Convex Hull & Edge Neighbors & kdTree
    n_points = point_data.shape[0]
    hull = ConvexHull(point_data)
    convex_list = make_convex_list(hull.vertices) #contains point pairs
    concave_list = list(convex_list)
    nrbs = EdgeNeighbors(convex_list)
    kd_tree = cKDTree(point_data)

    point_ids = set(np.arange(point_data.shape[0]))
    inner_point_ids = point_ids-set(np.array(convex_list).flatten())
    





    plotter.add_point_data(point_data)
    plotter.draw_all_points()
    #plotter.draw_extra_points(sample_points,PointStyle.LOWLIGHT)
    plotter.show()
    plotter.edge_multi(convex_list,EdgeStyle.NORMAL)
    DEBUG = False

    print("\nPoint data: ")
    for i, point in enumerate(point_data):
        print("{}: {}".format(i,point))

    print("\nConvex list:\n {}".format(convex_list))
    #1. Digging convex
    #input("FFS")
    n_starting_edges = hull.simplices.shape[0]
    print("Nr of starting edges: {}".format(n_starting_edges))
    stopwatch = AdvancedStopWatch(7,['Nearest inne point','Calculations','Split and remove','Remove deleted'])
    stopwatch.start_total()
    
    counter = 0
    current_egde_id = 0
    while current_egde_id < len(concave_list) and counter < 100000:
        counter = counter +1
        edge_point_ids = concave_list[current_egde_id] #get point ids of current edge
        edge_points = point_data[edge_point_ids] # the actual coordinates

        #DEBUG
        if current_egde_id == 6:
            #DEBUG = False
            pass
            
        print('Round {}/{}: [{} & {}]'.format(current_egde_id,len(concave_list),edge_point_ids[0],edge_point_ids[1]))
        
        sample_points = sample_edge(edge_points[0,:],edge_points[1,:],SAMPLE_DIST)


        nbr_ids = set()
        for p in sample_points:
            nbr_ids.update(set(kd_tree.query_ball_point(p,SAMPLE_DIST*2))) 
        
        if DEBUG:
            #plotter.draw_extra_points(sample_points,PointStyle.LOWLIGHT)
            plotter.edge_multi(concave_list,EdgeStyle.DEACTIVATED)
            plotter.point_multi(nbr_ids,PointStyle.HIGHLIGHT)
            
             
        nbr_ids.discard(edge_point_ids[0])
        nbr_ids.discard(edge_point_ids[1])
        nbr_ids.intersection_update(inner_point_ids)

        print("\tPotential pk: {}".format(nbr_ids))
        
        #find the nearest inner point from the current edge
        neighbor_edge_1 = concave_list[nrbs.get_predecessor(current_egde_id)]
        neighbor_edge_2 = concave_list[nrbs.get_successor(current_egde_id)]
        stopwatch.start_lap('Nearest inne point')

        pk_id, pk_dist = find_nearest_inner_point_not_closer_to_neighbor_edges(point_data,nbr_ids,edge_points,neighbor_edge_1,neighbor_edge_2)
        stopwatch.stop_lap('Nearest inne point')

        if pk_id==-1:
            print("\t => TRUE NEIGHBOR TROUBLE! Done with this edge")
            current_egde_id = current_egde_id+1
            if DEBUG:
                plotter.reset_all_points()
                plotter.delete_all_edges()
            continue
        pk = point_data[pk_id]
        stopwatch.start_lap('Calculations')
        edge_length = np.linalg.norm(edge_points[0]-edge_points[1])
        dd = decision_distance(pk,edge_points)
        #distance_pk_edge = point_to_edge_distance(point
        value_to_compare = edge_length/dd
        stopwatch.stop_lap('Calculations')



        if DEBUG:
            print("\tDistance to pk: {}".format(pk_dist))
            print("\tEdge length (eh): {}".format(edge_length))
            print("\tDecision distance (dd): {}".format(dd))
            print("\tValue to compare: {}".format(value_to_compare))
            plotter.edge(edge_point_ids,EdgeStyle.CHOSEN)
            plotter.edge(neighbor_edge_1,EdgeStyle.LOWLIGHT)
            plotter.edge(neighbor_edge_2,EdgeStyle.LOWLIGHT)
            plotter.point(pk_id,PointStyle.CHOSEN)
            input("\t...enter to proceed....")

        if value_to_compare > THRESHOLD:
            stopwatch.start_lap('Split and remove')
            #Split and remove
            concave_list.append(np.array([edge_point_ids[0],pk_id],dtype = np.int32))
            concave_list.append(np.array([pk_id,edge_point_ids[1]],dtype = np.int32))
            nrbs.replace_edge_with_two_new(current_egde_id,len(concave_list)-2,len(concave_list)-1)
            concave_list[current_egde_id] = np.array([-1,-1])
            
            inner_point_ids.remove(pk_id)
            stopwatch.stop_lap('Split and remove')

            if DEBUG:
                print("\t => Split and remove!")
                #plotter.delete_edge(edge_point_ids)
                #plotter.edge(concave_list[-1],EdgeStyle.NORMAL)
                #plotter.edge(concave_list[-2],EdgeStyle.NORMAL)
            
        else:
            #Save edge and move on
            print("\t => Done with this edge")
            #pass

        if DEBUG:
            #plotter.delete_edge(neighbor_edge_1)
            #plotter.delete_edge(neighbor_edge_2)
            plotter.reset_all_points()
            plotter.delete_all_edges()

        current_egde_id = current_egde_id+1

    stopwatch.start_lap('Remove deleted')
    concave_list_2 = [pair for pair in concave_list if pair[0] != -1]

    stopwatch.stop_lap('Remove deleted')
    stopwatch.stop_total()
    stopwatch.print_timers()
    plotter.edge_multi(concave_list_2,EdgeStyle.LOWLIGHT)
    
    return concave_list_2

def find_nearest_inner_point_not_closer_to_neighbor_edges(point_data,inner_point_ids,edge_points,neighbor_edge_1,neighbor_edge_2):
    pk_dist = math.inf
    pk_id = -1
    pid_and_dist = []
    

    for id in inner_point_ids:
        dist = point_to_edge_distance(point_data[id],edge_points)
        center_point = edge_points[0] + (edge_points[1]-edge_points[0])*0.5
        center_dist = np.linalg.norm(point_data[id]-center_point)
        weighted_dist = dist+center_dist*0.1
        pid_and_dist.append([id,dist,weighted_dist])

    pid_and_dist = np.array(pid_and_dist)
    pid_and_dist = pid_and_dist[pid_and_dist[:,2].argsort()] #sort on distance
    
    
    count = 0;
    for pair in pid_and_dist:
        #check neighbor edges distances
        count = count+1
        
        d1 = point_to_edge_distance(point_data[np.int(pair[0])],point_data[neighbor_edge_1])
        d2 = point_to_edge_distance(point_data[np.int(pair[0])],point_data[neighbor_edge_2])
        pk_dist = pair[1]
        pk_is_closer_to_neighbor_edges = (d1 < pk_dist or d2 < pk_dist)

        
        if not pk_is_closer_to_neighbor_edges:
            pk_id = pair[0]
            pk_not_found = False
            break
    print("\tFinding pk took {} of {} tries".format(count,len(pid_and_dist)))

    return pk_id,pk_dist

def sample_edge(p1,p2,SAMPLE_DIST):
        #2.2 Create sample points
    sample_points = np.zeros([0,2])
   
    v = p2 - p1
    v_norm = v/np.linalg.norm(v)
    steps = np.arange(0, np.linalg.norm(v),SAMPLE_DIST)
        
    new_points = np.multiply(np.tile(v_norm,[len(steps),1]),np.reshape(steps,[len(steps),1]))+p1
    sample_points = np.vstack([sample_points,new_points])
    sample_points = np.vstack([sample_points,p2])
    return sample_points

def decision_distance(p,q):
    #q: list of points
    dist_list = distance_to_multiple_points(p,q)
    return np.min(dist_list)

def distance_to_multiple_points(single_point,point_array):
    many_single_points = np.tile(single_point,(point_array.shape[0],1))
    return distance_between_point_arrays(many_single_points,point_array)

def distance_between_point_arrays(point_array_1,point_array_2):
    #a numpy way of doing eucledian distnace between multiple points i 2D
    return np.sqrt(np.power(point_array_1[:,0]-point_array_2[:,0],2) + np.power(point_array_1[:,1]-point_array_2[:,1],2))

def point_to_edge_distance(point,edge_points):
    return Point(point).distance(LineString(edge_points))

def pointToTriangleDistance(point,triangle_points):
    return Point(point).distance(Polygon(triangle_points))


def plot_coords(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, color='#999999', zorder=1)

def generateTestDataFromPolygon(polygon,stepSize=2):
    points_in_polygon = None
    file_name = "a_data.npy"
    my_file = Path(file_name)
    if my_file.is_file():
        #file exists! Praise the lauwd!!!!             
        points_in_polygon = np.load(file_name)
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
        np.save(file_name, points_in_polygon)

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
def make_convex_list(vertices):
    convex_list = []
    for i in range(len(vertices)-1):
        
        convex_list.append(np.array([vertices[i],vertices[i+1]]))
    convex_list.append(np.array([vertices[-1],vertices[0]]))
    #return np.array(convex_list,dtype=np.int32)
    return convex_list

main()
ang = input("ZzzzZZzZz...")