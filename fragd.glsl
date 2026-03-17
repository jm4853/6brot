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

uniform float u_one;
uniform vec2 u_pi;




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

vec2 df64_diff(vec2 a, vec2 b) {
    return df64_add(a, b * -1.0);
}

vec2 df64_div(vec2 b, vec2 a) {
    float xn = 1.0f / a.x;
    vec2 yn = split(b.x * xn);
    float diff = (df64_diff(b, df64_mult(a, yn))).x;
    vec2 prod = twoProd(xn, diff);

    return df64_add(yn, prod);
}

vec2 df64_sqr(vec2 a) {
    return df64_mult(a, a);
}

vec2 df64_sqrt(vec2 a) {
    float xn = 1.0f / sqrt(a.x);
    vec2 yn = split(a.x*xn);
    vec2 ynsqr = df64_sqr(yn);

    float diff = (df64_diff(a, ynsqr)).x;
    vec2 prod = twoProd(xn, diff) / 2.0;

    return df64_add(yn, prod);
}

vec2 df64_expTAYLOR(vec2 a) {
    // const float thresh = 1.0e-20*exp(a.x);
    float thresh = 1.0e-20*exp(a.x);

    int i = 0;
    float m = 2.0f;
    vec2 f = vec2(2.0f, 0.0f);
    vec2 s = df64_add(split(1.0f), a);
    vec2 p = df64_sqr(a);
    vec2 t = p / 2.0f;
    while( abs(t.x) > thresh ) {
        s = df64_add(s, t);
        p = df64_mult(p, a);
        m += 1.0f;
        f = df64_mult(f, split(m));
        t = df64_div(p, f);
        if( i >= 100 ) break;
        i++;
    }

    return df64_add(s, t);
}

vec2 df64_log(vec2 a) {
    vec2 xi = vec2(0.0f, 0.0f);

    if(!df64_eq(a, split(1.0f))) {
        if( a.x <= 0.0 ) {
            xi = vec2(log(a.x));   // Return NaN
        } else {
            xi.x = log(a.x);
            xi = df64_add(df64_add(xi, df64_mult(df64_expTAYLOR(-xi), a)), split(-1.0));
        }
    }

    return xi;
}

vec2 __df64_atanTAYLOR(vec2 a) {
    // FROM AI
    // const float thresh = 1.0e-20*exp(a.x);
    float thresh = 1.0e-20*exp(a.x) * u_one;
    
    vec2 s = a;
    vec2 x2 = df64_mult(a, a);
    vec2 p = a;
    float n = 1.0;
    float sgn = 1.0;
    
    vec2 t = a; 
    
    for(int i = 0; i < 100; i++) {
        p = df64_mult(p, x2);
        n += 2.0 * u_one;
        sgn *= -1.0;
        
        // t = (sign * x^n) / n
        t = df64_div(df64_mult(vec2(sgn, 0.0), p), vec2(n, 0.0 * u_one));
        
        s = df64_add(s, t);
        
        if (abs(t.x) < thresh) break;
    }
    
    return s;
}

vec2 df64_atanTAYLOR(vec2 a) {
    if( abs(a.x) > 1.0 ) {
        return df64_add(u_pi * u_one, __df64_atanTAYLOR(df64_div(split(1.0), a)) * -1.0);
    }
    return __df64_atanTAYLOR(a);
}

vec4 df64_sincosTAYLOR(vec2 a) {
    // const float thresh = 1.0e-20 * abs(a.x) * u_one;
    float thresh = 1.0e-20 * abs(a.x) * u_one;

    vec2 t;
    vec2 p;
    vec2 f;
    vec2 s;
    vec2 x;
    float m;

    vec2 sin_a, cos_a;
    if( a.x == 0.0f ) {
        sin_a = vec2(0.0f, 0.0f);
        cos_a = vec2(1.0f, 0.0f);
    } else {
        x = df64_sqr(a) * -1.0;
        s = a;
        p = a;
        m = u_one;
        f = vec2(1.0f, 0.0f);
        for( int i = 0; i < 100; i++ ) {
            p = df64_mult(p, x);
            m += 2.0f;
            f = df64_mult(f, split(m * (m - 1)));
            t = df64_div(p, f);
            s = df64_add(s, t);
            if( abs(t.x) < thresh ) break;
        }

        sin_a = s;
        cos_a = df64_sqrt(df64_add(split(1.0f), df64_sqr(s) * -1.0));
    }

    return vec4(sin_a, cos_a);
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

vec4 df64c_pow(vec4 z, vec4 p) {
    vec2 z_dot = df64_log(df64_sqrt(df64c_dot(z, z)));
    vec2 z_atan = df64_atanTAYLOR(df64_div(z.zw, z.xy));
    vec2 t_r = df64c_dot(p, vec4(z_dot, z_atan));
    vec2 t_i = df64c_dot(vec4(p.zw, p.xy), vec4(z_dot, z_atan));
    vec4 sincos = df64_sincosTAYLOR(t_i);
    return df64v2_sdot(df64_expTAYLOR(t_r), vec4(sincos.zw, sincos.xy));
}

//---

void main() {
    vec4 vp = vec4(split(v_pos.x / 2.0), split(v_pos.y / 2.0));
    //   p = vp * u_D + u_O       (real pos = screen pos * zoom + origin offset)
    vec4 p = df64c_add(df64v2_mult(vp, u_D), u_O);
    
    
    //   z = [u_Xz, u_Yz] * p + u_Pz    = p.x * u_Xz + p.y * u_Yz + u_Pz
    vec4 z = df64c_add(df64c_add(df64v2_sdot(p.xy, u_Xz), df64v2_sdot(p.zw, u_Yz)), u_Pz);
    //   c = [u_Xc, u_Yc] * p + u_Pc    = p.x * u_Xc + p.y * u_Yc + u_Pc
    vec4 c = df64c_add(df64c_add(df64v2_sdot(p.xy, u_Xc), df64v2_sdot(p.zw, u_Yc)), u_Pc);
    //   a = [u_Xa, u_Ya] * p + u_Pa    = p.x * u_Xa + p.y * u_Ya + u_Pa
    vec4 a = df64c_add(df64c_add(df64v2_sdot(p.xy, u_Xa), df64v2_sdot(p.zw, u_Ya)), u_Pa);


    int n = 1000;
    // int n = 200;
    int i = 0;
    vec2 t = vec2(0.0, 0.0);
    for( i = 0; i < n; i++ ) {
        //   t = z_r ** 2 + z_i ** 2
        t = df64_add(df64_mult(z.xy, z.xy), df64_mult(z.zw, z.zw));
        if( t.x > 256.0 ) {
            break;
        }
        // z = z^2 + c
        // z = df64c_add(df64c_mult(z, z), c);
        // z = z^a + c
        z = df64c_add(df64c_pow(z, a), c);
    }
    // float q = float(i) / float(n);
    // // q = pow(q, 0.2);

    float smooth_i = float(i);
    if( (i < n) && (t.x > 0.0) ) {
        smooth_i = float(i) + 1.0 - log2(log2(sqrt(t.x)));
    }
    float q = clamp(smooth_i / float(n), 0.0, 1.0);


    f_color=vec4(spectral_color(400.0+(300.0*q)),1.0);
}
