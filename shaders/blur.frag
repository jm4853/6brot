#version 400

uniform sampler2D screenTexture; // The Mandelbrot image
uniform vec2 texelSize;          // 1.0 / (window_width, window_height)
out vec4 fragColor;

void main() {
    // Simple 3x3 Box Blur (Averages center + 8 neighbors)
    vec3 result = vec3(0.0);
    for (int x = -1; x <= 1; x++) {
        for (int y = -1; y <= 1; y++) {
            vec2 offset = vec2(x, y) * texelSize;
            result += texture(screenTexture, gl_FragCoord.xy / textureSize(screenTexture, 0) + offset).rgb;
        }
    }
    fragColor = vec4(result / 9.0, 1.0);
}
