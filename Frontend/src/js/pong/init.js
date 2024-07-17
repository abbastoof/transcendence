// init.js
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { initializeScene } from './sceneSetup.js';
import { WIDTH, HEIGHT } from './constants.js';

export function init() {
    // Create renderer
    const renderer = new THREE.WebGLRenderer();
    const container = document.getElementById('pongCanvas');
    
    if (container !== null) {
        renderer.setSize(WIDTH, HEIGHT);
        container.appendChild(renderer.domElement);
    }
    else {
        setTimeout(init, 0);
    }
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
 
    // Initialize the scene
    initializeScene(renderer, scene, camera, composer);

    return { renderer, scene, camera, composer };
}