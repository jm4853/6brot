# import moderngl
# import numpy as np
# from PIL import Image
# import glfw
import threading
import time
import sys
import math
import ControlPanel
from display import Viewer
import math

A_SCALE = 6


def animate_worker(p):
    period = 120
    step = 0.001
    a = 0.3
    while True:
        time.sleep(period / (math.pi * 2 / step))
        p[2:4] = 0.7885 * math.cos(a), 0.7885 * math.sin(a)
        a += step



        
    


if __name__ == "__main__":
    P = [0,0,0,0,2/A_SCALE,0]
    O = [-0.5,0,1.0]
    # O = [0,0,1.0]
    V = [0,0,0.9,0,0,0]
    U = [0,0,0,0.9,0,0]
    if 'julia' in sys.argv:
        P = [0,0,-0.53,0.56,2/A_SCALE,0]
        O = [0,0,1.0]
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

    a_t = threading.Thread(target=animate_worker, args=(P,), daemon=True)
    a_t.start()

    v = Viewer(V, U, P, O, A_SCALE)
    v.mandel32()

