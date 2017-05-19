import os
import sys
import vispy
import numpy as np
import math


from vispy import app, gloo
app.use_app('pyqt5')
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *

from vispy.util.transforms import perspective, translate, rotate
from vispy.geometry import meshdata as md
from vispy.geometry import generation as gen

from BuildingList import *

#from cube import cube

from vispy.scene import SceneCanvas
from vispy.scene.visuals import Polygon, Ellipse, Rectangle, RegularPolygon, XYZAxis
from vispy.color import Color
white = Color("#ecf0f1")
gray = Color("#121212")
red = Color("#e74c3c")
blue = Color("#2980b9")
orange = Color("#e88834")

read_data = bfp.bfps_from_shape_file()
dxdy = read_data[0].points[0]
polygons = []
print(type(read_data[0].fnr_br))

data = []
rest = []
for building in read_data[:100]:

    if building.fnr_br == '10002489162':
        print("Found: ", building)
        print(building.points)

    data.append (building.points - dxdy)
    try:
        poly = Polygon((building.points - dxdy), color=orange)
    except AssertionError:
        print("COuld not triangulate object: ", building)
        print(building.points)
        rest.append(building)
        continue
    polygons.append(poly)

#print(polygons)
axis = XYZAxis()



read_data = bfp.bfps_from_shape_file()
#for item in read_data:
    #print(item, item.points)
#print(read_data[0].points)
dataa = read_data[0].points

dx = np.mean(dataa[:,0])
dy = np.mean(dataa[:,1])
dataa = dataa - [dx, dy]


VERT_SHADER = """ // simple vertex shader
attribute vec2 a_position;

uniform vec2 u_pan;
uniform vec2 u_scale;

void main (void) {

    vec2 position_tr = u_scale * (a_position + u_pan);

    gl_Position = vec4(position_tr, 0.0, 1.0);
}
"""

FRAG_SHADER = """ // simple fragment shader
uniform vec4 u_color;
void main()
{
    gl_FragColor = u_color;
}
"""

class Wrapper(QWidget):
    def __init__(self):

        self.canvas = MapCanvas()
        self.set


class MapCanvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')

        # Create program
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)

        

        # Set uniform and attribute
        self.program['u_color'] = 0.2, 1.0, 0.4, 1

        self.program['u_pan'] = (0., 0.)
        self.program['u_scale'] = (1., 1.)


        gloo.set_viewport(0,0,256,256)
        gloo.set_clear_color('white')

        self.show()

    #def on_resize(self, event):
    #    width, height = event.physical_size
    #    gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        gloo.clear()
        
        for building in read_data:
            points = building.points - [dx, dy]
            self.program['a_position'] = gloo.VertexBuffer( points )
            self.program.draw('triangles')

        md = None
        for poly in polygons:
            md = poly.mesh.mesh_data
            self.program['a_position'] = gloo.VertexBuffer( np.float32(md.get_vertices())  - [dx, dy])
            faces = md.get_faces()
            self.program.draw(mode='triangles', indices=gloo.IndexBuffer(faces))

            #vertic = gloo.VertexBuffer( np.float32(md.get_vertices())  - [dx, dy])
            #indices = gloo.IndexBuffer(faces)
            #self.program.bind(vertic)
            #self.program.draw('triangles', indices)
        
        #self.program['a_position'] = gloo.VertexBuffer(vPosition2)
        #self.program.draw('triangle_strip')

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.physical_size)

    #def on_draw(self, event):
    #    gloo.clear(color=(0.0, 0.0, 0.0, 1.0))
    #    self.program.draw('line_strip')

    def _normalize(self, x_y):
        x, y = x_y
        w, h = float(self.size[0]), float(self.size[1])
        return x/(w/2.)-1., y/(h/2.)-1.

    def on_mouse_move(self, event):
        
        if event.is_dragging:
            #print("HELO")
            x0, y0 = self._normalize(event.press_event.pos)
            x1, y1 = self._normalize(event.last_event.pos)
            x, y = self._normalize(event.pos)
            dx, dy = x - x1, -(y - y1)
            button = event.press_event.button

            pan_x, pan_y = self.program['u_pan']
            scale_x, scale_y = self.program['u_scale']

            if button == 1:
                self.program['u_pan'] = (pan_x+dx/scale_x, pan_y+dy/scale_y)
            elif button == 2:
                scale_x_new, scale_y_new = (scale_x * math.exp(2.5*dx),
                                            scale_y * math.exp(2.5*dy))
                self.program['u_scale'] = (scale_x_new, scale_y_new)
                self.program['u_pan'] = (pan_x -
                                         x0 * (1./scale_x - 1./scale_x_new),
                                         pan_y +
                                         y0 * (1./scale_y - 1./scale_y_new))
            self.update()

    def on_mouse_wheel(self, event):
        #print("YOYO")
        dx = np.sign(event.delta[1])*.05
        scale_x, scale_y = self.program['u_scale']
        scale_x_new, scale_y_new = (scale_x * math.exp(2.5*dx),
                                    scale_y * math.exp(2.5*dx))
        self.program['u_scale'] = (scale_x_new, scale_y_new)
        self.update()


    #    self.program.bind(gloo.VertexBuffer(data))

    #    self.program['u_pan'] = (0., 0.)
    #    self.program['u_scale'] = (1., 1.)

    #    gloo.set_viewport(0, 0, *self.physical_size)

    #    gloo.set_state(clear_color=(1, 1, 1, 1), blend=True,
    #                   blend_func=('src_alpha', 'one_minus_src_alpha'))

    #    self.show()

    #def on_resize(self, event):
    #    gloo.set_viewport(0, 0, *event.physical_size)

    #def on_draw(self, event):
    #    gloo.clear(color=(0.0, 0.0, 0.0, 1.0))
    #    self.program.draw('line_strip')

    #def _normalize(self, x_y):
    #    x, y = x_y
    #    w, h = float(self.size[0]), float(self.size[1])
    #    return x/(w/2.)-1., y/(h/2.)-1.

    #def on_mouse_move(self, event):
    #    if event.is_dragging:
    #        x0, y0 = self._normalize(event.press_event.pos)
    #        x1, y1 = self._normalize(event.last_event.pos)
    #        x, y = self._normalize(event.pos)
    #        dx, dy = x - x1, -(y - y1)
    #        button = event.press_event.button

    #        pan_x, pan_y = self.program['u_pan']
    #        scale_x, scale_y = self.program['u_scale']

    #        if button == 1:
    #            self.program['u_pan'] = (pan_x+dx/scale_x, pan_y+dy/scale_y)
    #        elif button == 2:
    #            scale_x_new, scale_y_new = (scale_x * math.exp(2.5*dx),
    #                                        scale_y * math.exp(2.5*dy))
    #            self.program['u_scale'] = (scale_x_new, scale_y_new)
    #            self.program['u_pan'] = (pan_x -
    #                                     x0 * (1./scale_x - 1./scale_x_new),
    #                                     pan_y +
    #                                     y0 * (1./scale_y - 1./scale_y_new))
    #        self.update()

    #def on_mouse_wheel(self, event):
    #    dx = np.sign(event.delta[1])*.05
    #    scale_x, scale_y = self.program['u_scale']
    #    scale_x_new, scale_y_new = (scale_x * math.exp(2.5*dx),
    #                                scale_y * math.exp(2.5*dx))
    #    self.program['u_scale'] = (scale_x_new, scale_y_new)
    #    self.update()

if __name__ == '__main__':
    c = MapCanvas()
    app.run()
