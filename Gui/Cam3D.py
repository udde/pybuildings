import numpy as np
import Utils.vector_utils as vut
from vispy import gloo, app, use

class Camera():

    def __init__(self, pos, target, up ,fov, aspect, near, far, is_2d = False):
        
        self.__is_2d = is_2d
        self.__up = np.array(up, dtype=np.float32)
        self.__projection_mat = vut.perspective(fov, aspect, near, far)
        
        self.T = vut.translate(pos)
        self.zero = np.array([0,0,0,1],dtype=np.float32)
        self.rx = 0
        self.Rx = vut.rotx(self.rx)
        self.Ry = vut.roty(0)
        self.sf = 0.77
        self.S = vut.scale(self.sf*np.array([1,1,1]))
        
        self.__pos = vut.transform( self.S*self.Ry*self.Rx*self.T, self.zero)[:3]

        self.__target = np.array(target)
        self.__look_dir = vut.normalize(np.array(self.__target, dtype=np.float32) - np.array(self.__pos, dtype=np.float32))          
        self.__right = vut.normalize(np.cross(self.__look_dir, self.__up))
        self.__cam_up = vut.normalize(np.cross(self.__right, self.__look_dir))
        self.__view_mat = vut.lookat(self.__pos, self.__target, self.__up)

        x = np.dot(self.__pos, self.__look_dir * -1)
        self.zoom_factor = x * 0.04

        self.__prev_mouse_pos = []
        self.__is_move = False
        self.__is_rotate = False
        
        self.update()


    def update(self):
        
        self.__look_dir = vut.normalize(np.array(self.__target, dtype=np.float32) - np.array(self.__pos, dtype=np.float32))          
        self.__right = vut.normalize(np.cross(self.__look_dir, self.__up))
        self.__cam_up = vut.normalize(np.cross(self.__right, self.__look_dir))
        self.__view_mat = vut.lookat(self.__pos, self.__target, self.__cam_up)


    def scale(self, f):
        #print(self.zoom_factor)
        x = np.dot(self.__pos, self.__look_dir * -1)
        
        self.zoom_factor = x * 0.04
        self.__pos += f*self.__look_dir*self.zoom_factor
        self.update()


    def rotx(self, a):
        
        if not self.__is_2d:

            self.__pos = vut.transform(vut.rotate(a, self.__right), np.append(self.__pos, 1))[:3]
            self.update()


    def roty(self, a):

        if not self.__is_2d:

            self.__pos = vut.transform(vut.rotate(a,self.__cam_up), np.append(self.__pos, 1))[:3]
            self.update()
    

    def translate_to(self, xy):
        
        self.__pos[0] = xy[0]
        self.__pos[1] = xy[1]
        self.__pos[2] = 300
        self.__target = np.array([xy[0], xy[1], 0], dtype=np.float32)
        self.update()


    def translate2d(self, xy):
        translate_factor = self.zoom_factor/14
        #print(self.zoom_factor)
        self.__pos += self.__right * xy[0] * translate_factor
        self.__pos -= self.__cam_up * xy[1] * translate_factor
        self.__target = np.array(self.__target, dtype=np.float32)
        self.__target += self.__right * xy[0] * translate_factor
        self.__target -= self.__cam_up * xy[1] * translate_factor
        self.update()
    

    @property
    def proj(self):
        return np.transpose(self.__projection_mat) #transpose for gloo        
    
    @property
    def view(self):
        return np.transpose(self.__view_mat) #transpose for gloo
    
    
    @property
    def view_proj(self):
        return np.transpose(self.__projection_mat * self.__view_mat) #transpose for gloo
    

    @property
    def prev_mouse_pos(self):
        return self.__prev_mouse_pos
    
    @prev_mouse_pos.setter
    def prev_mouse_pos(self, prev_mouse_pos):
        self.__prev_mouse_pos = prev_mouse_pos


    @property
    def is_move(self):
        return self.__is_move
    
    @is_move.setter
    def is_move(self, is_move):
        self.__is_move = is_move
    

    @property
    def is_rotate(self):
        return self.__is_rotate
    
    @is_rotate.setter
    def is_rotate(self, is_rotate):
        self.__is_rotate = is_rotate

    
    @property
    def zoom_factor(self):
        return self.__zoom_factor
    
    @zoom_factor.setter
    def zoom_factor(self, zoom_factor):
        self.__zoom_factor = zoom_factor


    @property
    def pos(self):
        return self.__pos
    
    @pos.setter
    def pos(self, pos):
        self.__pos = pos
        self.update()


    @property
    def target(self):
        return self.__target
    
    @target.setter
    def target(self, target):
        self.__pos = target
        self.update()

    
class Canvas(app.Canvas):

    def __init__(self, *args, **kwargs):
        
        app.Canvas.__init__(self, *args, **kwargs)
        self.title = 'App demo'
        cam = Camera([0,2,5], [0,0,0], 45.0, 800.0/ 600.0, 0.01, 250.0)

        
    def on_close(self, event):
        print('closing!')

    def on_resize(self, event):
        print('Resize %r' % (event.size, ))

    def on_key_press(self, event):
        modifiers = [key.name for key in event.modifiers]
        print('Key pressed - text: %r, key: %s, modifiers: %r' % (
            event.text, event.key.name, modifiers))

    def on_key_release(self, event):
        modifiers = [key.name for key in event.modifiers]
        print('Key released - text: %r, key: %s, modifiers: %r' % (
            event.text, event.key.name, modifiers))

    def on_mouse_press(self, event):
        self.print_mouse_event(event, 'Mouse press')

    def on_mouse_release(self, event):
        self.print_mouse_event(event, 'Mouse release')

    def on_mouse_move(self, event):
        self.print_mouse_event(event, 'Mouse move')

    def on_mouse_wheel(self, event):
        self.print_mouse_event(event, 'Mouse wheel')

    def print_mouse_event(self, event, what):
        modifiers = ', '.join([key.name for key in event.modifiers])
        print('%s - pos: %r, button: %s, modifiers: %s, delta: %r' %
              (what, event.pos, event.button, modifiers, event.delta))

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)


if __name__ == '__main__':
    
    canvas = Canvas(keys='interactive')
    canvas.show()
    app.run()