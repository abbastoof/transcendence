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
import { globalState } from './globalState.js';
const glitchPass = new GlitchPass();
globalState.glitchPass = glitchPass;
const rgbShift = new ShaderPass( RGBShiftShader );
globalState.rgbShift = rgbShift;

// init 
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
    // Initialize the scene
    initializeScene(renderer, scene, camera, composer);

    return { renderer, scene, camera, composer };
}

// Initializes the composer for post-processing effects
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

    const outputPass = new OutputPass();
    composer.addPass( outputPass );
}

// Initializes the camera
// camera position is set to isometric view, looking at the origin
// position is based on the global state invertedView
// which is set to true if the game is a remote game, and the local player is player 2
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
/**
 * Initializes the lights in the scene.
 * 
 * @param {THREE.Scene} scene - The scene to which the lights will be added.
 */
function initLights(scene) {
    // AmbientLight: This light globally illuminates all objects in the scene equally.
    // This can be used to provide a basic level of lighting to a scene.
    const ambientLight = new THREE.AmbientLight(0x909090);
    scene.add(ambientLight);

    // DirectionalLight1: This light gets emitted in a specific direction. It acts as though it is infinitely far away,
    // and the rays produced by it are parallel. It can be used to simulate sunlight; in this case, it's coming from the front right above.
    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.7);
    directionalLight1.position.set(100, 100, 100);
    directionalLight1.castShadow = true;
    scene.add(directionalLight1);

    // DirectionalLight2: Another directional light, this one coming from the back left above.
    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight2.position.set(-100, 100, -100);
    scene.add(directionalLight2);

    // HemisphereLight: This light is positioned directly above the scene, but it falls off as you get closer to the poles,
    // leading to a cooler (blueish) light from the sky and a warmer (reddish) light from the ground.
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
