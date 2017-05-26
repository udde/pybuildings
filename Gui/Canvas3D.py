import numpy as np
import Utils.vector_utils as vut
import math
from vispy import app, gloo, gloo
from vispy.gloo import Program, VertexBuffer, IndexBuffer
from vispy.util.transforms import perspective, translate, rotate
from vispy.color import Color
from vispy.gloo import gl
import Gui.Cam3D as Cam3D
from vispy.geometry import create_cube
from Utils.ulpy import distinct_colors
from Utils.pca_utils import * 
from Core import Solidator
import copy
from PlaneFitting.PlaneFittingBase import PlaneFittingBase
from PlaneFitting.LeastSquarePlaneFitting import LeastSquarePlaneFitting

pf = LeastSquarePlaneFitting()

vertex = """
//#version 200 es

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
attribute vec3 position;
//attribute vec2 texcoord;
attribute vec3 normal;
attribute vec3 color;

varying vec3 v_color;

varying vec3 v_norm;
varying vec3 v_pos;

void main()
{
    vec4 position = projection * view * model * vec4(position,1.0);
    v_pos = position.xyz;
    
    v_color = color;
    v_norm = normal;
    gl_Position = position;

    //gl_PointSize = 50000.0f / gl_Position.z;
}
"""

fragment = """

varying vec3 v_color;
varying vec3 v_norm;
varying vec3 v_pos;
uniform float u_alpha;

void main()
{
    
    vec3 l0 = normalize(vec3( 1.0, 1.0, 0.0 ));
    vec3 l1 = normalize(vec3( -1.0, -1.0, 0.5 ));

    vec3 norm = v_norm;

    float amb = 0.4;

    float d0 = 0.7 * min(dot( norm, l0 ), 1.0);
    float d1 = 0.7 * min(dot( norm, l1 ), 1.0);
    
    vec3 color = v_color;
    gl_FragColor.xyz = (amb + d0 + d1 ) * color;
    gl_FragColor.a = u_alpha;
}
"""


vert = """
#version 120

// Uniforms
// ------------------------------------
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_linewidth;
uniform float u_antialias;
uniform float u_size;

// Attributes
// ------------------------------------
attribute vec3  a_position;
attribute vec4  a_fg_color;
attribute vec4  a_bg_color;
attribute float a_size;

// Varyings
// ------------------------------------
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_size;
varying float v_linewidth;
varying float v_antialias;

void main (void) {
    v_size = a_size * u_size;
    v_linewidth = u_linewidth;
    v_antialias = u_antialias;
    v_fg_color  = a_fg_color;
    v_bg_color  = a_bg_color;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
    gl_PointSize = v_size + 2*(v_linewidth + 1.5*v_antialias);
}
"""

