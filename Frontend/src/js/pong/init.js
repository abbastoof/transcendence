// init.js
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { WIDTH, HEIGHT } from './constants.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';
import { scanlineShader } from './shaders/scanlineShader.js';
import { GlitchPass } from 'three/examples/jsm/postprocessing/GlitchPass.js';
import { RGBShiftShader } from 'three/examples/jsm/shaders/RGBShiftShader.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { FilmPass } from 'three/examples/jsm/postprocessing/FilmPass.js';
import { globalState } from './globalState.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
const glitchPass = new GlitchPass();
globalState.glitchPass = glitchPass;
const rgbShift = new ShaderPass( RGBShiftShader );
globalState.rgbShift = rgbShift;

export function init(canvas) {
    // Create renderer
    if (!canvas) {
        console.error('Canvas element is not provided.');
        return;
    }
    const renderer = new THREE.WebGLRenderer({ canvas });
    renderer.setSize(canvas.width, canvas.height);
    renderer.setPixelRatio(window.devicePixelRatio); // Handle high-DPI displays
    
    const scene = new THREE.Scene();

    const aspect = WIDTH / HEIGHT;
    const frustumSize = 750; // Adjust as needed for your scene scale
    var camera = new THREE.OrthographicCamera(
        frustumSize * aspect / -2,
        frustumSize * aspect / 2,
        frustumSize / 2,
        frustumSize / -2,
        .1,
        2000
    );
    // Create composer for postprocessing
    const composer = new EffectComposer( renderer );
    // composer.addPass(new OutputPass());
    console.log(scene)
    // Initialize the scene
    initializeScene(renderer, scene, camera, composer);

    return { renderer, scene, camera, composer };
}


function initComposer (renderer, composer, scene, camera) {
    // Post-processing effects
    const renderPass = new RenderPass( scene, camera );
    composer.addPass( renderPass );
    
    glitchPass.enabled = false;
    glitchPass.goWild = true;
    composer.addPass( glitchPass );

    rgbShift.uniforms[ 'amount' ].value = 0.0015;
    rgbShift.enabled = true;
    composer.addPass( rgbShift );
    
    const scanlinePass = new ShaderPass(scanlineShader);
    scanlinePass.enabled = true;
    composer.addPass(scanlinePass);
    // const filmPass = new FilmPass( 0.9, .2, 900, false );
    // composer.addPass( filmPass );

    const outputPass = new OutputPass();
    composer.addPass( outputPass );
}

function initCamera(camera) {
    // Camera setup
    if (globalState.invertedView === true) {
        camera.position.set(400, 400, -400); // Adjust these values for your desired isometric angle
    }
    else {
        camera.position.set(-400, 400, 400); // Adjust these values for your desired isometric angle
    }
    camera.lookAt(0, 0, 0);
    camera.zoom = 2.0;
}

function initLights(scene) {
    const ambientLight = new THREE.AmbientLight(0x909090);
    scene.add(ambientLight);

    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.7);
    directionalLight1.position.set(100, 100, 100);
    directionalLight1.castShadow = true;
    scene.add(directionalLight1);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight2.position.set(-100, 100, -100);
    scene.add(directionalLight2);

    const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.6);
    hemiLight.position.set(0, 200, 0);
    scene.add(hemiLight);
}

function initializeScene(renderer, scene, camera, composer) {
    initComposer(renderer, composer, scene, camera);
    initCamera(camera);
    scene.background = new THREE.Color(0x000000);
    initLights(scene);
    // Scene setup
}
