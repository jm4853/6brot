import argparse
import threading
import time
import sys
import math
import vecpanel as VPanel
from display import Viewer
import math
from vecbuf import VectorBuffer



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

def mandel_zoom(iters):
    def __iter_mandel_zoom(i, vbuf):
        # start = 2.0
        # stop = 1.7741242160188373e-14
        start = 0.4252632389468262
        stop = 0.0001580796401652085
        a = stop * ((start / stop) ** (1 - (i/iters)))
        vbuf['O'][2] = a
    return __iter_mandel_zoom



def julia_rotate_worker(p):
    step = 0.001
    a = 0.0
    while True:
        time.sleep(0.01)
        p[2:4] = 0.7885 * math.cos(a), 0.7885 * math.sin(a)
        a += step

def julia_rotate(start, stop, iters):
    def __iter_julia_rotate(i, vbuf):
        a = start + (stop - start) * (i / iters)
        vbuf['P'][2:4] = 0.7885 * math.cos(a), 0.7885 * math.sin(a)
    return __iter_julia_rotate
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='6brot')
    parser.add_argument('-f64', action='store_true', help='64-bit floating point render')
    parser.add_argument('--julia', action='store_true', help='initialize with julia set')
    ns = parser.parse_args(sys.argv[1:])
    P = [0,0,0,0,2,0]
    P = [0, 0, 0, 0, 0.6470588235294121, -3.5294117647058822]
    O = [-0.5, 0.0, 1.6128161736849973, 600, 1, 0]
    # O = [0.5596849942261557, -0.16094445093923102, 0.4252632389468262, 600, 1.0, 0]
    O = [0.5551920198936007, -0.15929986867088075, 0.4252632389468262, 2000, 0.6499999999999997, 0]
    # O[:2] = [-0.2208100689243828, 0.758197816745033]
    # O[:2] = [-0.3476909928241201, 0.6069024572220293]
    # O[:2] = [-0.6502355409757977, 0.4759636838082013]
    # O = [-0.6502355409757977, 0.4759636838082013, 1.9504383129729465e-05, 600]
    # O = [-0.6511895403942833, 0.47986299107659164, 2.0, 100000, 0.33, 0]
    V = [0.9,0,0.9,0,0,0]
    U = [0,0.9,0,0.9,0,0]
    if ns.julia:
        P = [0,0,-0.53,0.56,2,0]
        O[:-1] = [0,0,1.0]
        # O = [0.08728900839574767, 0.2313537673122509, 0.47759837243791636, 50000, 0.24999999999999967]
        # O = [0.016557340826957014, 0.023797803624821534, 1.6128161736849973, 5000, 0.3, 0]
        O = [0.08728900839574767, 0.2313537673122509, 0.47759837243791636, 1000, 1]
        V = [0.9,0,0,0,0,0]
        U = [0,0.9,0,0,0,0]

    vb = VectorBuffer({'V': V, 'U': U, 'P': P, 'O': O})

    # julia_rotate(3.292, 3.296, 1)(0, vb)   # TODO

    t = threading.Thread(target=VPanel.thread_worker, args=(vb,), daemon=True)
    t.start()
    # TODO: tkinter not thread safe
    time.sleep(0.5)

    # if ns.julia:
    #     a_t = threading.Thread(target=julia_rotate_worker, args=(P,), daemon=True)
    # else:
    #     a_t = threading.Thread(target=zoom_worker, args=(O,), daemon=True)
    # a_t.start()


    v = Viewer(vb)

    if not False:
    # if False:
        duration = 10
        n_frames = duration*10
        v.record('mandel32', mandel_zoom(n_frames), n_frames, duration)
        # start = 3.22 + (3.3 - 3.22) * (-461 / 100)
        # stop = 3.22 + (3.3 - 3.22) * (-95 / 100)
        # v.record('mandel64', julia_rotate(start, stop, n_frames), n_frames, duration)
        # v.record('mandel64', julia_rotate(3.292, 3.29255, n_frames), n_frames, duration)
    else:
        if ns.f64:
            # v.run('mandel64', julia_rotate(3.22, 3.3, 100))
            # v.run('mandel64', mandel_zoom(100))
            v.run('mandel64')
        else:
            v.run('mandel32')

