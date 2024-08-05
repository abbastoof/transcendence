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
        vec3 col = vec3(cos(c * iTime)* .09, cos(c * iTime)*.01, sin(c * iTime + xRand) * .5);

        fragColor = vec4(col, 1.0);
    }

    void main() {
        mainImage(gl_FragColor, vUv * iResolution.xy);
    }
`;

export const toinenShaderi = `

    uniform float iTime;
    uniform vec2 iResolution;
    varying vec2 vUv;

    float Band(float t, float start, float end, float blur){
        float step1 = smoothstep(start - blur, start + blur, t);
        float step2 = smoothstep(end + blur, end - blur, t);
        
        return step1 * step2;
    }
    
    float Rect(vec2 uv, vec4 sides, float blur)
    {
        float band1 = Band(uv.x, sides.x, sides.y, blur);
        float band2 = Band(uv.y, sides.z, sides.w, blur);
        return band1 * band2;
    }
    
    void mainImage( out vec4 fragColor, in vec2 fragCoord )
    {
        vec2 uv = fragCoord/iResolution.xy;
        
        uv -= .5;
        uv.x *= iResolution.x/iResolution.y;
        //vec3 col = 1. *tan(iTime-(uv.yxx * 2.)+vec3(0.0, 1.1, 4.4 )/ iTime );
        float mask = 0.;
        
        
        float x = uv.x;
        
        float m = (x+tan(iTime)*2.1)*(x-sin(iTime));
        float y = uv.y-m;
    
        x /= 5.;
        
        vec4 rec = vec4(-.2*abs(cos(iTime *.8))-.9, .2*abs(sin(iTime *.8))+.2, -.2*abs(cos(iTime*.1))-.2, .5*-abs(-cos(iTime*.6)));
        mask = Rect(vec2(x,y), rec, .6);
        
        vec3 col = vec3(tan(iTime),1.*m,1.-sin(iTime*.1)) * mask;
        //&col *= mask;
        // Output to screen
        fragColor = vec4(col,1.0);
    }
    void main() {
        mainImage(gl_FragColor, vUv * iResolution.xy);
    }
`
