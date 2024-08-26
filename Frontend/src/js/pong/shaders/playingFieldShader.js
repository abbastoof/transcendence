export const playingFieldShader = `
    uniform float iTime;
    uniform vec2 iResolution;
    uniform float xRand;
    uniform float yRand;
    uniform float multiRand;
    uniform float ballDx;
    varying vec2 vUv;

    float noise21(vec2 p){
        return fract(sin(p.x * xRand + p.y * yRand) * multiRand);
    }

    float SmoothNoise(vec2 uv) {
        vec2 lv = fract(uv);
        vec2 id = floor(uv);

        lv = lv * lv * (3.0 - 2. * lv);
        float bl = noise21(id);
        float br = noise21(id + vec2(1, 0));
        float b = mix(bl, br, lv.x);

        float tl = noise21(id + vec2(0, 1));
        float tr = noise21(id + vec2(1, 1));
        float t = mix(tl, tr, lv.x);

        return mix(b, t, lv.y);
    }

    float SmoothNoise2(vec2 uv) {
        float c = SmoothNoise(uv * cos(iTime * 0.05));
        c += SmoothNoise(uv * 8.0) * 0.5;
        c += SmoothNoise(uv * 16.0) * 0.25;
        c += SmoothNoise(uv * 32.0) * 0.125;
        c += SmoothNoise(uv * 64.0) * 0.0625;
        return c / 5.0;
    }

    void mainImage(out vec4 fragColor, in vec2 fragCoord) {
        vec2 uv = fragCoord / iResolution.xy;
        //uv.y -= iTime * 0.09;
        uv.x -= iTime * 0.1 * ballDx;
        float c = SmoothNoise2(uv);
        vec3 col = vec3(cos(c * iTime + xRand)* .01, cos(c * iTime)*.05, sin(c * iTime - yRand) * .8);

        fragColor = vec4(col, 1.0);
    }

    void main() {
        mainImage(gl_FragColor, vUv * iResolution.xy);
    }
`;



