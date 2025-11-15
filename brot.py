import moderngl
import numpy as np
from PIL import Image
import glfw
import threading
import time
import sys
import ControlPanel
import Shaders


V = [0,0,0.9,0,0,0]
U = [0,0,0,0.9,0,0]

if __name__ == "__main__":
    if 'julia' in sys.argv:
        V = [0.9,0,0,0,0,0]
        U = [0,0.9,0,0,0,0]
    if 'a' in sys.argv:
        V = [0,0,0,0,0.9,0]
        U = [0,0,0,0,0,0.9]
        

A_SCALE = 6

P = [0,0,-0.5,0.5,2/A_SCALE,0]
O = [-0.5,0,3.5]



t = threading.Thread(target=ControlPanel.worker, args=(V, U, P, O), daemon=True)
t.start()



WIDTH = 1200
HEIGHT = WIDTH
# WIDTH = 1200
# HEIGHT = 1000

# Initialize GLFW
glfw.init()
window = glfw.create_window(WIDTH, HEIGHT, "Mandelbrot", None, None)
glfw.make_context_current(window)

ctx = moderngl.create_context()

vertices = np.array([
    -1.0, -1.0,
    1.0, -1.0,
    -1.0, 1.0,
    1.0, 1.0,
], dtype='f4')

prog = ctx.program(
    vertex_shader='''
    #version 330
    in vec2 in_pos;
    out vec2 v_pos;
    void main() {
        v_pos = in_pos;
        gl_Position = vec4(in_pos, 0.0, 1.0);
    }
    ''',
    fragment_shader=Shaders.ITER_SHADER
)

vbo = ctx.buffer(vertices.tobytes())
vao = ctx.simple_vertex_array(prog, vbo, 'in_pos')


# t = 0

while not glfw.window_should_close(window):
    # t += 0.01
    v = np.array(V)
    u = np.array(U)
    p = np.array(P)
    v[-2:] *= A_SCALE
    u[-2:] *= A_SCALE
    p[-2:] *= A_SCALE
    o = np.array(O[:-1])
    dx = 1/(1-O[2]) - 1

    # u[0], u[1] = 0.5 * np.sin(t), 0.5 * np.cos(t)
    # u[2], u[3] = 0.5 * np.sin(t*1.67), 0.5 * np.cos(t*1.67)
    # time.sleep(0.01)

    dy = (HEIGHT / WIDTH) * dx
    x_p = v / np.linalg.norm(v)
    u_n = u / np.linalg.norm(u)
    y_p = u_n - np.dot(np.dot(u_n, x_p), x_p)

    # X_P = V / np.linalg.norm(V)
    # U_N = U / np.linalg.norm(U)
    # Y_P = U_N - np.dot(np.dot(U_N, X_P), X_P)

    prog['u_Xp'].value = x_p[:-2]
    prog['u_Yp'].value = y_p[:-2]
    prog['u_P0'].value = p[:-2]
    prog['u_o'].value = o
    # prog['u_d'].value = np.array([1/(1-dx), 1/(1-dy)]) - 1
    prog['u_d'].value = (dx, dy)
    prog['u_Ax'].value = x_p[-2:]
    prog['u_Ay'].value = y_p[-2:]
    prog['u_Ap'].value = p[-2:]

    ctx.clear(0.0, 0.0, 0.0)
    vao.render(moderngl.TRIANGLE_STRIP)
    glfw.swap_buffers(window)
    glfw.poll_events()
    # print(f"V: {v}")
    # print(f"U: {u}")
    # print(f"P: {p}")

glfw.terminate()
