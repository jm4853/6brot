#version 400
/*
Each 64-bit real value is represented with a larger and smaller component.
https://godotengine.org/article/emulating-double-precision-gpu-render-large-worlds/
```
double x = ...;
float big_x = (float)x;
float small_x = (float)(x - (double)big_x);
```
Because `big_x` is the closest float to `x`, the difference `x - big_x` is very small.
This ensures a level of precision, since the distribution of floating point values is
much higher near zero.
*/


in vec2 v_pos;
out vec4 f_color;

uniform vec4 u_O;
uniform vec4 u_D;

uniform vec4 u_Xz;
uniform vec4 u_Xc;
uniform vec4 u_Xa;

uniform vec4 u_Yz;
uniform vec4 u_Yc;
uniform vec4 u_Ya;

uniform vec4 u_Pz;
uniform vec4 u_Pc;
uniform vec4 u_Pa;

uniform vec4 u_AvgStep; // Step size for gathering color average (should be 0.25 * (range / resolution), i.e. 25% of a pixel)
uniform bool u_DoAvg;

uniform float u_one;





// https://stackoverflow.com/questions/56195735/cant-find-a-way-to-color-the-mandelbrot-set-the-way-im-aiming-for
vec3 spectral_color(float l)        // RGB <0,1> <- lambda l <400,700> [nm]
{
    float t;  vec3 c=vec3(0.0,0.0,0.0);
         if ((l>=400.0)&&(l<410.0)) { t=(l-400.0)/(410.0-400.0); c.r=    +(0.33*t)-(0.20*t*t); }
    else if ((l>=410.0)&&(l<475.0)) { t=(l-410.0)/(475.0-410.0); c.r=0.14         -(0.13*t*t); }
    else if ((l>=545.0)&&(l<595.0)) { t=(l-545.0)/(595.0-545.0); c.r=    +(1.98*t)-(     t*t); }
    else if ((l>=595.0)&&(l<650.0)) { t=(l-595.0)/(650.0-595.0); c.r=0.98+(0.06*t)-(0.40*t*t); }
    else if ((l>=650.0)&&(l<700.0)) { t=(l-650.0)/(700.0-650.0); c.r=0.65-(0.84*t)+(0.20*t*t); }
         if ((l>=415.0)&&(l<475.0)) { t=(l-415.0)/(475.0-415.0); c.g=             +(0.80*t*t); }
    else if ((l>=475.0)&&(l<590.0)) { t=(l-475.0)/(590.0-475.0); c.g=0.8 +(0.76*t)-(0.80*t*t); }
    else if ((l>=585.0)&&(l<639.0)) { t=(l-585.0)/(639.0-585.0); c.g=0.84-(0.84*t)           ; }
         if ((l>=400.0)&&(l<475.0)) { t=(l-400.0)/(475.0-400.0); c.b=    +(2.20*t)-(1.50*t*t); }
    else if ((l>=475.0)&&(l<560.0)) { t=(l-475.0)/(560.0-475.0); c.b=0.7 -(     t)+(0.30*t*t); }
    return c;
}

vec4 cx_add(vec4 x, vec4 y) {
    vec2 a = x.xy;
    vec2 b = x.zw;
    vec2 c = y.xy;
    vec2 d = y.zw;
    return vec4(a.x+c.x, a.y+c.y, b.x+d.x, b.y+d.y);
}

//---
// https://andrewthall.org/papers/df64_qf128.pdf

vec2 df64_add(vec2 a, vec2 b);
vec2 df64_mult(vec2 a, vec2 b);
bool df64_eq(vec2 a, vec2 b);
bool df64_lt(vec2 a, vec2 b);

vec4 df64c_add(vec4 a, vec4 b);
vec4 df64c_mult(vec4 a, vec4 b);


bool df64_eq(vec2 a, vec2 b) {
    return ((a.x == b.x) && (a.y == b.y));
}

vec2 quickTwoSum(float a, float b) {
    // assumes a > b
    float s = (a + b) * u_one;
    float e = b - (s - a);
    return vec2(s, e);
}

vec2 twoSum(float a, float b) {
    float s = (a + b) * u_one;
    float v = (s - a) * u_one;
    float e = (a - (s - v)) + (b - v);
    return vec2(s, e);
}

vec2 df64_add(vec2 a, vec2 b) {
    vec2 s = twoSum(a.x, b.x);
    vec2 t = twoSum(a.y, b.y);
    s.y += t.x;
    s = quickTwoSum(s.x, s.y);
    s.y += t.y;
    s = quickTwoSum(s.x, s.y);
    return s;
}

vec2 split(float a) {
    const float split = 4097;   // (1 << 12) + 1 ?
    float t = (a * split) * u_one;
    float a_l = (t - (t - a)) * u_one;
    float a_s = a - a_l;
    return vec2(a_l, a_s);
}

vec2 twoProd(float a, float b) {
    float p = (a * b) * u_one;
    vec2 aS = split(a);
    vec2 bS = split(b);
    float err = ((aS.x * bS.x - p)
                + aS.x * bS.y + aS.y*bS.x)
                + aS.y * bS.y;
    return vec2(p, err);
}

