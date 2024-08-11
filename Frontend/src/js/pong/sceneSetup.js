import * as THREE from 'three';
import { GlitchPass } from 'three/examples/jsm/postprocessing/GlitchPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';
import { RGBShiftShader } from 'three/examples/jsm/shaders/RGBShiftShader.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { FilmPass } from 'three/examples/jsm/postprocessing/FilmPass.js';
import { globalState } from './globalState.js';

const glitchPass = new GlitchPass();
globalState.glitchPass = glitchPass;
const rgbShift = new ShaderPass( RGBShiftShader );
globalState.rgbShift = rgbShift;
export function initializeScene(renderer, scene, camera, composer) {
    // Post-processing effects
    const renderPass = new RenderPass( scene, camera );
    composer.addPass( renderPass );
    
    glitchPass.enabled = false;
    glitchPass.goWild = true;
    composer.addPass( glitchPass );



    rgbShift.uniforms[ 'amount' ].value = 0.0015;
    rgbShift.enabled = false;
    composer.addPass( rgbShift );

    const filmPass = new FilmPass( 0.9, .2, 900, false );
    composer.addPass( filmPass );

    const outputPass = new OutputPass();
    composer.addPass( outputPass );

    // Camera setup
   if (globalState.invertedView === true) {
        camera.position.set(400, 400, -400); // Adjust these values for your desired isometric angle
   }
    else {
        camera.position.set(-400, 400, 400); // Adjust these values for your desired isometric angle
    }
    camera.lookAt(0, 0, 0);
    camera.zoom = 2.0;

    // Scene setup
    scene.background = new THREE.Color(0x000000);
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
    console.log("scene was initialized")
}