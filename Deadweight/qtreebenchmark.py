from pyqtree import Index
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from LasFileHandler import LasFileHandler
import matplotlib.patches as ptc
from geompy import BoundingBox2d
import itertools
import scipy.spatial as spt
class PcPointBox(object):
    

    def __init__(self,xy,id):
        self.__id = id
        self.__point = xy
        self.__RADIUS = 10
        self.__size = self.__RADIUS*2

        self.__xmin = self.__point[0]-self.__RADIUS
        self.__xmax = self.__point[0]+self.__RADIUS
        self.__ymin = self.__point[1]-self.__RADIUS
        self.__ymax = self.__point[1]+self.__RADIUS
    @property
    def bbox(self):
        return (self.__xmin,self.__ymin,self.__xmax,self.__ymax)
    @property
    def bbox_coordinates(self):
        upper_left =  [self.__xmin,self.__ymax]
        upper_right = [self.__xmax,self.__ymax]
        lower_left = [self.__xmin,self.__ymin]
        lower_right = [self.__xmax,self.__ymin]
        return (upper_left,upper_right,lower_right,lower_left)
         
    def __str__(self):
        return "PBox id: {}\n".format(self.__id)
    
def main():
    file_path = os.path.dirname(os.path.realpath(__file__)) + '/datafromndr' + "/norrkoping.las"

    lasdata = LasFileHandler(file_path)
    lasdata.printshit()

    bb = lasdata.get_bounding_box()
   
    temp_bb = bounding_box(bb.center[0],bb.center[1],200,200)
    aoi_bb = BoundingBox2d(temp_bb[2],temp_bb[0],temp_bb[3],temp_bb[1])
    
    print(bb)
    #(xmin, ymin, xmax, ymax)
    n_boxes = 2000000


    x_vals = np.random.randint(bb.xmin,bb.xmax,(n_boxes,1))
    y_vals = np.random.randint(bb.ymin,bb.ymax,(n_boxes,1))
    centers = np.concatenate([x_vals,y_vals],1);
    #print("Centers: \n",centers);   
    spindex = Index((bb.xmin,bb.ymin,bb.xmax,bb.ymax),maxitems=100, maxdepth=100)
    

    #patches = []
    #items = []
    #start = time.time()
    #print("Inserting {} points in quad-tree...".format(n_boxes))
    
    #for i in range(0,centers.shape[0]):
    #    x = centers[i,0]
    #    y = centers[i,1]
    #    item = PcPointBox((x,y),i)
    #    #items.append(item)
        
    #    spindex.insert(item,item.bbox)
    #    #polygon = Polygon(item.bbox_coordinates, True)
    #    #patches.append(polygon)
    
    #end = time.time()
    #print("Operation took ",(end - start)*1000," ms")
    #matches  = spindex.intersect((aoi_bb.xmin,aoi_bb.ymin,aoi_bb.xmax,aoi_bb.ymax))
    #print("Matches found: ",len(matches))


    start = time.time()
    print("Inserting {} points in KD-tree...".format(n_boxes))
    tree = spt.cKDTree(centers,8)
    end = time.time()
    print("Operation took ",(end - start)*1000," ms")
    #for s in matches:
        #print(s)

    #plot_stuff(patches,centers,bb,aoi_bb)

def rect(x,y,width,height):
    w = width/2
    h = height/2

    upper_left = [x-w,y+h]
    upper_right = [x+w,y+h]
    lower_left = [x-w,y-h]
    lower_right = [x+w,y-h]
    rect = np.array([upper_left,upper_right,lower_right,lower_left])
    return rect
def bounding_box(x,y,width,height):
    xmax = x+width/2
    xmin = x-width/2
    ymax = y+height/2
    ymin = y-height/2
    return (xmin,ymin,xmax,ymax)
    
def plot_stuff(patches,centers,bb,aoi):
    fig, ax = plt.subplots(figsize=(20, 10))
    
    
    #Point boxes
    p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4)
    colors = np.full((len(patches)),0.4)
    p.set_array(np.array(colors))

    #for i in range(0,centers.shape[0]):
        #ax.annotate(i, centers[i], color='w', weight='bold', fontsize=6, ha='center', va='center')

    #Bounding Area & Area of Interest
    bounding_area = Polygon(bb.to_rect_coords(), True,alpha = None, facecolor = 'none',edgecolor = 'black', linewidth = 1,linestyle ='solid')
    area_of_interest = Polygon(aoi.to_rect_coords(), True,alpha = 0.2,facecolor = (1,0,0))

    ax.annotate('aoi', aoi.center, color='w', weight='bold', fontsize=6, ha='center', va='center')
    ax.add_patch(bounding_area)
    ax.add_patch(area_of_interest)


    ax.add_collection(p)
    ax.set_aspect('equal')
    ax.set_xlim(bb.xmin-100,bb.xmax+100)
    ax.set_ylim(bb.ymin-100,bb.ymax+100)
    ax.set_aspect('equal')
    
    plt.show()

main()


