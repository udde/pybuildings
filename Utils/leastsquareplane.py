import numpy as np
import scipy.linalg
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# some 3-dim points
mean = np.array([0.0,0.0,0.0])
cov = np.array([[1.0,-0.5,0.8], [-0.5,1.1,0.0], [0.8,0.0,1.0]])
data = np.random.multivariate_normal(mean, cov, 50)

#from pca_utils import *
#points = readPointsFromFile("PolygonPoints.txt")  
#normals, curvatures = calculateNomalsCurvatures(points)
#regions = findRegions(points, normals, curvatures, maxangle=40, curvaturefactor=0.8, prints=True)
#removeWallRegions(regions, normals, wallangle=80)
##printRegions(points, regions)
#data = points[regions[0]]

# regular grid covering the domain of the data
X,Y = np.meshgrid(np.arange(-3.0, 3.0, 0.5), np.arange(-3.0, 3.0, 0.5))
XX = X.flatten()
YY = Y.flatten()

order = 1    # 1: linear, 2: quadratic
if order == 1:
    # best-fit linear plane
    A = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
    C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])    # coefficients
    
    # evaluate it on grid
    Z = C[0]*X + C[1]*Y + C[2]
    
    # or expressed using matrix/vector product
    Z = np.dot(np.c_[XX, YY, np.ones(XX.shape)], C).reshape(X.shape)

    #Plane
    a, b, c, d = C[0], C[1], -1., C[2]

def getPlane(points):
    data = points
    X,Y = np.meshgrid(np.arange(-3.0, 3.0, 0.5), np.arange(-3.0, 3.0, 0.5))
    XX = X.flatten()
    YY = Y.flatten()
    A = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
    C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])    # coefficients
    
    # evaluate it on grid
    Z = C[0]*X + C[1]*Y + C[2]
    
    # or expressed using matrix/vector product
    Z = np.dot(np.c_[XX, YY, np.ones(XX.shape)], C).reshape(X.shape)

    #Plane
    a, b, c, d = C[0], C[1], -1., C[2]

    if (c < 0):
        #print("!!!")
        #print(a,b,c,d)
        a *= -1
        b *= -1
        c *= -1
        d *= -1

    return a,b,c,d


    
    

#elif order == 2:
#    # best-fit quadratic curve
#    A = np.c_[np.ones(data.shape[0]), data[:,:2], np.prod(data[:,:2], axis=1), data[:,:2]**2]
#    C,_,_,_ = scipy.linalg.lstsq(A, data[:,2])
    
#    # evaluate it on a grid
#    Z = np.dot(np.c_[np.ones(XX.shape), XX, YY, XX*YY, XX**2, YY**2], C).reshape(X.shape)

# plot points and fitted surface
#fig = plt.figure()
#ax = fig.gca(projection='3d')
#ax.plot_surface(10*X, 10*Y, Z, rstride=10, cstride=10, alpha=0.2)
#ax.scatter(data[:,0], data[:,1], data[:,2], c='r', s=10)
#ax.scatter(0,0,30, c='black', s=50)
#plt.xlabel('X')
#plt.ylabel('Y')
#ax.set_zlabel('Z')
#ax.axis('equal')
#ax.axis('tight')
#plt.show()