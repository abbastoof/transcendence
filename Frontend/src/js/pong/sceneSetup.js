import * as THREE from 'three';
import { GlitchPass } from 'three/examples/jsm/postprocessing/GlitchPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';
import { RGBShiftShader } from 'three/examples/jsm/shaders/RGBShiftShader.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';

export function initializeScene(renderer, scene, camera, composer) {
    // Post-processing effects
    const renderPass = new RenderPass( scene, camera );
    composer.addPass( renderPass );
    const glitchPass = new GlitchPass();
    composer.addPass( glitchPass );

    const effect2 = new ShaderPass( RGBShiftShader );
    effect2.uniforms[ 'amount' ].value = 0.0015;
    composer.addPass( effect2 );

    const outputPass = new OutputPass();
    composer.addPass( outputPass );

    // Camera setup
    camera.position.set(0, 400, 400); // Adjust these values for your desired isometric angle
    camera.lookAt(0, 0, 0);
    camera.zoom = 2.0;

    // Scene setup
    scene.background = new THREE.Color(0x000000);
    const ambientLight = new THREE.AmbientLight(0x909090);
    scene.add(ambientLight);

    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.7);
    directionalLight1.position.set(50, 100, 50);
    directionalLight1.castShadow = true;
    scene.add(directionalLight1);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight2.position.set(-50, 100, -50);
    scene.add(directionalLight2);

    const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.6);
    hemiLight.position.set(0, 200, 0);
    scene.add(hemiLight);
    console.log("scene was initialized")
}