frag = """
#version 120

// Constants
// ------------------------------------


// Varyings
// ------------------------------------
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_size;
varying float v_linewidth;
varying float v_antialias;

// Functions
// ------------------------------------

// ----------------
float disc(vec2 P, float size)
{
    float r = length((P.xy - vec2(0.5,0.5))*size);
    r -= v_size/2;
    return r;
}

// ----------------
float arrow_right(vec2 P, float size)
{
    float r1 = abs(P.x -.50)*size + abs(P.y -.5)*size - v_size/2;
    float r2 = abs(P.x -.25)*size + abs(P.y -.5)*size - v_size/2;
    float r = max(r1,-r2);
    return r;
}

// ----------------
float ring(vec2 P, float size)
{
    float r1 = length((gl_PointCoord.xy - vec2(0.5,0.5))*size) - v_size/2;
    float r2 = length((gl_PointCoord.xy - vec2(0.5,0.5))*size) - v_size/4;
    float r = max(r1,-r2);
    return r;
}

// ----------------
float clober(vec2 P, float size)
{
    const float PI = 3.14159265358979323846264;
    const float t1 = -PI/2;
    const vec2  c1 = 0.2*vec2(cos(t1),sin(t1));
    const float t2 = t1+2*PI/3;
    const vec2  c2 = 0.2*vec2(cos(t2),sin(t2));
    const float t3 = t2+2*PI/3;
    const vec2  c3 = 0.2*vec2(cos(t3),sin(t3));

    float r1 = length((gl_PointCoord.xy- vec2(0.5,0.5) - c1)*size);
    r1 -= v_size/3;
    float r2 = length((gl_PointCoord.xy- vec2(0.5,0.5) - c2)*size);
    r2 -= v_size/3;
    float r3 = length((gl_PointCoord.xy- vec2(0.5,0.5) - c3)*size);
    r3 -= v_size/3;
    float r = min(min(r1,r2),r3);
    return r;
}

// ----------------
float square(vec2 P, float size)
{
    float r = max(abs(gl_PointCoord.x -.5)*size,
                  abs(gl_PointCoord.y -.5)*size);
    r -= v_size/2;
    return r;
}

// ----------------
float diamond(vec2 P, float size)
{
    float r = abs(gl_PointCoord.x -.5)*size + abs(gl_PointCoord.y -.5)*size;
    r -= v_size/2;
    return r;
}

// ----------------
float vbar(vec2 P, float size)
{
    float r1 = max(abs(gl_PointCoord.x -.75)*size,
                   abs(gl_PointCoord.x -.25)*size);
    float r3 = max(abs(gl_PointCoord.x -.5)*size,
                   abs(gl_PointCoord.y -.5)*size);
    float r = max(r1,r3);
    r -= v_size/2;
    return r;
}

// ----------------
float hbar(vec2 P, float size)
{
    float r2 = max(abs(gl_PointCoord.y -.75)*size,
                   abs(gl_PointCoord.y -.25)*size);
    float r3 = max(abs(gl_PointCoord.x -.5)*size,
                   abs(gl_PointCoord.y -.5)*size);
    float r = max(r2,r3);
    r -= v_size/2;
    return r;
}

// ----------------
float cross(vec2 P, float size)
{
    float r1 = max(abs(gl_PointCoord.x -.75)*size,
                   abs(gl_PointCoord.x -.25)*size);
    float r2 = max(abs(gl_PointCoord.y -.75)*size,
                   abs(gl_PointCoord.y -.25)*size);
    float r3 = max(abs(gl_PointCoord.x -.5)*size,
                   abs(gl_PointCoord.y -.5)*size);
    float r = max(min(r1,r2),r3);
    r -= v_size/2;
    return r;
}


// Main
// ------------------------------------
void main()
{
    float size = v_size +2*(v_linewidth + 1.5*v_antialias);
    float t = v_linewidth/2.0-v_antialias;

    float r = disc(gl_PointCoord, size);
    // float r = square(gl_PointCoord, size);
    // float r = ring(gl_PointCoord, size);
    // float r = arrow_right(gl_PointCoord, size);
    // float r = diamond(gl_PointCoord, size);
    // float r = cross(gl_PointCoord, size);
    // float r = clober(gl_PointCoord, size);
    // float r = hbar(gl_PointCoord, size);
    // float r = vbar(gl_PointCoord, size);


    float d = abs(r) - t;
    if( r > (v_linewidth/2.0+v_antialias))
    {
        discard;
    }
    else if( d < 0.0 )
    {
       gl_FragColor = v_fg_color;
    }
    else
    {
        float alpha = d/v_antialias;
        alpha = exp(-alpha*alpha);
        if (r > 0)
            gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
        else
            gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
    }
}
"""

class BuildingObject():

    def __init__(self, idx, points, bfp, solid):
        self.idx = idx
        self.original_points = points
        self.points = np.copy(points)
        self.bfp = bfp
        self.solid = solid
        self.regions = []



