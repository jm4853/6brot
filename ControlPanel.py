import tkinter as tk
import time

# LABEL_FONT = "Arial"
LABEL_FONT = "Computer Modern"
LABEL_FONT = "Times New Roman"

def canvas_oval(canvas, x, y):
    r = 3
    return canvas.create_oval(
        x - r, y - r,
        x + r, y + r,
        fill="red",
        outline="black",
        tags="point"
    )

def __configure(event, vec, i):
    canvas = event.widget
    canvas.delete("all")
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    canvas.create_line(0, h/2, w, h/2, fill="black", width=2, tags="axis")
    canvas.create_line(w/2, 0, w/2, h, fill="black", width=2, tags="axis")
    canvas.create_rectangle(
        1, 1, w-2, h-2,
        outline="black",
        width=2,
        tags="border"
    )
    x = (vec[2*i] + 1) * w / 2
    y = (vec[2*i+1] + 1) * h / 2
    canvas_oval(canvas, x, y)

def event_configure(vec, i):
    def __d(event):
        return __configure(event, vec, i)
    return __d
    

def __draw_dot(event, vec, i):
    canvas = event.widget
    canvas.delete("point")
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    canvas_oval(canvas, event.x, event.y)
    vec[2*i] = 2 * event.x / w - 1
    vec[2*i+1] = 2 * event.y / h - 1

def event_draw_dot(vec, i):
    def __d(event):
        return __draw_dot(event, vec, i)
    return __d

def event_get(vec, i):
    def __d(event):
        vec[i] = event.widget.get()
    return __d

def worker(v, u, p, o):
    root = tk.Tk()
    root.title("Parameter Panel")
    
    row1l_frame = tk.Frame(root)
    row1l_frame.pack(fill="both", expand=True)
    for i, d in enumerate(['z', 'c', 'a']):
        label1 = tk.Label(row1l_frame, text=f"V[{d}]", font=(LABEL_FONT, 12))
        label1.grid(row=0, column=i, padx=5, pady=(6, 2))
        row1l_frame.columnconfigure(i, weight=1)
    
    row1_frame = tk.Frame(root)
    row1_frame.pack(fill="both", expand=True)
    
    colors_row1 = ["lightblue", "lightgreen", "lightcoral"]
    
    for i, color in enumerate(colors_row1):
        canvas = tk.Canvas(row1_frame, bg=color, width=200, height=200)
        canvas.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        canvas.bind("<Button-1>", event_draw_dot(v, i))
        canvas.bind("<B1-Motion>", event_draw_dot(v, i))
        canvas.bind("<Configure>", event_configure(v, i))
        row1_frame.columnconfigure(i, weight=1)
    
    row2l_frame = tk.Frame(root)
    row2l_frame.pack(fill="both", expand=True)
    for i, d in enumerate(['z', 'c', 'a']):
        label2 = tk.Label(row2l_frame, text=f"U[{d}]", font=(LABEL_FONT, 12))
        label2.grid(row=0, column=i, padx=5, pady=(6, 2))
        row2l_frame.columnconfigure(i, weight=1)
    
    row2_frame = tk.Frame(root)
    row2_frame.pack(fill="both", expand=True)
    
    colors_row2 = ["plum1", "lightgray", "lightpink"]
    
    for i, color in enumerate(colors_row2):
        canvas = tk.Canvas(row2_frame, bg=color, width=200, height=200)
        canvas.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        canvas.bind("<Button-1>", event_draw_dot(u, i))
        canvas.bind("<B1-Motion>", event_draw_dot(u, i))
        canvas.bind("<Configure>", event_configure(u, i))
        row2_frame.columnconfigure(i, weight=1)

    row3l_frame = tk.Frame(root)
    row3l_frame.pack(fill="both", expand=True)
    for i, d in enumerate(['z', 'c', 'a']):
        label3 = tk.Label(row3l_frame, text=f"P[{d}]", font=(LABEL_FONT, 12))
        label3.grid(row=0, column=i, padx=5, pady=(6, 2))
        row3l_frame.columnconfigure(i, weight=1)
    
    row3_frame = tk.Frame(root)
    row3_frame.pack(fill="both", expand=True)
    
    colors_row3 = ["peachpuff", "LemonChiffon3", "lightyellow"]
    
    for i, color in enumerate(colors_row3):
        canvas = tk.Canvas(row3_frame, bg=color, width=200, height=200)
        canvas.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
        canvas.bind("<Button-1>", event_draw_dot(p, i))
        canvas.bind("<B1-Motion>", event_draw_dot(p, i))
        canvas.bind("<Configure>", event_configure(p, i))
        row3_frame.columnconfigure(i, weight=1)


    row4l_frame = tk.Frame(root)
    row4l_frame.pack(fill="both", expand=True)
    for i, t in enumerate(['Origin (x, y)', 'Δx']):
        label4 = tk.Label(row4l_frame, text=t, font=(LABEL_FONT, 12))
        label4.grid(row=0, column=i, padx=5, pady=(6, 2))
        row4l_frame.columnconfigure(i, weight=i*3+1)

    row4_frame = tk.Frame(root)
    row4_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(row4_frame, bg="lightgray", width=200, height=200)
    canvas.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
    canvas.bind("<Button-1>", event_draw_dot(o, 0))
    canvas.bind("<B1-Motion>", event_draw_dot(o, 0))
    canvas.bind("<Configure>", event_configure(o, 0))
    row4_frame.columnconfigure(0, weight=1)

    scrollBar = tk.Scale(row4_frame, from_=0, to=0.99, resolution=0.00001, orient=tk.HORIZONTAL)
    scrollBar.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    scrollBar.bind("<B1-Motion>", event_get(o, 2))
    row4_frame.columnconfigure(1, weight=4)

    
    root.mainloop()

