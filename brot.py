import argparse
import threading
import time
import sys
import math
from ControlPanel import VectorPanel
from display import Viewer
import math

A_SCALE = 6


def zoom_worker(o):
    step = 0.0001
    a = 0.3
    d = 1.0
    while True:
        time.sleep(0.001)
        o[2] -= (0.001 * o[2]) * d
        if o[2] < 1.7752192206871532e-13:
            o[2] = 1.7752192206871532e-13
            d *= -1.0
        if o[2] > 5:
            o[2] = 5
            d *= -1.0
        a += step

def julia_rotate_worker(p):
    step = 0.001
    a = 0.0
    while True:
        time.sleep(0.01)
        p[2:4] = 0.7885 * math.cos(a), 0.7885 * math.sin(a)
        a += step


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='6brot')
    parser.add_argument('-f64', action='store_true', help='64-bit floating point render')
    parser.add_argument('--julia', action='store_true', help='initialize with julia set')
    ns = parser.parse_args(sys.argv[1:])
    P = [0,0,0,0,2/A_SCALE,0]
    O = [-0.5,0,1.0]
    # O[:-1] = [-0.2208100689243828, 0.758197816745033]
    # O[:-1] = [-0.3476909928241201, 0.6069024572220293]
    # O = [0,0,1.0]
    V = [0,0,0.9,0,0,0]
    U = [0,0,0,0.9,0,0]
    if ns.julia:
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

    vp = VectorPanel([V, U, P])
    vp.start()
    # t = threading.Thread(target=ControlPanel.controlWorker, args=(V, U, P), daemon=True)
    # t.start()

    # if ns.julia:
    #     a_t = threading.Thread(target=julia_rotate_worker, args=(P,), daemon=True)
    # else:
    #     a_t = threading.Thread(target=zoom_worker, args=(O,), daemon=True)
    # a_t.start()

    v = Viewer(V, U, P, O, A_SCALE)
    if ns.f64:
        v.mandel64()
    else:
        v.mandel32()

