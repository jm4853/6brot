import moderngl
import numpy as np
from PIL import Image
import glfw
import threading
import time
import sys
import math
import ControlPanel

A_SCALE = 6

VERTEX_SHADER="vertex.glsl"
# FRAGMENT_SHADER="frag.glsl"
FRAGMENT_SHADER="fragd.glsl"


WINDOW_WIDTH = 1200
WINDOW_HEIGHT = WINDOW_WIDTH
# WINDOW_WIDTH = 1200
# WINDOW_HEIGHT = 1000


def splitd(n):
    n = np.float64(n)
    a = np.float32(n)
    return a, np.float32(n - np.float64(a))

def load_program(vertex_path=VERTEX_SHADER, fragment_path=FRAGMENT_SHADER):
    vert = None
    with open(vertex_path, 'r') as f:
        # vert = ''.join(f.readlines())
        vert = f.read()
    frag = None
    with open(fragment_path, 'r') as f:
        # frag = ''.join(f.readlines())
        frag = f.read()
    return ctx.program(vertex_shader=vert, fragment_shader=frag)

if __name__ == "__main__":
    P = [0,0,-0.5,0.5,2/A_SCALE,0]
    O = [-0.5,0,0.99]
    V = [0,0,0.9,0,0,0]
    U = [0,0,0,0.9,0,0]
    if 'julia' in sys.argv:
        V = [0.9,0,0,0,0,0]
        U = [0,0.9,0,0,0,0]
    elif 'a' in sys.argv:
        V = [0,0,0,0,0.9,0]
        U = [0,0,0,0,0,0.9]
    elif len(sys.argv) == 13:
        V = [float(v) for v in sys.argv[1:7]]
        U = [float(u) for u in sys.argv[7:]]

    dx_scale = lambda v : 1/(1-(v**8)) - 1
    t = threading.Thread(target=ControlPanel.controlWorker, args=(V, U, P, O, dx_scale), daemon=True)
    t.start()

    # Initialize GLFW
    glfw.init()
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Mandelbrot", None, None)
    glfw.make_context_current(window)
    
    ctx = moderngl.create_context()
    
    vertices = np.array([
        -1.0, -1.0,
        1.0, -1.0,
        -1.0, 1.0,
        1.0, 1.0,
    ], dtype='f4')
    
    prog = load_program()
    
    vbo = ctx.buffer(vertices.tobytes())
    vao = ctx.simple_vertex_array(prog, vbo, 'in_pos')
    
    # t = 0
    
    while not glfw.window_should_close(window):
        time.sleep(0.1)
        # t += 0.01
        v = np.array(V)
        u = np.array(U)
        p = np.array(P)
        v[-2:] *= A_SCALE
        u[-2:] *= A_SCALE
        p[-2:] *= A_SCALE
        o = np.array(O[:-1])
        dx = O[2]
        # dx = 1/(1-(O[2]**8)) - 1

        # u[0], u[1] = 0.5 * np.sin(t), 0.5 * np.cos(t)
        # u[2], u[3] = 0.5 * np.sin(t*1.67), 0.5 * np.cos(t*1.67)
    
        dy = (WINDOW_HEIGHT / WINDOW_WIDTH) * dx
        x_p = v / np.linalg.norm(v)
        u_n = u / np.linalg.norm(u)
        y_p = u_n - np.dot(np.dot(u_n, x_p), x_p)
    
        # X_P = V / np.linalg.norm(V)
        # U_N = U / np.linalg.norm(U)
        # Y_P = U_N - np.dot(np.dot(U_N, X_P), X_P)
    
        # prog['u_Xzr'].value, prog['u_Xzi'].value, prog['u_Xcr'].value, prog['u_Xci'].value, prog['u_Xar'].value, prog['u_Xai'].value = x_p
        # prog['u_Yzr'].value, prog['u_Yzi'].value, prog['u_Ycr'].value, prog['u_Yci'].value, prog['u_Yar'].value, prog['u_Yai'].value = y_p
        # prog['u_Pzr'].value, prog['u_Pzi'].value, prog['u_Pcr'].value, prog['u_Pci'].value, prog['u_Par'].value, prog['u_Pai'].value = p
        # prog['u_Ox'].value, prog['u_Oy'].value = o
        # prog['u_Dx'].value, prog['u_Dy'].value = dx, dy

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
        # prog['u_pi'].value = splitd(math.pi)


        # prog['u_Xp'].value = x_p[:-2]
        # prog['u_Yp'].value = y_p[:-2]
        # prog['u_P0'].value = p[:-2]
        # prog['u_o'].value = o
        # prog['u_d'].value = (dx, dy)
        # prog['u_Ax'].value = x_p[-2:]
        # prog['u_Ay'].value = y_p[-2:]
        # prog['u_Ap'].value = p[-2:]
    
        ctx.clear(0.0, 0.0, 0.0)
        vao.render(moderngl.TRIANGLE_STRIP)
        glfw.swap_buffers(window)
        glfw.poll_events()
        # print(f"V: {v}")
        # print(f"U: {u}")
        # print(f"P: {p}")
    
    glfw.terminate()
