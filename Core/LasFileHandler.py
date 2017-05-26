import os
import sys
import struct
import numpy as np
#import geompy
import array
import time
import math
import psutil
import locale
import Vendor.smallestenclodingcircle as sec
locale.setlocale(locale.LC_ALL, '')

from scipy.spatial.ckdtree import cKDTree
#from geompy import Polygon2d
#from geompy import BoundingBox2d
from Utils.tempy import printProgress
from Utils.ulpy import Stopwatch
from Utils.ulpy import point_in_poly
from pathlib import Path


import Utils.ulpy as ulpy

from shapely.geometry import Point, Polygon

class LasFileHandler(object):
    """description of class"""
    __file_path = None
    __file_signature = None
    __file_source_ID = None
    __global_encodding = None
    __guid_shit = None #TODO: fix 
    __version_major = None
    __version_minor = None
    __system_identifier = None
    __generating_software = None
    __file_creation_day_of_year = None
    __file_creation_year = None
    __header_size = None
    __offset_to_point_data = None
    __nr_of_variable_length_records = None
    __point_data_format_id = None
    __point_data_record_length = None
    __nr_of_point_records = None
    __nr_of_points_by_return = None 
    __XYZ_scale_factor = None
    __XYZ_offset = None
    __XYZ_max_min = None

    __current_lod = 0
    __nr_of_trees = None
    __trees = None
    __point_data = None
    __translation_point = None

    N_LONGS_PER_POINT_RECORD = 7

    def __init__(self,file_path,nr_sub_trees = None):

        self.__file_path = file_path
        self.read_header()
        
        if nr_sub_trees == None:
            self.__nr_of_trees = self.calculate_nr_of_trees()
        else:
            #Check if power of 2
            bit_string = "{0:b}".format(int(nr_sub_trees))
            if bit_string.count('1') != 1 or bit_string[0] != '1' or nr_sub_trees > 32:
                raise ValueError('Nr of sub-trees has to be power of 2 and less than 33')
            else:
                self.__nr_of_trees = nr_sub_trees

        self.__trees = [] #contains kd-trees
        self.__point_data = [] #contains xyz to corresponding tree.
        cx = self.__XYZ_max_min[0]+(self.__XYZ_max_min[0]-self.__XYZ_max_min[1])/2
        cy = self.__XYZ_max_min[2]+(self.__XYZ_max_min[2]-self.__XYZ_max_min[3])/2
        self.__translation_point = (cx,cy)
        vmem = psutil.virtual_memory()
        print("\n==== LAS-READER INFO ====")
        print("Availble memory: {0:.2f} GB".format(vmem.available/math.pow(1024,3)))
        needed_memory = self.__nr_of_point_records * self.__point_data_record_length*2
        print("Memory needed for file: {0:.2f} GB".format(needed_memory/math.pow(1024,3)))
        print("Total number of points records: {0:n}".format(self.__nr_of_point_records))
        print("Number of separate trees: ", self.__nr_of_trees)
        print("Dataset center point: ",self.__translation_point)

    def get_bounding_box(self):
        xmax = self.__XYZ_max_min[0]
        xmin = self.__XYZ_max_min[1]
        ymax = self.__XYZ_max_min[2]
        ymin = self.__XYZ_max_min[3]
        return BoundingBox2d(xmax,xmin,ymax,ymin)
    @property
    def bounds(self):
        xmax = self.__XYZ_max_min[0]
        xmin = self.__XYZ_max_min[1]
        ymax = self.__XYZ_max_min[2]
        ymin = self.__XYZ_max_min[3]
        return xmin,ymin,xmax,ymax #shapely and shapefile follows this format
    def translation_point(self):
        return self.__translation_point
    def get_points_from_polygon(self, polygon: Polygon,rectangle_mode = False):
        timer = Stopwatch()
        if type(polygon) != type(Polygon):
            TypeError("polygon has to be shapely Polygon") 
        point_temp = np.array(list(polygon.exterior.coords))
        print("\n==== SEARCHING FOR POINTS IN POLYGON ({} POINTS) ===".format(point_temp.shape[0]))
        timer.start("Finding smallest enclosing circle")

        circle = sec.make_circle(list(polygon.exterior.coords))
        
        center = circle[0:2]
        radius = circle[2]
        
        timer.stop_latest()
        str = "Finding points in {} sub-trees".format(len(self.__trees))
        timer.start(str)
        points = np.zeros([0,3])
        for i in range(0,len(self.__trees)):
            ids = self.__trees[i].query_ball_point(center,radius+5) 
            points_temp = [self.__point_data[i][k] for k in ids]
            points = np.vstack([points, self.__point_data[i][ids]])
            
        timer.stop_latest()
        print("Found {} points".format(len(points)))
        z_range = (points[:,2].min(),points[:,2].max())
        timer.start("Determining which points are inside polygon")
        
        #points[:] = [x for x in points if polygon.intersects(Point(x))]
        if rectangle_mode:
            mask = ulpy.points_in_rectangle(points[:,0:2], polygon)
        else:
            mask = np.array([polygon.intersects(Point(x)) for x in points])

        points_in = points[mask]
        points_out = points[mask==False]
        
        timer.stop_latest()
        
        print("Now only {} points remain".format(len(points_in)))
        #print(np.array(points))
        return points_in,points_out,z_range
   
    def calculate_nr_of_trees(self):
        n_points = self.__nr_of_point_records
        dividor = 2
        while n_points/dividor > 3000000:
            dividor = math.pow(dividor,2)
        return dividor
    @property
    def current_lod(self):
        return self.__current_lod
    def make_index_list(self,tree_id):
       
        upper_bound = self.__nr_of_point_records*self.N_LONGS_PER_POINT_RECORD
        step_size = self.__nr_of_trees*self.N_LONGS_PER_POINT_RECORD
        ids =  np.arange(tree_id*self.N_LONGS_PER_POINT_RECORD,upper_bound,step_size,dtype = np.int)
        return ids
    def read_points(self):
        # lod 0 = no points read => next tree to read
        next_tree_to_make = self.__current_lod
        print("\n==== READING TREE DETAIL LEVEL {} of {} ===".format(self.__current_lod,int(self.__nr_of_trees-1)))
        tree,data = self.make_kdtree(self.make_index_list(next_tree_to_make),self.__current_lod, self.__nr_of_trees)
        self.__trees.append(tree)
        self.__point_data.append(data)
        self.__current_lod+=1

    def read_header(self):
        print("Reading LAS-file header...")
        f = open(self.__file_path, "rb")

        bytes = f.read(4)
        self.__file_signature = bytes.decode("utf-8")
        self.__file_source_ID = int.from_bytes(f.read(2),'little', signed = False)
        self.__global_encodding = int.from_bytes(f.read(2),'little', signed = False)
        self.__guid_shit= f.read(16).decode("utf-8")
        self.__version_major= int.from_bytes(f.read(1),'little', signed = False)
        self.__version_minor= int.from_bytes(f.read(1),'little', signed = False)
        self.__system_identifier = f.read(32).decode("utf-8")
        self.__generating_software = f.read(32).decode("utf-8")
        self.__file_creation_day_of_year = int.from_bytes(f.read(2),'little', signed = False)
        self.__file_creation_year = int.from_bytes(f.read(2),'little', signed = False)
        self.__header_size = int.from_bytes(f.read(2),'little', signed = False)
        self.__offset_to_point_data = int.from_bytes(f.read(4),'little', signed = False)
        self.__nr_of_variable_length_records = int.from_bytes(f.read(4),'little', signed = False)

        bytes = f.read(1)

        char = struct.unpack('B', bytes)

        xcv = int.from_bytes(bytes,'little', signed = False) #TODO: this is supposed to be char
        
        self.__point_data_format_id = xcv

        blabla = int.from_bytes(f.read(2), sys.byteorder, signed = False)
        self.__point_data_record_length = blabla

        
        tmpint = int.from_bytes(f.read(4), sys.byteorder, signed = False)
        self.__nr_of_point_records = tmpint
        

        
        #first = struct.unpack('5L',f.read(20))

        tmplist = [
            int.from_bytes(f.read(4),sys.byteorder, signed = False),
            int.from_bytes(f.read(4),sys.byteorder, signed = False),
            int.from_bytes(f.read(4),sys.byteorder, signed = False),
            int.from_bytes(f.read(4),sys.byteorder, signed = False),
            int.from_bytes(f.read(4),sys.byteorder, signed = False)
        ]


        x = "break"

        self.__nr_of_points_by_return = tuple(tmplist)

        self.__XYZ_scale_factor = np.array(struct.unpack('3d',f.read(24)))
        self.__XYZ_offset = np.array(struct.unpack('3d',f.read(24)))
        self.__XYZ_max_min = struct.unpack('6d',f.read(48))

        f.close()
    def read_point_data_from_begining(self,nr_of_points):
        f = open(self.__file_path, "rb")
        f.seek(self.__offset_to_point_data)
        print("")
        print("=== READING POINT DATA TEST===")
        print("XYZ scale factor:", self.__XYZ_scale_factor)
        for n in range(0,nr_of_points):
            bytes = f.read(12)
            raw = struct.unpack('3l',bytes)
            record = np.array(raw)
            xyz = record * self.__XYZ_scale_factor + self.__XYZ_offset
            bytes_to_vask = self.__point_data_record_length-12
            bytes = f.read(bytes_to_vask)          
        f.close()
   
    
    def make_kdtree(self,ids,current_lod,n_trees):
        timer = Stopwatch() 
        point_data = None
        n_iterations = len(ids)

        dataset_file_name = "{}_{}_{}_{}{}.npy".format(self.__file_creation_year, self.__file_creation_day_of_year, self.__nr_of_point_records,n_trees,current_lod)

        my_file = Path(dataset_file_name)
        if my_file.is_file():
            #file exists! Praise the lauwd!!!!
            timer.start("Reading point data from file")             
            point_data= np.load(dataset_file_name)
            timer.stop_latest()
        else:
            #file does not exist

            #Open file and discard header
            f = open(self.__file_path, "rb")
            f.seek(self.__offset_to_point_data)

            #Read points from file
            timer.start("Reading all {} points from file".format(self.__nr_of_point_records))
            all_data = array.array('i')
            all_data.fromfile(f, self.__nr_of_point_records*7)
            timer.stop_latest()


            #Move to list (version 3)
            timer.start("Moving {} data points to a list".format(n_iterations))
            offset =  np.array([self.__XYZ_offset[0],self.__XYZ_offset[1],self.__XYZ_offset[2]])
            scale_factor = np.array([self.__XYZ_scale_factor[0],self.__XYZ_scale_factor[1],self.__XYZ_scale_factor[2]]) 
            raw_points = np.array([(all_data[id], all_data[id +1],all_data[id +2]) for id in ids])
            print("Scale factor: {}".format(scale_factor))
            print("Offset: {}".format(offset))
            point_data = raw_points[:,:]*scale_factor+offset
            timer.stop_latest()

            #Save points to file
            timer.start("Saving point data to file")
            np.save(dataset_file_name, point_data)
            timer.stop_latest()

        xy_point_data = point_data[:,0:2]
        #Create KDTree
        timer.start("Creating kd-tree with {} points".format(n_iterations))
        tree = cKDTree(xy_point_data,leafsize = 24,compact_nodes = False,balanced_tree = False)
        timer.stop_latest()

        #timer.start("Re-arranging data")
        #for i in range(n_iterations):
        #    point_data[i].append(z_vals[i])
        #timer.stop_latest()
        #print("Nr of points in tree: ",tree.n)
        
        return tree,point_data
    def printshit(self):
        print("\n====== LAS FILE HEADER DATA ======")
        print("File Signature:", self.__file_signature)
        print("File Source ID:", self.__file_source_ID)
        print("Global Encoding:", self.__file_source_ID)
        print("Version: {}.{}".format(self.__version_major,self.__version_major))
        print("System Identifier:", self.__system_identifier)
        print("Generating Software:", self.__generating_software)
        print("File Creation Day of Year:", self.__file_creation_day_of_year)
        print("File Creation Year:", self.__file_creation_year)
        print("Header Size:", self.__header_size)
        print("Offset (in bytes) to point data:", self.__offset_to_point_data)
        print("Number of Variable Length Records:", self.__nr_of_variable_length_records)
        print("Point Data Format ID:", self.__point_data_format_id)
        print("Point Data Record Length:", self.__point_data_record_length)
        print("Number of point records:", self.__nr_of_point_records)
        print("Number of points by return:", self.__nr_of_points_by_return)
        print("XYZ scale factor:", self.__XYZ_scale_factor)
        print("XYZ offset:", self.__XYZ_offset)
        print("XYZ min max:", self.__XYZ_max_min)
        print("")
    def read_variable_length_records(self):
        f = open(self.__file_path, "rb")
        f.seek(self.__header_size)
        
        #VARIABLE LENGTH RECORDS
        f.seek(2) #Reserved

        for x in range(0,self.__nr_of_variable_length_records):
            #TODO: save this
            print("\tVariable length record: ",  x)
            vlr_user_id = f.read(16).decode("utf-8")
            vlr_record_id = int.from_bytes(f.read(2),'little', signed = False)
            vlr_length_after_header = int.from_bytes(bytes,'little', signed = False)
            vlr_description = f.read(32).decode("utf-8")

            print("\tDescription:", VLR_description);

            #Read actual data
            bytes = f.read(VLR_length_after_header)
        f.close()
   
    
