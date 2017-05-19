# -*- coding: utf-8 -*-

import importlib
import numpy as np
from vispy import app, gloo
from vispy.gloo import Program, VertexBuffer, IndexBuffer
from vispy.util.transforms import perspective, translate, rotate, ortho
from vispy.geometry import create_cube, PolygonData, polygon

import numpy as np
from vispy.color import Color
import triangle

from Deadweight.ShapeFileHandler import ShapeFileHandler
import Utils.vector_utils as vut
import Gui.Cam3D as Cam3D

vertex = """
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 pv;

attribute vec2 position;
//attribute vec2 texcoord;
//attribute vec3 normal;
//attribute vec4 color;

varying vec4 v_color;
void main()
{
    //mat4 x = projection * view;
    vec4 color = vec4(0.0, 0.8, 0.5, 1.0);
    v_color = color;
    gl_Position = projection * view * model * vec4(position, 0.0, 1.0);
}
"""

fragment = """
varying vec4 v_color;
void main()
{
    gl_FragColor = vec4(0.21, 0.35, 0.71, 1.0);
}
"""
fragment_active = """
varying vec4 v_color;
void main()
{
    gl_FragColor = vec4(0.44, 0.57, 0.75, 1.0);
}
"""


class Map2D(app.Canvas):

    def __init__(self, data_handler, parent):

        app.Canvas.__init__(self, size=(512, 512), title='map', keys='interactive')

        self.__parent__ = parent
        self.__data_handler = data_handler

        ##read building data
        ##fetch single building
        #building1 = self.__sh.get_single_at_id(1595) #nya
        #building2 = self.__sh.get_single_at_id(1999) #stryk
        #building3 = self.__sh.get_single_at_id(1886) #strykbrada
        #building4 = self.__sh.get_single_at_id(1722) #Gula vid bron
        #building5 = self.__sh.get_single_at_id(1723) #
        ##and its vertices
        #verts1 = building1.gl_ready_vertices()
        #verts2 = building2.gl_ready_vertices()
        #verts3 = building3.gl_ready_vertices()
        #verts4 = building4.gl_ready_vertices()
        #verts5 = building5.gl_ready_vertices()

        self.all_buildings = self.__data_handler.get_all_buildings()

        all_pos = self.all_buildings[0].gl_ready_vertices()

        for building in self.all_buildings[1:]:
            all_pos = np.vstack((all_pos, building.gl_ready_vertices()))

        abets = self.__data_handler.get_single_at_id(1886)
        abets = abets.gl_ready_vertices()

        #Problem: 977, 1061, 1342(tva stora hal), 1389(hal), 1393(hal), 1434(hal), 1327(rese)
        #Error 1072, 1327(rese). 1472(?!?!?), 1504(!?!?!)
        #for j in range(100000):
        #    for i in range(1503, 1504):
            #print("----------------\n----------------",i)
                #all_pos = all_buildings[i].gl_ready_vertices()
        

        self.translate_by = np.mean(abets[:],0)
        self.scale = 1.0

        all_pos = (all_pos - self.translate_by) * self.scale

        allverts = np.zeros(len(all_pos), [('position', np.float32, 2)])
        allverts['position'] = all_pos

        self.selectedverts = np.zeros(len(abets), [('position', np.float32, 2)])
        self.selectedverts['position'] = (abets - self.translate_by) * self.scale
        
        self.vertices = VertexBuffer(allverts)
        self.selectedvertices = VertexBuffer(self.selectedverts)
        #self.indices = IndexBuffer(I)

        # Build program
        self.program = Program(vertex, fragment)
        self.program.bind(self.vertices)

        self.cam2 = Cam3D.Camera([0,0,250], [0,0,0], [0,1,0], 45.0, self.size[0] / float(self.size[1]), 0.001, 10000.0, is_2d=True)
        
        # Build view, model, projection & normal
        self.program['model'] =  np.eye(4, dtype=np.float32) #models are at palce from beginnings?
        self.program['model'] = np.transpose(vut.rotx(-10))

        self.program['view'] = self.cam2.view
        
        projection = perspective(45.0, self.size[0] / float(self.size[1]), 1.0, 1000.0)
        self.program['projection'] = projection

        self.phi, self.theta = 0, 0
        
        gloo.set_state(clear_color=(0.70, 0.70, 0.7, 1.00), depth_test=True)
        self.set_selected([1999])
        self.activate_zoom()
        self.timer = app.Timer('auto', self.on_timer, start=True)
        
        self.show()
    
        
    def set_selected(self, ids):
        
        #building = self.__data_handler.get_single_at_id(id)
        #verts2 = building.gl_ready_vertices()
        
        self.selectedverts = np.zeros(0, [('position', np.float32, 2)])
        
        for id in ids:
            building = self.__data_handler.get_single_at_id(id)
            verts = building.gl_ready_vertices()
            data = np.zeros(len(verts), [('position', np.float32, 2)])
            data['position'] = (verts - self.translate_by) * self.scale
            self.selectedverts = np.concatenate([self.selectedverts, data])

        #self.selectedverts['position'] = (verts2 - self.translate_by) * self.scale
        self.selectedvertices = VertexBuffer(self.selectedverts)

        
        
        
        
        
        selected_pos = np.mean(self.all_buildings[id].points, 0) - self.translate_by
        self.cam2.translate_to(selected_pos)
        self.program['view'] = self.cam2.view
        
        self.update()


    def on_mouse_press(self, event):
        
        if event.button == 1:
            
            self.cam2.is_move = True
            self.cam2.is_rotate = False
        
        if event.button == 2:
            
            self.cam2.is_move = False
            self.cam2.is_rotate = True
        
        self.cam2.prev_mouse_pos = event.pos


    def on_mouse_release(self, event):
        
        self.cam2.is_move = False
        self.cam2.is_rotate = False


    def on_mouse_move(self, event):

        if self.cam2.is_move:

            self.cam2.translate2d( -1*np.array(event.pos - self.cam2.prev_mouse_pos, dtype=np.float32 ))
            self.program['view'] = self.cam2.view
            self.update()

        elif self.cam2.is_rotate:

            self.cam2.rotx(-1*np.array((event.pos - self.cam2.prev_mouse_pos))[1:2])
            self.cam2.roty(-1*np.array((event.pos - self.cam2.prev_mouse_pos))[0:1])
            self.program['view'] = self.cam2.view
            self.update()

        self.cam2.prev_mouse_pos = event.pos


    def on_mouse_wheel(self, event):
        
        self.cam2.scale(event.delta[1])
        self.program['view'] = self.cam2.view
        self.update()


    def on_draw(self, event):
        
        gloo.clear(color=True, depth=True)

        self.program.set_shaders(vertex, fragment_active)
        self.program.bind(self.selectedvertices)
        self.program.draw('triangles')

        self.program.set_shaders(vertex, fragment)
        self.program.bind(self.vertices)
        self.program.draw('triangles')


    def on_resize(self, event):
        
        self.activate_zoom()


    def activate_zoom(self):
        
        gloo.set_viewport(0, 0, *self.physical_size)
        projection = perspective(45.0, self.size[0] / float(self.size[1]), 1.0, 10000.0)
        self.program['projection'] = projection
        self.update()


    def on_timer(self, event):
        
        self.update()
    

    def on_resize(self, event):

        self.activate_zoom()


    def on_key_press(self, event):

        modifiers = [key.name for key in event.modifiers]
        print('Key pressed - text: %r, key: %s, modifiers: %r' % (
            event.text, event.key.name, modifiers))


    def on_key_release(self, event):

        modifiers = [key.name for key in event.modifiers]
        print('Key released - text: %r, key: %s, modifiers: %r' % (
            event.text, event.key.name, modifiers))


if __name__ == '__main__':
    
    map = Map2D()
    app.run()
