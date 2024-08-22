export const scoreBoardShader = `
    uniform vec3 color;
    uniform float iTime;
    uniform float base;
    uniform float speed;
    varying vec2 vUv;

    void main() {
        // Create a time-based color animation
        float r = base + 0.9 * sin(iTime * speed + vUv.x * .1);
        float g = base + 0.9 * sin(iTime * speed + vUv.y * .1);
        float b = base + 0.9 * sin(iTime * speed);

        vec3 animatedColor = vec3(r, g, b) * color;

        gl_FragColor = vec4(animatedColor, 1.0);
    }
`;