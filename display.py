import moderngl
import numpy as np
from PIL import Image
import glfw
import math
import time
from enum import Enum
from abc import ABC, abstractmethod



# WINDOW_WIDTH = 800
# WINDOW_HEIGHT = WINDOW_WIDTH
WINDOW_WIDTH = 150
WINDOW_HEIGHT = 150



class UniformWrapper(ABC):
    def __init__(self, prog):
        self.prog = prog
    @abstractmethod
    def set_O(self, O):
        pass
    @abstractmethod
    def set_P(self, P):
        pass
    @abstractmethod
    def set_VU(self, V, U):
        pass
class Uniform32(UniformWrapper):
    def __init__(self, prog):
        super().__init__(prog)
    def set_O(self, O):
        o = np.array(O[:2])
        dx = O[2]
        n = O[3]
        dy = (WINDOW_HEIGHT / WINDOW_WIDTH) * dx
        px_sizex = dx * 2 / WINDOW_WIDTH
        px_sizey = dy * 2 / WINDOW_HEIGHT
        self.prog['u_qpow'].value = O[4]
        self.prog['u_n'].value = n
        self.prog['u_o'].value = o
        self.prog['u_d'].value = (dx, dy)
        self.prog['u_AvgStep'].value = ((px_sizex * 0.25), (px_sizey * 0.25))
        self.prog['u_DoAvg'] = True
    def set_P(self, P):
        p = np.array(P)
        self.prog['u_P0'].value = p[:-2]
        self.prog['u_Ap'].value = p[-2:]
    def set_VU(self, V, U):
        v = np.array(V)
        u = np.array(U)
        x_p = v / np.linalg.norm(v)
        u_n = u / np.linalg.norm(u)
        y_p = u_n - np.dot(np.dot(u_n, x_p), x_p)
        self.prog['u_Xp'].value = x_p[:-2]
        self.prog['u_Yp'].value = y_p[:-2]
        self.prog['u_Ax'].value = x_p[-2:]
        self.prog['u_Ay'].value = y_p[-2:]
def splitd(n):
    n = np.float64(n)
    a = np.float32(n)
    return a, np.float32(n - np.float64(a))
class Uniform64(UniformWrapper):
    def __init__(self, prog):
        super().__init__(prog)
    def set_O(self, O):
        o = np.array(O[:2])
        dx = O[2]
        n = O[3]
        dy = (WINDOW_HEIGHT / WINDOW_WIDTH) * dx
        px_sizex = dx * 2 / WINDOW_WIDTH
        px_sizey = dy * 2 / WINDOW_HEIGHT
        self.prog['u_n'].value = n
        self.prog['u_O'].value = (*splitd(o[0]), *splitd(o[1]))
        self.prog['u_D'].value = (*splitd(dx), *splitd(dy))
        self.prog['u_qpow'].value = O[4]
        self.prog['u_one'].value = 1.0
        self.prog['u_AvgStep'].value = (*splitd(px_sizex * 0.25), *splitd(px_sizey * 0.25))
        self.prog['u_DoAvg'] = True
    def set_P(self, P):
        p = np.array(P)
        self.prog['u_Pz'].value = (*splitd(p[0]), *splitd(p[1]))
        self.prog['u_Pc'].value = (*splitd(p[2]), *splitd(p[3]))
    def set_VU(self, V, U):
        v = np.array(V)
        u = np.array(U)
        x_p = v / np.linalg.norm(v)
        u_n = u / np.linalg.norm(u)
        y_p = u_n - np.dot(np.dot(u_n, x_p), x_p)
        self.prog['u_Xz'].value = (*splitd(x_p[0]), *splitd(x_p[1]))
        self.prog['u_Yz'].value = (*splitd(y_p[0]), *splitd(y_p[1]))
        self.prog['u_Xc'].value = (*splitd(x_p[2]), *splitd(x_p[3]))
        self.prog['u_Yc'].value = (*splitd(y_p[2]), *splitd(y_p[3]))

