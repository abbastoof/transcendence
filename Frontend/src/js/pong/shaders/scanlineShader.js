import * as THREE from 'three';
import { WIDTH, HEIGHT } from '../constants.js';

export const scanlineShader = {
    uniforms: {
        iResolution: { value: new THREE.Vector2(WIDTH, HEIGHT) },
        tDiffuse: { value: null },  // the rendered scene texture
        scanlineIntensity: { value: 0.5 },  // adjust to reduce darkness
    },
    vertexShader: `
        varying vec2 vUv;
        void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    `,
    fragmentShader: `
        uniform vec2 iResolution;
        uniform sampler2D tDiffuse;
        uniform float scanlineIntensity;
        varying vec2 vUv;

        float Scanlines(float x, float repeat, float modValue) {
            x = floor(x * repeat);  // Adding iTime to create movement
            return mod(x, modValue) / modValue;
        }

        void main() {
            vec2 fragCoord = vUv * iResolution.xy;
            vec2 uv = fragCoord / iResolution.xy;

            float repeat = 300.0;  // Number of scanlines
            float modValue = 2.0;   // Alternation between light and dark lines
            float scanline = Scanlines(uv.y, repeat, modValue);

            vec4 color = texture2D(tDiffuse, vUv);

            // Blend the scanline effect with the original color
            color.rgb = mix(color.rgb, color.rgb * scanline, scanlineIntensity);

            gl_FragColor = color;
        }
    `
};
