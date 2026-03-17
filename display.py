import moderngl
import numpy as np
from PIL import Image
import glfw
import math
import time
from enum import Enum



WINDOW_WIDTH = 1200
WINDOW_HEIGHT = WINDOW_WIDTH
# WINDOW_WIDTH = 1200
# WINDOW_HEIGHT = 1000


        



def splitd(n):
    n = np.float64(n)
    a = np.float32(n)
    return a, np.float32(n - np.float64(a))


class Viewer:
    VERTEX_SHADER="vertex.glsl"
    # F32_FRAGMENT_SHADER="frag.glsl"
    MANDEL32_FRAG="mandel32.frag"
    # F64_FRAG_SHADER="fragd.glsl"
    MANDEL64_FRAG="mandel64.frag"
    BLUR_FRAG_SHADER="blur.frag"

    def __init__(self, v, u, p, o, a_scale, dx_scale):
        self.V = v
        self.U = u
        self.P = p
        self.O = o
        self.A_SCALE = a_scale
        self.ctx = None
        self.dx_scale = dx_scale
        self.last_y = None
        self.last_x = None
        self.mouse_pressed = None

    def mandel32(self):
        # Initialize GLFW
        glfw.init()
        window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "6brot 32-bit", None, None)
        # monitor = glfw.get_monitors()[1]
        # mode = glfw.get_video_mode(monitor)
        # WINDOW_WIDTH = mode.size.width
        # WINDOW_HEIGHT = mode.size.height
        # glfw.window_hint(glfw.DECORATED, glfw.FALSE)
        # window = glfw.create_window(mode.size.width, mode.size.height, "6brot 64-bit Fullscreen", None, None)
        if not window:
            glfw.terminate()
            raise Exception("No window")

        glfw.set_key_callback(window, self.get_key_cb())
        glfw.set_scroll_callback(window, self.get_scroll_cb())
        glfw.set_mouse_button_callback(window, self.get_mouse_cb())
        glfw.set_cursor_pos_callback(window, self.get_cursor_cb())
        # xpos, ypos = glfw.get_monitor_pos(monitor)
        # glfw.set_window_pos(window, xpos, ypos)
        glfw.make_context_current(window)
        
        self.ctx = moderngl.create_context()
        
        vertices = np.array([
            -1.0, -1.0*(WINDOW_WIDTH/WINDOW_HEIGHT),
            -1.0, (WINDOW_WIDTH/WINDOW_HEIGHT),
            1.0, -1.0*(WINDOW_WIDTH/WINDOW_HEIGHT),
            1.0, (WINDOW_WIDTH/WINDOW_HEIGHT),
        ], dtype='f4')
        
        prog = self.load_program(self.MANDEL32_FRAG)
        
        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.simple_vertex_array(prog, vbo, 'in_pos')

        while not glfw.window_should_close(window):
            time.sleep(0.01)

            v = np.array(self.V)
            u = np.array(self.U)
            p = np.array(self.P)
            v[-2:] *= self.A_SCALE
            u[-2:] *= self.A_SCALE
            p[-2:] *= self.A_SCALE
            o = np.array([self.O[0], self.O[1]])
            dx = self.O[2]
        
            dy = (WINDOW_HEIGHT / WINDOW_WIDTH) * dx
            x_p = v / np.linalg.norm(v)
            u_n = u / np.linalg.norm(u)
            y_p = u_n - np.dot(np.dot(u_n, x_p), x_p)
            
            px_sizex = dx * 2 / WINDOW_WIDTH
            px_sizey = dy * 2 / WINDOW_HEIGHT

            prog['u_Xp'].value = x_p[:-2]
            prog['u_Yp'].value = y_p[:-2]
            prog['u_P0'].value = p[:-2]
            prog['u_o'].value = o
            prog['u_d'].value = (dx, dy)
            prog['u_Ax'].value = x_p[-2:]
            prog['u_Ay'].value = y_p[-2:]
            prog['u_Ap'].value = p[-2:]

            prog['u_AvgStep'].value = ((px_sizex * 0.25), (px_sizey * 0.25))
            prog['u_DoAvg'] = False

            self.ctx.clear(0.0, 0.0, 0.0)
            vao.render(moderngl.TRIANGLE_STRIP)
            glfw.swap_buffers(window)
            glfw.poll_events()
        
        glfw.terminate()

    def mandel64(self):
        # Initialize GLFW
        glfw.init()
        window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "6brot 64-bit", None, None)
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
        
        prog = self.load_program(self.MANDEL64_FRAG)
        
        vbo = self.ctx.buffer(vertices.tobytes())
        vao = self.ctx.simple_vertex_array(prog, vbo, 'in_pos')

        while not glfw.window_should_close(window):
            time.sleep(0.1)

            v = np.array(self.V)
            u = np.array(self.U)
            p = np.array(self.P)
            v[-2:] *= self.A_SCALE
            u[-2:] *= self.A_SCALE
            p[-2:] *= self.A_SCALE
            o = np.array([self.O[0], self.O[1]])
            dx = self.O[2]
        
            dy = (WINDOW_HEIGHT / WINDOW_WIDTH) * dx
            x_p = v / np.linalg.norm(v)
            u_n = u / np.linalg.norm(u)
            y_p = u_n - np.dot(np.dot(u_n, x_p), x_p)
            
            
            px_sizex = dx * 2 / WINDOW_WIDTH
            px_sizey = dy * 2 / WINDOW_HEIGHT

            prog['u_Xz'].value = (*splitd(x_p[0]), *splitd(x_p[1]))
            prog['u_Yz'].value = (*splitd(y_p[0]), *splitd(y_p[1]))
            prog['u_Pz'].value = (*splitd(p[0]), *splitd(p[1]))
            prog['u_Xc'].value = (*splitd(x_p[2]), *splitd(x_p[3]))
            prog['u_Yc'].value = (*splitd(y_p[2]), *splitd(y_p[3]))
            prog['u_Pc'].value = (*splitd(p[2]), *splitd(p[3]))
            # prog['u_Xa'].value = (*splitd(x_p[4]), *splitd(x_p[5]))
            # prog['u_Ya'].value = (*splitd(y_p[4]), *splitd(y_p[5]))
            # prog['u_Pa'].value = (*splitd(p[4]), *splitd(p[5]))
            prog['u_O'].value = (*splitd(o[0]), *splitd(o[1]))
            prog['u_D'].value = (*splitd(dx), *splitd(dy))
            prog['u_one'].value = 1.0
            prog['u_AvgStep'].value = (*splitd(px_sizex * 0.25), *splitd(px_sizey * 0.25))
            prog['u_DoAvg'] = False

        
            self.ctx.clear(0.0, 0.0, 0.0)
            vao.render(moderngl.TRIANGLE_STRIP)
            glfw.swap_buffers(window)
            glfw.poll_events()
        
        glfw.terminate()

    def load_program(self, fragment_path, vertex_path=VERTEX_SHADER):
        vert = None
        with open(vertex_path, 'r') as f:
            vert = f.read()
        frag = None
        with open(fragment_path, 'r') as f:
            frag = f.read()
        return self.ctx.program(vertex_shader=vert, fragment_shader=frag)

    def get_key_cb(self):
        def key_event_handler(window, key, scancode, action, mods):
            if key == glfw.KEY_ESCAPE and action != glfw.RELEASE:
                print("<Esc> Detected, closing")
                glfw.set_window_should_close(window, True)
            elif key == glfw.KEY_UP and action != glfw.RELEASE:
                self.O[1] -= (0.05 * self.O[2])
            elif key == glfw.KEY_DOWN and action != glfw.RELEASE:
                self.O[1] += (0.05 * self.O[2])
            elif key == glfw.KEY_LEFT and action != glfw.RELEASE:
                self.O[0] -= (0.05 * self.O[2])
            elif key == glfw.KEY_RIGHT and action != glfw.RELEASE:
                self.O[0] += (0.05 * self.O[2])
            print(f'Got key: {key}:{action}')
        return key_event_handler
    
    def get_scroll_cb(self):
        def scroll_event_handler(window, xoffset, yoffset):
            self.O[2] -= yoffset * 0.1 * self.O[2]
            if self.O[2] < 0.0:
                self.O[2] = 0.0
        return scroll_event_handler

    def get_mouse_cb(self):
        def mouse_button_event_handler(window, button, action, mods):
            if button == glfw.MOUSE_BUTTON_LEFT:
                if action == glfw.PRESS:
                    self.mouse_pressed = True
                    self.last_x, self.last_y = glfw.get_cursor_pos(window)
                elif action == glfw.RELEASE:
                    self.mouse_pressed = False
        return mouse_button_event_handler

    def get_cursor_cb(self):
        def cursor_position_event_handler(window, xpos, ypos):
            if self.mouse_pressed:
                width, height = glfw.get_window_size(window)
                drag_delta_x = xpos - self.last_x
                drag_delta_y = ypos - self.last_y
                self.last_x = xpos
                self.last_y = ypos
                dx = drag_delta_x / width
                dy = drag_delta_y / height
                self.O[0] -= dx * self.O[2]
                self.O[1] += dy * self.O[2]
        return cursor_position_event_handler
        