class Viewer:
    VERTEX_SHADER="shaders/vertex.glsl"
    MANDEL32_FRAG="shaders/mandel32.frag"
    MANDEL64_FRAG="shaders/mandel64.frag"
    BLUR_FRAG_SHADER="shaders/blur.frag"

    def __init__(self, vbuf):
        self.vbuf = vbuf
        self.ctx = None
        self.last_y = None
        self.last_x = None
        self.mouse_pressed = dict()
        self.uniforms = None
    def process_updates(self, updates):
        if 'V' in updates.keys() or 'U' in updates.keys():
            v = updates.get('V', self.vbuf['V'].data)
            u = updates.get('U', self.vbuf['U'].data)
            self.uniforms.set_VU(v, u)
        if 'O' in updates.keys():
            self.uniforms.set_O(updates['O'])
        if 'P' in updates.keys():
            self.uniforms.set_P(updates['P'])

    def run(self, prog_name, func=None):
        # Initialize GLFW
        glfw.init()
        window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, prog_name, None, None)
        glfw.set_key_callback(window, self.get_key_cb())
        glfw.set_scroll_callback(window, self.get_scroll_cb())
        glfw.set_mouse_button_callback(window, self.get_mouse_cb())
        glfw.set_cursor_pos_callback(window, self.get_cursor_cb())
        glfw.make_context_current(window)
        
        self.ctx = moderngl.create_context()

        vertices = np.array([
            -1.0, -1.0,
            1.0, -1.0,
            -1.0, 1.0,
            1.0, 1.0,
        ], dtype='f4')
        
        prog = self.load_program(prog_name)
        
        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.simple_vertex_array(prog, vbo, 'in_pos')

        glfw.wait_events_timeout(0.5)   # Updates from vecpanel do not raise glfw event
        while not glfw.window_should_close(window):
            if not func is None:
                func(self.vbuf['O'][5], self.vbuf)
            if self.vbuf.dirty:
                updates = self.vbuf.get_updates()
                self.process_updates(updates)
                self.ctx.clear(0.0, 0.0, 0.0)
                vao.render(moderngl.TRIANGLE_STRIP)
                glfw.swap_buffers(window)
            glfw.wait_events()
        
        glfw.terminate()

    def record(self, prog_name, iter_func, n_iter, duration):
        glfw.init()
        window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, prog_name, None, None)
        glfw.set_key_callback(window, self.get_key_cb())
        glfw.set_scroll_callback(window, self.get_scroll_cb())
        glfw.set_mouse_button_callback(window, self.get_mouse_cb())
        glfw.set_cursor_pos_callback(window, self.get_cursor_cb())
        glfw.make_context_current(window)
        
        self.ctx = moderngl.create_context()

        vertices = np.array([
            -1.0, -1.0,
            1.0, -1.0,
            -1.0, 1.0,
            1.0, 1.0,
        ], dtype='f4')
        
        prog = self.load_program(prog_name)
        
        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.simple_vertex_array(prog, vbo, 'in_pos')

        frames = []

        for i in range(n_iter):
            iter_func(i, self.vbuf)
            vecs = self.vbuf.read()
            self.process_updates(vecs)
            self.ctx.clear(0.0, 0.0, 0.0)
            vao.render(moderngl.TRIANGLE_STRIP)
            raw_data = self.ctx.screen.read(components=3)
            img = Image.frombytes('RGB', (WINDOW_WIDTH, WINDOW_HEIGHT), raw_data)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            frames.append(img)
            glfw.swap_buffers(window)
        glfw.terminate()
        print(f'Saving...')
        frames[0].save(
            f'{prog_name}.gif',
            save_all=True, 
            append_images=frames[1:], 
            duration=duration*1000/n_iter,
            loop=0
        )
        print(f'Done!')
        

    def print_vectors(self):
        o = self.vbuf['O'].data
        dx = o[2]
        n = o[3]
        o = o[:2]
        print('================================')
        # print(f'n = {n}')
        # print(f'dx = {dx}')
        # print(f'O = {o}')
        print(f'O = {self.vbuf["O"].data}')
        print(f'V = {self.vbuf["V"].data}')
        print(f'U = {self.vbuf["U"].data}')
        print(f'P = {self.vbuf["P"].data}')
        print('================================')

    def load_shaders(self, fragment_path, vertex_path=VERTEX_SHADER):
        vert = None
        with open(vertex_path, 'r') as f:
            vert = f.read()
        frag = None
        with open(fragment_path, 'r') as f:
            frag = f.read()
        return self.ctx.program(vertex_shader=vert, fragment_shader=frag)
    def load_program(self, prog_name):
        prog = None
        if prog_name == 'mandel32':
            prog = self.load_shaders(self.MANDEL32_FRAG)
            self.uniforms = Uniform32(prog)
        elif prog_name == 'mandel64':
            prog = self.load_shaders(self.MANDEL64_FRAG)
            self.uniforms = Uniform64(prog)
        return prog

    def get_key_cb(self):
        def key_event_handler(window, key, scancode, action, mods):
            if key == glfw.KEY_ESCAPE and action != glfw.RELEASE:
                print("<Esc> Detected, closing")
                glfw.set_window_should_close(window, True)
            elif key == glfw.KEY_UP and action != glfw.RELEASE:
                self.vbuf['O'][3] = int(self.vbuf['O'][3] * 1.25)
                print(f'N = {self.vbuf["O"][3]}')
            elif key == glfw.KEY_DOWN and action != glfw.RELEASE:
                self.vbuf['O'][3] = int(self.vbuf['O'][3] / 1.25)
                print(f'N = {self.vbuf["O"][3]}')
            elif key == glfw.KEY_LEFT and action != glfw.RELEASE:
                if self.vbuf['O'][4] > 0.05:
                    self.vbuf['O'][4] -= 0.05
                print(f'q_pow = {self.vbuf["O"][4]}')
            elif key == glfw.KEY_RIGHT and action != glfw.RELEASE:
                self.vbuf['O'][4] += 0.05
                if self.vbuf['O'][4] > 1:
                    self.vbuf['O'][4] = 1.0
                print(f'q_pow = {self.vbuf["O"][4]}')
            elif key == glfw.KEY_M and action != glfw.RELEASE:
                self.vbuf['O'][5] += 1
            elif key == glfw.KEY_N and action != glfw.RELEASE:
                self.vbuf['O'][5] -= 1
        return key_event_handler
    
    def get_scroll_cb(self):
        def scroll_event_handler(window, xoffset, yoffset):
            self.vbuf['O'][2] = max(self.vbuf['O'][2] * (1 - yoffset * 0.1), 0.0)
        return scroll_event_handler

    def get_mouse_cb(self):
        def mouse_button_event_handler(window, button, action, mods):
            if button == glfw.MOUSE_BUTTON_LEFT:
                if action == glfw.PRESS:
                    self.mouse_pressed['l'] = True
                    self.last_x, self.last_y = glfw.get_cursor_pos(window)
                elif action == glfw.RELEASE:
                    self.mouse_pressed['l'] = False
            elif button == glfw.MOUSE_BUTTON_MIDDLE:
                if action == glfw.PRESS:
                    if not self.mouse_pressed.get('m', False):
                        self.print_vectors()
                    self.mouse_pressed['m'] = True
                elif action == glfw.RELEASE:
                    self.mouse_pressed['m'] = False
        return mouse_button_event_handler

    def get_cursor_cb(self):
        def cursor_position_event_handler(window, xpos, ypos):
            if self.mouse_pressed.get('l', False):
                width, height = glfw.get_window_size(window)
                drag_delta_x = xpos - self.last_x
                drag_delta_y = ypos - self.last_y
                self.last_x = xpos
                self.last_y = ypos
                dx = drag_delta_x / width
                dy = drag_delta_y / height
                self.vbuf['O'][0] -= dx * self.vbuf['O'][2]
                self.vbuf['O'][1] += dy * self.vbuf['O'][2]
        return cursor_position_event_handler
        