vec2 df64_mult(vec2 a, vec2 b) {
    vec2 p = twoProd(a.x, b.x);
    p.y += a.x * b.y;
    p.y += a.y * b.x;
    p = quickTwoSum(p.x, p.y);
    return p;
}
//==

vec4 df64c_add(vec4 a, vec4 b) {
    // eltwise add
    return vec4(df64_add(a.xy, b.xy), df64_add(a.zw, b.zw));
}

vec4 df64c_mult(vec4 a, vec4 b) {
    // (a + bi)(c + di) = (ac-bd) + (ad + bc)i
    vec2 r = df64_add(df64_mult(a.xy, b.xy), (df64_mult(a.zw, b.zw) * -1.0));
    vec2 i = df64_add(df64_mult(a.xy, b.zw), df64_mult(a.zw, b.xy));
    return vec4(r, i);
}

vec4 df64v2_mult(vec4 a, vec4 b) {
    // eltwise mult
    return vec4(df64_mult(a.xy, b.xy), df64_mult(a.zw, b.zw));
}

vec2 df64c_dot(vec4 a, vec4 b) {
    vec4 t = df64v2_mult(a, b);    
    return df64_add(t.xy, t.zw);
}

vec4 df64v2_sdot(vec2 x, vec4 v) {
    return vec4(df64_mult(x, v.xy), df64_mult(x, v.zw));
}

//---

float test_mandel(vec4 z, vec4 c, int n) {
    int i = 0;
    vec2 t = vec2(0.0, 0.0);
    for( i = 0; i < n; i++ ) {
        //   t = z_r ** 2 + z_i ** 2
        t = df64_add(df64_mult(z.xy, z.xy), df64_mult(z.zw, z.zw));
        // if( t.x > 256.0 ) {
        if( t.x > 4.0 ) {
            break;
        }
        // z = z^2 + c
        // z = df64c_add(df64c_mult(z, z), c);
        z = df64c_add(df64c_mult(z, z), c);
    }
    // float smooth_i = float(i);
    // if( (i < n) && (t.x > 0.0) ) {
    //     smooth_i = float(i) + 1.0 - log2(log2(sqrt(t.x)));
    // }
    // return smooth_i;
    return float(i)/float(n);
}

void main() {
    // vec4 a = df64c_add(df64c_add(df64v2_sdot(p.xy, u_Xa), df64v2_sdot(p.zw, u_Ya)), u_Pa);
    // z = [u_Xz, u_Yz] * p + u_Pz    = p.x * u_Xz + p.y * u_Yz + u_Pz
    // vec4 z = df64c_add(df64c_add(df64v2_sdot(p.xy, u_Xz), df64v2_sdot(p.zw, u_Yz)), u_Pz);
    // c = [u_Xc, u_Yc] * p + u_Pc    = p.x * u_Xc + p.y * u_Yc + u_Pc
    // vec4 c = df64c_add(df64c_add(df64v2_sdot(p.xy, u_Xc), df64v2_sdot(p.zw, u_Yc)), u_Pc);
    vec4 vp = vec4(split(v_pos.x), split(v_pos.y));
    //   p = vp * u_D + u_O       (real pos = screen pos * zoom + origin offset)
    vec4 ap = df64c_add(df64v2_mult(vp, u_D), u_O);     // actual p
    vec4 p = vec4(ap);

    int n_halo = 2;
    float halo_weight = 1.0;
    float center_weight = 1.0;
    int n = 600;

    vec4 z = df64c_add(df64c_add(df64v2_sdot(p.xy, u_Xz), df64v2_sdot(p.zw, u_Yz)), u_Pz);
    vec4 c = df64c_add(df64c_add(df64v2_sdot(p.xy, u_Xc), df64v2_sdot(p.zw, u_Yc)), u_Pc);

    float q = test_mandel(z, c, center_weight * n);

    if( u_DoAvg ) {
        q *= center_weight / (halo_weight + center_weight);

        p = df64c_add(ap, vec4(vec2(0.0f), u_AvgStep.zw * -1.0));
        z = df64c_add(df64c_add(df64v2_sdot(p.xy, u_Xz), df64v2_sdot(p.zw, u_Yz)), u_Pz);
        c = df64c_add(df64c_add(df64v2_sdot(p.xy, u_Xc), df64v2_sdot(p.zw, u_Yc)), u_Pc);
        q += halo_weight * test_mandel(z, c, n) / (n_halo * halo_weight + center_weight);
        
        p = df64c_add(ap, vec4(vec2(0.0f), u_AvgStep.zw));
        z = df64c_add(df64c_add(df64v2_sdot(p.xy, u_Xz), df64v2_sdot(p.zw, u_Yz)), u_Pz);
        c = df64c_add(df64c_add(df64v2_sdot(p.xy, u_Xc), df64v2_sdot(p.zw, u_Yc)), u_Pc);
        q += halo_weight * test_mandel(z, c, n) / (n_halo * halo_weight + center_weight);
    }


    // f_color = vec4(avg_c, 1.0);
    // q = pow(q, 0.2);
    f_color=vec4(spectral_color(400.0+(300.0*q)),1.0);
}
