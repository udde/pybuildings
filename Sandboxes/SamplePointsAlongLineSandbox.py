import importlib
import matplotlib
importlib.reload(matplotlib)
matplotlib.use('qt4agg')

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

#fig = plt.figure()
#ax = fig.add_subplot(111)
#line = np.array([[0,0],[1,1]])
#ax.plot(line[:,0],line[:,1])
#fig.show()

line = np.array([[0,0],[1,1],[.8,2]])
x = line[:,0]
y = line[:,1]
xvals = np.linspace(0, 1, 30)
yinterp = np.interp(xvals, x, y)
import matplotlib.pyplot as plt
plt.plot(x, y, 'o')

plt.plot(xvals, yinterp, '-x')

plt.show()


input("FAN")