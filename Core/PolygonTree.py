from scipy.spatial.ckdtree import cKDTree
from shapely.geometry import Polygon, Point, MultiPoint
import shapely.ops
import shapely.affinity
from .GisPolygon import GisPolygon
import numpy as np
import Vendor.smallestenclodingcircle as sec
from Utils import ulpy
from Utils.ulpy import Stopwatch, AdvancedStopWatch, minimal_bounding_box
from sklearn.neighbors import NearestNeighbors

class PolygonTree(object):
    """A kd tree modified to handle 2D- Polygons"""
    def __init__(self,gis_polygon_list = None, grow_regions = False,neighbor_method = 'coordinates'):
        self.__grow_regions = grow_regions
        self.__point2polygon = np.zeros(0,dtype = np.uint16)
        self.__polygon2points = []
        self.__polygon2gis = []
        self.__all_points = np.zeros([0,2])
        self.__next_polygon_id_to_add = 0
        self.__tree_synced= False
        self.__polygons = []
        self.__polygon2region = {}
        
        self.__centroids = []

        if gis_polygon_list is not None:
            timer = Stopwatch()
            print("\n==== CREATING POLYGON TREE OF {} POLYGONS ===".format(len(gis_polygon_list)))
            timer.start("Extracting all points from all polygons")
            for polygon in gis_polygon_list:
                self.add_polygon(polygon)
            timer.stop_latest()
            self.create_necessary_datastructures()
        
    
    def add_polygon(self,gis_polygon: GisPolygon):
        polygon = gis_polygon.polygonize()[0] #TODO handle more?
        ppoints = np.array(list(polygon.exterior.coords))
        n_pppoints = ppoints.shape[0]
        start_id = self.__all_points.shape[0]
        end_id = start_id + ppoints.shape[0]
        ids = np.arange(start_id,end_id)
        self.__all_points = np.vstack([self.__all_points,ppoints])
        self.__point2polygon = np.append(self.__point2polygon,np.full(n_pppoints,self.__next_polygon_id_to_add,dtype=np.uint16))
        self.__polygon2points.append(ids)
        self.__polygon2gis.append(gis_polygon.id)
        self.__next_polygon_id_to_add += 1
        self.__tree_synced = False
        self.__polygons.append(polygon)
        #self.__centroids.append(polygon.centroid)

    def create_necessary_datastructures(self):
        N_NEIGHBOURS = 12
        timer = Stopwatch()
        timer.start("Creating kd-tree")
        self.__tree = cKDTree(self.__all_points)
        self.__tree_synced = True
        timer.stop_latest()

        timer.start("Creating neighbour tree")
        self.__nbr_tree = NearestNeighbors(n_neighbors=N_NEIGHBOURS, algorithm='ball_tree').fit(self.__all_points)
        self.__nbr_distances, self.__nbr_indices = self.__nbr_tree.kneighbors(self.__all_points)
        timer.stop_latest()

        if self.__grow_regions:
            self.__regions = self.grow_regions()

    #Takes a polygon id and returns all ids belonging to the same region
    def get_region(self,polygon_id):
        
        region = self.__polygon2region[int(polygon_id)]
        return self.__regions[region]

    def get_all_clusters_in_polygon(self,polygon: Polygon):
        polygon_ids = self.find_intersecting(polygon)
        print("\nTop dogs: ")
        print(polygon_ids)

        connected = []
        for id in polygon_ids:
            if not id in connected:
                connected += self.get_region(id)

        print("\nUnion of cluster grown from top dogs: ")
        print(connected)
        return np.array(connected), polygon_ids
    
    def get_bounding_slice_from_polygon(self,polygon: Polygon):

        polygon_ids, top_dogs = self.get_all_clusters_in_polygon(polygon)

        points = self.get_polygon_points(polygon_ids)
        convex_hull = MultiPoint(points).convex_hull

        mbb = minimal_bounding_box(convex_hull).buffer(5,cap_style=3,join_style =2)
        #gedda.show_figure()
        #gedda.draw_auxiliary_polygon(mbb,face_color = 'none')
        #gedda.update()
        polygon_ids,questionable_polygon_ids = self.find_intersecting(mbb, rectangle_mode=True,overlap_thresh = 0.9,output_crossers = True)

        return polygon_ids,questionable_polygon_ids,mbb, top_dogs

    def find_intersecting(self,polygon: Polygon,overlap_thresh = 0.9, rectangle_mode = True, output_crossers = False):
        MIN_HOUSE_DISTANCE = 0.2
        POLYGON_OVERLAP_THRESH = overlap_thresh
        #returns all ids of polygons that in someway intersects input polygon
        timer = Stopwatch()
        if not self.__tree_synced:
            self.create_necessary_datastructures()
            self.__tree_synced = True

        print("\n==== FIND INTERSECTION ===")
        timer.start("Finding smallest enclosing circle")
        #Circle C around P
        circle = sec.make_circle(list(polygon.exterior.coords))
        center = circle[0:2]
        radius = circle[2]
        timer.stop_latest()

        timer.start("Searching points within circle in kd-tree")
        #FInd points in C
        point_ids = np.array(self.__tree.query_ball_point(center,radius))  
        points = self.__all_points[point_ids]
        timer.stop_latest()
        print("Points found: {}".format(len(points)))

        #Exlude points not in P
        timer.start("Determining which points are inside polygon")
        if rectangle_mode:
            mask = ulpy.points_in_rectangle(points, polygon)
        else:
            mask = np.array([polygon.intersects(Point(x)) for x in points])
        point_ids_in = point_ids[mask]
        timer.stop_latest()
        print("Points remaining {} ".format(len(points)))
        #Find polygons belonging to points
        polygon_ids,counts = np.unique(self.__point2polygon[point_ids_in],return_counts = True)

        #Only choose polygons that are very much inside the search polygon
        polygon_id_relevance = self.polygon_coverage(polygon_ids,polygon)
        top_dog_polygon_ids = polygon_ids[polygon_id_relevance>POLYGON_OVERLAP_THRESH]
        questionable_polygon_ids = polygon_ids[polygon_id_relevance<=POLYGON_OVERLAP_THRESH]
        if output_crossers:
            return top_dog_polygon_ids,questionable_polygon_ids
        else:
            return top_dog_polygon_ids

    def intersects(self,polygon: Polygon):
        MIN_HOUSE_DISTANCE = 0.2
        POLYGON_OVERLAP_THRESH = 0.9
        #returns all ids of polygons that in someway intersects input polygon
        timer = Stopwatch()
        if not self.__tree_synced:
            self.create_necessary_datastructures()
            self.__tree_synced = True

        print("\n==== SEARCHING POLYGON INTERSECTION  ===")
        timer.start("Finding smallest enclosing circle")
        #Circle C around P
        circle = sec.make_circle(list(polygon.exterior.coords))
        center = circle[0:2]
        radius = circle[2]
        timer.stop_latest()

        timer.start("Searching points within circle in kd-tree")
        #FInd points in C
        point_ids = np.array(self.__tree.query_ball_point(center,radius))  
        points = self.__all_points[point_ids]
        timer.stop_latest()
        print("Found {} points".format(len(points)))
        
        timer.start("Determining which points are inside polygon")
        #Exlude points not in P
        mask = np.array([polygon.intersects(Point(x)) for x in points])
        point_ids_in = point_ids[mask]
        print("\npoint ids in:")
        print(point_ids_in)
        timer.stop_latest()
        print("\npolygon ids in:")
        print(self.__point2polygon[point_ids_in])
        #Find polygons belonging to points
        polygon_ids,counts = np.unique(self.__point2polygon[point_ids_in],return_counts = True)

        print("\nunique ids :")
        print(polygon_ids)

        print("\ncounts :")
        print(counts)

        #Circle around those points
        circle = sec.make_circle(self.get_polygon_points(polygon_ids))
        center = circle[0:2]
        radius = circle[2]
        point_ids_2 = np.array(self.__tree.query_ball_point(center,radius))
        polygon_ids_2,counts_2 = np.unique(self.__point2polygon[point_ids_2],return_counts = True)

        print("\npolygon ids 2:")
        print(self.__point2polygon[point_ids_2])

        print("\nunique ids 2 :")
        print(polygon_ids_2)

        print("\ncounts 2 :")
        print(counts_2)
        #points = self.__all_points[point_ids_2]

        polygon_id_relevance = self.polygon_coverage(polygon_ids_2,polygon)
        print("\ninsideness  :")
        print(polygon_id_relevance)

        top_dog_polygon_ids = polygon_ids_2[polygon_id_relevance>POLYGON_OVERLAP_THRESH]

        print("\ntop polygon ids  :")
        print(top_dog_polygon_ids)

        other_dog_polygon_ids = np.setdiff1d(polygon_ids_2,top_dog_polygon_ids)
        final_polygon_ids = top_dog_polygon_ids

        print("\nother polygon ids :")
        print(other_dog_polygon_ids)
        for tp in top_dog_polygon_ids:
            top_polygon = self.get_polygon(tp)

            for op in other_dog_polygon_ids:
                other_polygon = self.get_polygon(op)
                intersects = top_polygon.intersects(other_polygon.buffer(MIN_HOUSE_DISTANCE))
                print("{} intersects {}: \t{}".format(tp,op,intersects))
                if intersects:
                     final_polygon_ids = np.append(final_polygon_ids,op)
                     

        print("\nfinal polygon ids  :")
        final_polygon_ids = np.unique(final_polygon_ids)
        print(final_polygon_ids)
            
        return final_polygon_ids

    def find_neighbours_of(self,polygon_id):
        
        ppoints = self.get_polygon_points([polygon_id])
        pids = self.__polygon2points[polygon_id] 
        point_nbrs = self.__nbr_indices[pids].flatten()
        #point_nbrs = point_nbrs.unique()
        polygon_ids = self.__point2polygon[point_nbrs]
        polygon_ids = np.unique(polygon_ids)

        polygon_ids = list(polygon_ids)
        org_index = polygon_ids.index(polygon_id)
        del polygon_ids[org_index]
        
        return polygon_ids
        
    def grow_regions(self):
        stopwatch = AdvancedStopWatch(7,['Get neighbours','Get polygon 1','Find 1','Remove','Get polygon 2','Intersect'])
        stopwatch.start_total()
        backlog = set(np.arange(len(self.__polygon2points)))

        rounds = 0
        regions = [] #regions

        while len(backlog) != 0:

            
            start_index = backlog.pop()
            if start_index == 817:
                hej = 2
            seeds = set([start_index])
            current_region = [start_index]
            current_region_id = len(regions)
            self.__polygon2region[start_index] = current_region_id

            while len(seeds) != 0:
                #find nearest neighbours of current seed
                current_seed = seeds.pop()

                stopwatch.start_lap('Get neighbours')
                neighbours = self.find_neighbours_of(current_seed)
                stopwatch.stop_lap('Get neighbours')


                stopwatch.start_lap('Get polygon 1')
                p1 = self.get_polygon(current_seed).buffer(0.2)
                stopwatch.stop_lap('Get polygon 1')

                for j in range(len(neighbours)):
                    
                    current_neighbour = neighbours[j]
                    

                    stopwatch.start_lap('Find 1')
                    is_in_backlog = current_neighbour in backlog #constant
                    stopwatch.stop_lap('Find 1')

                    stopwatch.start_lap('Get polygon 2')
                    p2 = self.get_polygon(current_neighbour)
                    stopwatch.stop_lap('Get polygon 2')

                    stopwatch.start_lap('Intersect')
                    intersects = p1.intersects(p2)
                    stopwatch.stop_lap('Intersect')
 
                    if is_in_backlog and intersects:
                        current_region.append(current_neighbour) #O(1)
                        self.__polygon2region[current_neighbour] = current_region_id

                        stopwatch.start_lap('Remove')
                        backlog.remove(current_neighbour) #O(1)
                        stopwatch.stop_lap('Remove')

                        seeds.add(current_neighbour) #O(1)
            
            
            regions.append(current_region)
            #print("Round {}. Region: {}".format(rounds,current_region))
            rounds+=1
        stopwatch.stop_total()
        stopwatch.print_timers()
        return regions

    def get_polygon(self,polygon_id):
        
        #return Polygon(self.__all_points[self.__polygon2points[polygon_id]])
        return self.__polygons[polygon_id]
    def get_polygons(self,polygon_ids):

        return [self.get_polygon(id) for id in polygon_ids if mr_Trump.is_president == True]

    def get_polygon_points(self,polygon_ids):
        ppoints = np.zeros([0,2])
        for id in polygon_ids:
            pids = self.__polygon2points[id]
            points = self.__all_points[pids]
            ppoints = np.vstack([ppoints,points])

        return ppoints

    def polygon_coverage(self,polygon_ids,area: Polygon):
        result = []
        for id in polygon_ids:
            polygon = Polygon(self.__all_points[self.__polygon2points[id]])
            snitt = area.intersection(polygon)
            snitt_area = snitt.area
            polygon_area = polygon.area
            result.append(snitt_area/polygon_area)

        return np.array(result)
    


