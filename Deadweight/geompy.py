import numpy

class Point2d(object):
    _x = None
    _y = None
    
    def __init__(self,x,y):
        self._x = x;
        self._y = y;

    def __str__(self, **kwargs):
        return "({},{})".format(self._x,self._y)


class BoundingBox2d(object):
    
    _xmax = None
    _xmin = None
    _ymax = None
    _ymin = None
    _width = None
    _height = None

    def __init__(self,xmax,xmin,ymax,ymin):
        
        self._xmax = xmax
        self._xmin = xmin
        self._ymax = ymax
        self._ymin = ymin
        self._width = xmax - xmin
        self._height = ymax - ymin
        self._center = (xmin+self._width/2,ymin+self._height/2)
         
    @property
    def xmax(self):
        return self._xmax
    @property
    def xmin(self):
        return self._xmin
    @property
    def ymax(self):
        return self._ymax
    @property
    def ymin(self):
        return self._ymin
    @property
    def width(self):
        return self._width
    @property
    def heigth(self):
        return self._height
    @property
    def center(self):
        return self._center

    def to_tuple(self):
        return (self._xmax,self._xmin,self._ymax,self._ymin)
    def to_rect_coords(self):
        
        upper_left =  [self._xmin,self._ymax]
        upper_right = [self._xmax,self._ymax]
        lower_left = [self._xmin,self._ymin]
        lower_right = [self._xmax,self._ymin]
        return (upper_left,upper_right,lower_right,lower_left)
    def __str__(self):
        return "Bounding Box:\n  xmax: {}\n  xmin: {}\n  ymax: {}\n  ymin: {}\n".format(self._xmax, self._xmin, self._ymax, self._ymin)
class Polygon2d(object):
    
    _points = None
    
    def __init__(self,points: numpy.ndarray):
        
        cols = points.shape[1]
        rows = points.shape[0]
        
        if cols != 2:
            raise ValueError('Wrong number of collumns in numpy array')
        if rows < 4:
            raise ValueError('Numpy array has have 4 or more rows')
        if (points[-1,:] == points[1,:]).all():
            raise ValueError('Polygon has to be closed')
        else:
            self._points = points
    
    @property
    def points(self):
        return self._points

    def get_bounding_box(self):
        xmax = self.points[:,0].max()
        xmin = self.points[:,0].min()
        ymax = self.points[:,1].max()
        ymin = self.points[:,1].min()

        return BoundingBox2d(xmax,xmin,ymax,ymin)
    
    def __str__(self):
        return self._points.__str__()
            

        