class Canvas3D(app.Canvas):

    def __init__(self, data_handler, parent, currentdata):
        
        app.Canvas.__init__(self, size=(512, 512), title='3d view', keys='interactive')

        self.current_data = currentdata
        self.render_params = {
            'transparent': False,
            'top_dogs_only': False,
            'draw_polygons': True,
            'draw_points': True
        }
        self.__parent__ = parent
        self.__data_handler = data_handler
        self.__inliers, self.__outliers = 0, 0
        self.__render_points_params = {
                'inliers': False,
                'outliers': False
        }

        self.setupCanvas()

        #Render objects 
        self.render_objects = []

        #Data... SLICE
        self.__bfps = 0
        self.__points = 0
        self.__solids = 0
        self.__property_area = 0
        self.__mbb = 0
        self.__offset = 0
        self.__top_dogs = 0

        #self.__parent__.set_slice(1343)

        self.show()

    def setupCanvas(self):
            #Create the camera         
            self.__camera = Cam3D.Camera([0 ,-200, 150], [0,0,0], [0,0,1], 45.0, self.size[0] / float(self.size[1]), 0.01, 1000.0, is_2d=False)

            #Build and setup the glprogram for rendering the models
            self.program_solids = Program(vertex, fragment)
        
            self.program_solids['model'] = vut.rotx(90)
            self.program_solids['model'] = np.eye(4, dtype=np.float32)
            self.program_solids['view'] = self.__camera.view
            self.program_solids['u_alpha'] = np.float32(0.6)

            # build and setup glprogram for rendering the points
            self.program_points = gloo.Program(vert, frag)

            self.program_points['u_linewidth'] = 1.0
            self.program_points['u_antialias'] = 1.0
            self.program_points['u_model'] = np.eye(4, dtype=np.float32)
            self.program_points['u_view'] = self.__camera.view
            self.program_points['u_size'] = 0.3 +  0.8 /self.__camera.zoom_factor

            #Some aditional drawing variables/setups
            self.__draw_model_transparent = False
            self.context.set_clear_color(Color([0.7,0.7,0.7,1.0]))
            self.__theta = 0
            self.__phi = 0
            self.timer = app.Timer('auto', self.on_timer, start=True)
            self.activate_zoom()
       
            
    def readTheData(self):
        self.__bfps = self.current_data['bfps']
        self.__points = np.array(self.current_data['points'], copy=True)

        self.__solids = self.current_data['solids']
        self.__property_area = self.current_data['property_area']
        self.__mbb = self.current_data['mbb']
        self.__top_dogs = self.current_data['top_dogs']
        self.__top_dog_points = self.current_data['top_dog_points'] 

        self.__offset = np.mean(self.__property_area.points,0)
        
             
    def setCanvasData(self):
        #self.__bfps, self.__points, self.__solids, self.__property_area, self.__mbb, self.__top_dogs = self.__data_handler.get_slice_from_property(property_id)
        
        self.readTheData()
        for points in self.__points:
            points[:,0:2] -= self.__offset

        self.setup_points_selected = self.setup_points
        self.setup_polygons_selected = self.setup_bfps
        self.updateCanvas()

        self.reset_camera()
        self.update()

        self.__parent__.focus_building_id = self.__top_dogs

    def updateCanvas(self):
        self.setup_points_selected()
        self.setup_polygons_selected()
        self.update()

    def points(self):
        self.setup_points_selected = self.setup_points;
        self.readTheData()
        self.setup_points()
    
    def bfps(self):
        self.setup_polygons_selected = self.setup_bfps;

    def features(self):
        self.setup_polygons_selected = self.setup_features;
        self.setup_polygons_selected()
        self.update()

    def regions(self):
        self.setup_points_selected = self.setup_regions;
        self.slice_regions = self.current_data['regions']
        self.top_dogs_regions = self.current_data['top_dog_regions']
        self.setup_regions()

    def planes(self):
        self.setup_points_selected = self.setup_regions;
        self.all_planes = self.current_data['planes']
        self.top_dog_planes = self.current_data['top_dog_planes']
        self.setup_planes()

    def clearPoints(self):
        print("Clear Points")
        verts = np.zeros(0, [('position', np.float32, 3),('normal', np.float32, 3),('color', np.float32, 3)]) #start empty...
        self.program_points.bind(VertexBuffer(verts))
        self.update()

    def setup_bfps(self):

        verts = np.zeros(0, [('position', np.float32, 3),('normal', np.float32, 3),('color', np.float32, 3)]) #start with an empty array
        colors = distinct_colors(2)
        
        for i in range(len(self.__solids)):
            if self.render_params['top_dogs_only']:
                if self.__bfps[i].id in self.__top_dogs:
                    get_verts = self.__solids[i].get_gl_vertex_data(self.__offset)
                    data = np.zeros(len(get_verts), [('position', np.float32, 3),('normal', np.float32, 3),('color', np.float32, 3)])
                    data['position'] = get_verts['position']
                    data['normal'] = get_verts['normal']
                    data['color'] = colors[1]
                    verts = np.concatenate([verts, data])
            else:
                get_verts = self.__solids[i].get_gl_vertex_data(self.__offset)
                data = np.zeros(len(get_verts), [('position', np.float32, 3),('normal', np.float32, 3),('color', np.float32, 3)])
                data['position'] = get_verts['position']
                data['normal'] = get_verts['normal']
                if self.__bfps[i].id in self.__top_dogs:
                        data['color'] = colors[1]
                else:
                    data['color'] = colors[0]
                verts = np.concatenate([verts, data])

        self.program_solids.bind(VertexBuffer(verts))

    def setup_features(self):
        verts = np.zeros(0, [('position', np.float32, 3),('normal', np.float32, 3),('color', np.float32, 3)]) #start with an empty array
        colors = distinct_colors(2)
        
        features = self.current_data['top_dog_features']

        for i in range(len(features)):
            if self.render_params['top_dogs_only']:
                if self.__bfps[i].id in self.__top_dogs:
                    get_verts = self.__solids[i].get_gl_vertex_data(self.__offset)
                    data = np.zeros(len(get_verts), [('position', np.float32, 3),('normal', np.float32, 3),('color', np.float32, 3)])
                    data['position'] = get_verts['position']
                    data['normal'] = get_verts['normal']
                    data['color'] = colors[1]
                    verts = np.concatenate([verts, data])
            else:
                get_verts = self.__solids[i].get_gl_vertex_data(self.__offset)
                data = np.zeros(len(get_verts), [('position', np.float32, 3),('normal', np.float32, 3),('color', np.float32, 3)])
                data['position'] = get_verts['position']
                data['normal'] = get_verts['normal']
                if self.__bfps[i].id in self.__top_dogs:
                        data['color'] = colors[1]
                else:
                    data['color'] = colors[0]
                verts = np.concatenate([verts, data])

        self.program_solids.bind(VertexBuffer(verts))

    def setup_points(self):
        
        self.setup_points_selected = self.setup_points

        if self.render_params['top_dogs_only']:
            all_points = np.array(self.__top_dog_points)
        else:
            all_points = np.array(self.__points)
         
        total_n = sum([len(points) for points in all_points])
        data = np.zeros(total_n, [('a_position', np.float32, 3),
                        ('a_bg_color', np.float32, 4),
                        ('a_fg_color', np.float32, 4),
                        ('a_size', np.float32, 1)])

        start = 0
        for i in range(len(all_points)):
            points = all_points[i]
            n = len(points)
            if self.__bfps[i].id in self.__top_dogs:
                data[start:start+n]['a_bg_color'] = np.array([0.6, 0.92, 0.8, 0.5], dtype=np.float32)
            else:
                data[start:start+n]['a_bg_color'] = np.array([0.7,0.7,0.9,0.5], dtype=np.float32)

            data[start:start+n]['a_fg_color'] = 0, 0, 0, 1
            data[start:start+n]['a_size'] = 10
            data[start:start+n]['a_position'] = points
            start += n
        
        self.program_points.bind(gloo.VertexBuffer(data))
        self.update()
    
    def setup_planes(self):
        
        self.setup_points_selected = self.setup_regions
        
        all_points = np.array(self.__points)
        
        self.selected_planes = self.all_planes
        if self.render_params['top_dogs_only']:
            self.selected_planes = self.top_dog_planes

        #all_points = copy.copy(all_points)
        all_plane_points = copy.deepcopy(all_points)
        print("running setup planes with {} points".format(len(all_plane_points)))
        n_regions = len(self.selected_regions)

        #PREPARE DATA ARRAY
        total_n = 0
        current_regions = 0
        for i in range(len(all_plane_points)):
            points = all_plane_points[i]
            
            if self.render_params['top_dogs_only']:

                if self.__bfps[i].id in self.__top_dogs :
                    n_in_region = sum([len(region) for region in self.selected_regions[current_regions]])
                    total_n += len(points)
                    current_regions += 1

            else:
                total_n += len(points) 
        ##PREPARE DATA ARRAY
        #total_n = 0
        #current_regions = 0
        #for i in range(len(all_plane_points)):
        #    points = all_plane_points[i]
            
        #    if self.__bfps[i].id in self.__top_dogs :
        #        n_in_region = sum([len(region) for region in self.selected_regions[current_regions]])
        #        total_n += len(points)
        #        current_regions += 1
            
        #    elif self.render_params['top_dogs_only'] == False:
        #        total_n += len(points) 
                           
        data = np.zeros(total_n, [('a_position', np.float32, 3),
                        ('a_bg_color', np.float32, 4),
                        ('a_fg_color', np.float32, 4),
                        ('a_size', np.float32, 1)])

        #POPULATE DATA ARRAY
        start = 0
        current_regions = 0
        for i in range(len(all_plane_points)):
            points = all_plane_points[i]

            if self.render_params['top_dogs_only']:
                if self.__bfps[i].id in self.__top_dogs :
                    regions = self.selected_regions[current_regions]
                    m = sum([len(region) for region in regions])
                    n = len(points)
                    #assert(m == n) m innehåller inte alla points då de kan ha försvunnit i små regions

                    for j in range(len(regions)):
                        #plane = pf.fitPlane(points[regions[j]])
                        plane = self.selected_planes[current_regions][j]
                        points[regions[j]] = elevatePointsToPlane(points[regions[j]], plane)

                    datapoints = data[start:start+n]
                    self.setupRegionData(datapoints, regions, points)
                    current_regions += 1
                    start += n
            
            else:
                regions = self.selected_regions[current_regions]
                m = sum([len(region) for region in regions])
                n = len(points)
                #assert(m == n) m innehåller inte alla points då de kan ha försvunnit i små regions

                for j in range(len(regions)):
                    #plane = pf.fitPlane(points[regions[j]])
                    plane = self.selected_planes[current_regions][j]
                    points[regions[j]] = elevatePointsToPlane(points[regions[j]], plane)
                datapoints = data[start:start+n]
                self.setupRegionData(datapoints, regions, points)
                current_regions += 1
                start += n

        ##POPULATE DATA ARRAY
        #start = 0
        #current_regions = 0
        #for i in range(len(all_plane_points)):
        #    points = all_plane_points[i]
        #    n = len(points)

        #    if self.__bfps[i].id in self.__top_dogs :
                
        #        regions = self.selected_regions[current_regions]
        #        datapoints = data[start:start+n]
        #        for j in range(len(regions)):
        #            plane = pf.fitPlane(points[regions[j]])
        #            points[regions[j]] = elevatePointsToPlane(points[regions[j]], plane)

        #        #region_points = elevatePointsToPlane(points[:,0:2], self.all_planes[current_regions])
        #        self.setupRegionData(datapoints, regions, points)
        #        current_regions += 1
        #        start += n
            
        #    elif self.render_params['top_dogs_only'] == False:
        #        n = len(points)
        #        data[start:start+n]['a_bg_color'] = np.array([0.7,0.7,0.9,0.5], dtype=np.float32)
        #        data[start:start+n]['a_position'] = points
        #        start += n

            data[0:total_n]['a_fg_color'] = 0, 0, 0, 1
            data[0:total_n]['a_size'] = 10
        
        #BIND DATA TO GL PROGRAM
        self.program_points.bind(gloo.VertexBuffer(data))
        self.update()

    def setup_regions(self):

        self.setup_points_selected = self.setup_regions
        all_points = np.array(self.__points)
        all_points = copy.copy(all_points)

        self.selected_regions = self.slice_regions

        if self.render_params['top_dogs_only']:
            self.selected_regions = self.top_dogs_regions

        if self.selected_regions == None:
            self.__parent__.pipelineWidget.cluster_layout.setRegions()
            self.selected_regions = self.slice_regions

        n_regions = len(self.selected_regions)

        #PREPARE DATA ARRAY
        total_n = 0
        current_regions = 0
        for i in range(len(all_points)):
            points = all_points[i]
            
            if self.render_params['top_dogs_only']:

                if self.__bfps[i].id in self.__top_dogs :
                    n_in_region = sum([len(region) for region in self.selected_regions[current_regions]])
                    total_n += len(points)
                    current_regions += 1

            else:
                total_n += len(points) 
                           
        data = np.zeros(total_n, [('a_position', np.float32, 3),
                        ('a_bg_color', np.float32, 4),
                        ('a_fg_color', np.float32, 4),
                        ('a_size', np.float32, 1)])

        #POPULATE DATA ARRAY
        start = 0
        current_regions = 0
        for i in range(len(all_points)):
            points = all_points[i]

            if self.render_params['top_dogs_only']:
                if self.__bfps[i].id in self.__top_dogs :
                    regions = self.selected_regions[current_regions]
                    m = sum([len(region) for region in regions])
                    n = len(points)
                    #assert(m == n) m innehåller inte alla points då de kan ha försvunnit i små regions
                    datapoints = data[start:start+n]
                    self.setupRegionData(datapoints, regions, points)
                    current_regions += 1
                    start += n
            
            else:
                regions = self.selected_regions[current_regions]
                m = sum([len(region) for region in regions])
                n = len(points)
                #assert(m == n) m innehåller inte alla points då de kan ha försvunnit i små regions
                datapoints = data[start:start+n]
                self.setupRegionData(datapoints, regions, points)
                current_regions += 1
                start += n
            #else:
            #    n = len(points)
            #    data[start:start+n]['a_bg_color'] = np.array([0.7,0.7,0.9,0.5], dtype=np.float32)
            #    data[start:start+n]['a_position'] = points
            #    start += n

            data[0:total_n]['a_fg_color'] = 0, 0, 0, 1
            data[0:total_n]['a_size'] = 10
        
        #BIND DATA TO GL PROGRAM
        self.program_points.bind(gloo.VertexBuffer(data))
        self.update()
    
    def setupRegionData(self, datapoints, regions, points):
        n_regions = len(regions)
        colors = distinct_colors(n_regions)
       
        for region_idx in range(n_regions):
            n_points_in_region = len(regions[region_idx])
            r,g,b = colors[region_idx]
            for point_idx in regions[region_idx]:
                datapoints[point_idx]['a_bg_color'] = np.array([r,g,b,0.5], dtype=np.float32)
                datapoints[point_idx]['a_position'] = np.array(points[point_idx], dtype=np.float32)


    def reset_camera(self):
        #Create the camera         
        self.__camera = Cam3D.Camera([0 ,-100, 50], [0,0,0], [0,0,1], 45.0, self.size[0] / float(self.size[1]), 0.01, 1000.0, is_2d=False)

        self.program_solids['view'] = self.__camera.view

        self.program_points['u_view'] = self.__camera.view
        self.program_points['u_size'] = 0.3 +  0.8 /self.__camera.zoom_factor

        self.activate_zoom()

    def update_render_points_params(self, attr:str, value):
        self.__render_points_params[attr] = value
        self.setup_points()

    def on_mouse_press(self, event):

        if event.button == 1:
            
            self.__camera.is_move = True
            self.__camera.is_rotate = False
        
        if event.button == 2:
            
            self.__camera.is_move = False
            self.__camera.is_rotate = True
        
        self.__camera.prev_mouse_pos = event.pos

    def on_mouse_release(self, event):

        self.__camera.is_move = False
        self.__camera.is_rotate = False

    def on_mouse_move(self, event):

        if self.__camera.is_move:

            self.__camera.translate2d( -1*np.array(event.pos - self.__camera.prev_mouse_pos, dtype=np.float32 ))
            self.program_solids['view'] = self.__camera.view
            self.program_points['u_view'] = self.__camera.view
            self.update()

        elif self.__camera.is_rotate:

            self.__camera.rotx(-1*np.array((event.pos - self.__camera.prev_mouse_pos))[1:2])
            self.__camera.roty(-1*np.array((event.pos - self.__camera.prev_mouse_pos))[0:1])
            self.program_solids['view'] = self.__camera.view
            self.program_points['u_view'] = self.__camera.view
            self.update()

        self.__camera.prev_mouse_pos = event.pos
    
    def on_mouse_wheel(self, event):
    
        self.__camera.scale(event.delta[1])
        self.program_solids['view'] = self.__camera.view
        self.program_points['u_view'] = self.__camera.view
        self.program_points['u_size'] =  0.3 +  0.8 /self.__camera.zoom_factor #magicnumber zoom on the poor camera 
        self.update()
    

    def draw_model(self):
        
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthMask(gl.GL_TRUE)
        gl.glFrontFace(gl.GL_CCW)
        gl.glDisable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_ZERO, gl.GL_ZERO)
        
        if self.render_params['transparent']:
            
            gl.glEnable(gl.GL_BLEND)
            gl.glDepthMask(gl.GL_FALSE)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        self.program_solids.draw('triangles')


    def draw_points(self):

        gl.glDisable(gl.GL_BLEND)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthMask(gl.GL_TRUE)

        self.program_points.draw('points')
   
    
    def on_draw(self, event):

        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        
        if self.render_params['draw_polygons']:
            self.draw_model()
        
        if self.render_params['draw_points']:
            self.draw_points()


    def on_resize(self, event):
        
        self.activate_zoom()


    def activate_zoom(self):

        gloo.set_viewport(0, 0, *self.physical_size)
        projection = perspective(45.0, self.size[0] / float(self.size[1]), 1.0, 1000.0)
        self.program_solids['projection'] = projection
        self.program_points['u_projection'] = projection


    def on_timer(self, event):
        
        self.__theta += .5
        self.__phi += .5
        
        self.__camera.roty(.0)
        self.program_solids['view'] = self.__camera.view
        self.program_points['u_view'] = self.__camera.view
        self.update()


if __name__ == '__main__':

    c = Canvas3D(parent = None)
    app.run()