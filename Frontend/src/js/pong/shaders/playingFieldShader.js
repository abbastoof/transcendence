export const playingFieldShader = `
    uniform vec2 iResolution;
    varying vec2 vUv;

    void mainImage(out vec4 fragColor, in vec2 fragCoord) {
        vec3 col = vec3(0.576, 0.914, 0.745);

        fragColor = vec4(col, 1.0);
    }

    void main() {
        mainImage(gl_FragColor, vUv * iResolution.xy);
    }
`;