DISTANCE_SHADER='''
    #version 330
    in vec2 v_pos;
    out vec4 f_color;
    uniform vec2 u_o;
    uniform vec2 u_d;
    uniform vec4 u_Xp;
    uniform vec4 u_Yp;
    uniform vec4 u_P0;

    void main() {
        // Viewing Plane (x,y) coords
        vec2 p = ((v_pos * u_d) / 2.0) + u_o;
        // 4d (Re(z), Im(z), Re(c), Im(c)) coords
        vec4 P = (p.x * u_Xp) + (p.y * u_Yp) + u_P0;
        vec2 z = P.xy;
        vec2 c = P.zw;

        
        // vec2 c = ((v_pos * u_d) / 2.0) + u_o;
        // vec2 z = ((v_pos * u_d) / 2.0) + u_o;
        // vec2 c = u_c;
        // vec2 c = p.zw;
        float m2 = 0.0;
        vec2 dz = vec2(0.0);
        for( int i=0; i<300; i++ )
        {
            if( m2>1024.0 ) { di=0.0; break; }

            // Z' -> 2·Z·Z' + 1
            dz = 2.0*vec2(z.x*dz.x-z.y*dz.y, z.x*dz.y + z.y*dz.x) + vec2(1.0,0.0);

            // Z -> Z² + c
            z = vec2( z.x*z.x - z.y*z.y, 2.0*z.x*z.y ) + c;

            m2 = dot(z,z);
        }

        // distance
        // d(c) = |Z|·log|Z|/|Z'|
        float d = 0.5*sqrt(dot(z,z)/dot(dz,dz))*log(dot(z,z));
        //if( di>0.5 ) d=0.0;

        d = clamp( pow(4.0*d,0.2), 0.0, 1.0 );
        vec3 col = vec3(d);

        // vec3 col = vec3(pow(d*360, 1.5), 50, );

        f_color = vec4( col, 1.0 );
    }
'''
ITER_SHADER='''
    #version 330
    in vec2 v_pos;
    out vec4 f_color;
    uniform vec2 u_o;
    uniform vec2 u_d;
    uniform vec4 u_Xp;
    uniform vec4 u_Yp;
    uniform vec4 u_P0;
    uniform vec2 u_Ax;
    uniform vec2 u_Ay;
    uniform vec2 u_Ap;

	#define PI 3.14159265358979323846

    vec2 cx_pow(vec2 z, vec2 p) {
        
        float t_r = dot(p, vec2(log(sqrt(dot(z, z))), atan(z.y, z.x)));
        float t_i = dot(vec2(p.y, p.x), vec2(log(sqrt(dot(z, z))), atan(z.y, z.x)));
        return exp(t_r) * vec2(cos(t_i), sin(t_i));
    }


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

    void main() {
        // Viewing Plane (x,y) coords
        vec2 p = ((v_pos * u_d) / 2.0) + u_o;

        // 4d (Re(z), Im(z), Re(c), Im(c)) coords
        vec4 P = (p.x * u_Xp) + (p.y * u_Yp) + u_P0;

        vec2 z = P.xy;
        vec2 c = P.zw;
        vec2 a = (p.x * u_Ax) + (p.y * u_Ay) + u_Ap;

        // float n = 200;
        float n = 1000;

        int i = 0;
        for( i=0; i<n; i++ ) {
            if( dot(z, z) > 4 ) { break; }
            z = cx_pow( z, a ) + c;
        }

        float q=float(i)/float(n);
        // q = pow(q,0.2);
        f_color=vec4(spectral_color(400.0+(300.0*q)),1.0);

    }
'''
