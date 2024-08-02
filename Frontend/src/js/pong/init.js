// init.js
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { initializeScene } from './sceneSetup.js';
import { WIDTH, HEIGHT } from './constants.js';

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