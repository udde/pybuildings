#import os
#import sys
#import vispy
#import numpy as np
#from PyQt5 import QtWidgets, QtCore, QtGui
#from PyQt5.QtWidgets import *

#from vispy import app, gloo
#app.use_app('pyqt5')
#from vispy.util.transforms import perspective, translate, rotate
#from vispy.geometry import meshdata as md
#from vispy.geometry import generation as gen

#from BuildingList import *

#from cube import cube


#vert = """
#// Uniforms
#// ------------------------------------
#uniform   mat4 u_model;
#uniform   mat4 u_view;
#uniform   mat4 u_projection;
#uniform   vec4 u_color;

#// Attributes
#// ------------------------------------
#attribute vec3 a_position;
#attribute vec4 a_color;
#attribute vec3 a_normal;

#// Varying
#// ------------------------------------
#varying vec4 v_color;

#void main()
#{
#    v_color = a_color * u_color;
#    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
#}
#"""


#frag = """
#// Varying
#// ------------------------------------
#varying vec4 v_color;

#void main()
#{
#    gl_FragColor = v_color;
#}
#"""
#from vispy.util import 
#class MapCanvas(app.Canvas):
#    """description of class"""
#    def __init__(self):
#        app.Canvas.__init__(self, keys='interactive', size=(800, 600))

#        self.vertices, self.filled, self.outline = cube()
#        self.filled_buf = gloo.IndexBuffer(self.filled)
#        self.outline_buf = gloo.IndexBuffer(self.outline)

#        self.program = gloo.Program(vert, frag)
#        self.program.bind(gloo.VertexBuffer(self.vertices))

#        self.view = translate((0, 0, -5))
#        self.model = np.eye(4, dtype=np.float32)

#        gloo.set_viewport(0, 0, self.physical_size[0], self.physical_size[1])
#        self.projection = perspective(45.0, self.size[0] /
#                                      float(self.size[1]), 2.0, 10.0)

#        self.program['u_projection'] = self.projection

#        self.program['u_model'] = self.model
#        self.program['u_view'] = self.view

#        self.theta = 0
#        self.phi = 0

#        gloo.set_clear_color([0.9,0.98,0.9])
#        gloo.set_state('opaque')
#        gloo.set_polygon_offset(1, 1)

#        self._timer = app.Timer('auto', connect=self.on_timer, start=True)

#        self.show()

#    # ---------------------------------
#    def on_timer(self, event):
#        self.theta += .5
#        self.phi += .5
#        self.model = np.dot(rotate(self.theta, (0, 1, 0)),
#                            rotate(self.phi, (0, 0, 1)))
#        self.program['u_model'] = self.model
#        self.update()

#    # ---------------------------------
#    def on_resize(self, event):
#        gloo.set_viewport(0, 0, event.physical_size[0], event.physical_size[1])
#        self.projection = perspective(45.0, event.size[0] /
#                                      float(event.size[1]), 2.0, 10.0)
#        self.program['u_projection'] = self.projection

#    # ---------------------------------
#    def on_draw(self, event):
#        gloo.clear()

#        # Filled cube

#        gloo.set_state(blend=False, depth_test=True, polygon_offset_fill=True)
#        self.program['u_color'] = 1, 1, 1, 1
#        self.program.draw('triangles', self.filled_buf)

#        # Outline
#        gloo.set_state(blend=True, depth_test=True, polygon_offset_fill=False)
#        gloo.set_depth_mask(False)
#        self.program['u_color'] = 0, 0, 0, 1
#        self.program.draw('lines', self.outline_buf)
#        gloo.set_depth_mask(True)


