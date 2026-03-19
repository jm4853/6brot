This document describes how viewing surface is constructed given the vectors (and scalar) described in the Parameter Panel: $U$, $V$, $P_0$, $O=(x_0, y_0)$, and $\Delta x$.

Let $U,V \in \mathbb{R}^n$ be two linearly independent vectors which define a unique viewing plane through the origin, $P$. First, construct $X_P = \frac {V}{\left|V\right|}$, the first basis vector for the viewing plane, and normalize $U$ as $U_N = \frac {U}{\left|U\right|}$. Then construct $Y_P = U_N - \left(U_N\cdot X_P\right)\cdot X_P = U_N - \text{proj}_{X_P}\left(U_N\right)$. Then $X_P$, $Y_P$ are orthogonal normalized basis vectors for $P$, Let the point $P_0 \in P$, then $P = \left\\{P_0 + sX_P + tY_P \vert t,s\in\mathbb{R}\right\\}$.

> Alert when $U\cdot V = 0$, i.e. $U$ and $V$ are linearly dependent.

Suppose the viewing window is centered at $P_0 \in \mathbb{R}^n$, and $\Delta x, \Delta y \in \mathbb{R}$ describe the width and height of the viewing window proportional to basis vectors $X_P$ and $Y_P$. Let $w_p$ be the width in number of pixels, and let $h_p$ be the height in number of pixels. The lowest $x$ and $y$ values to test are $x_0 = -\frac 1 2 \Delta x$ and $y_0 = -\frac 1 2 \Delta y$. Also the step size for the $x$ and $y$ directions are $s_x = \frac{\Delta x}{w_p}$ and $s_y = \frac {\Delta y}{h_p}$. Then the points that must be tested are:

$\bigcup_{h=1}^{h_p}\bigcup_{w=1}^{w_p}\left(x_0 + s_xw\right)X_P+\left(y_0+s_yh\right)Y_P + P_0$


**Example:** 


Testing $z' = z^2+c$ for divergence.


For $v \in \mathbb{R}^4$, let $v = \left<\text{Re}(z_0), \text{Im}(z_0), \text{Re}(c), \text{Im}(c)\right>$, i.e. $z_0 = v_1 + v_2i$ and $c = v_3+v_4i$


Consider viewing the Mandelbrot set with $z_0 = 0$. Then:
$P_0 = \left<0,0,0,0\right>$
$X_P = \left<0,0,1,0\right>$
$Y_P = \left<0,0,0,1\right>$


Consider viewing the Julia set when $c = -0.5125 + 0.5213i$. Then:
$P_0 = \left<0,0,-0.5125,0.5213\right>$
$X_P = \left<1, 0, 0, 0\right>$
$Y_P = \left<0, 1,0,0\right>$


