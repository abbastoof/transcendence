import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { RGBShiftShader } from 'three/addons/shaders/RGBShiftShader.js';
import { DotScreenShader } from 'three/addons/shaders/DotScreenShader.js';
import { GlitchPass } from 'three/addons/postprocessing/GlitchPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { randFloat } from 'three/src/math/MathUtils';

const randomX = randFloat(50.0, 690.0);
const randomY = randFloat(2124.0, 5291.0);
const randomMultiplier = randFloat(625.0, 90909.0);
console.log("random x: " + randomX);
console.log("random y: " + randomY);
console.log("random multiplier: " + randomMultiplier);
// Vertex shader code
const vertexShader = `
    varying vec2 vUv;

    void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
`;

const fragmentShader = `
    uniform float iTime;
    uniform vec2 iResolution;
    uniform float xRand;
    uniform float yRand;
    uniform float multiRand;
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
        uv.y -= iTime * 0.01;
        float c = SmoothNoise2(uv);
        vec3 col = vec3(c);//vec3(sin(c * iTime));// * .09, fract(c * iTime * .05), fract(c));

        fragColor = vec4(col, 1.0);
    }

    void main() {
        mainImage(gl_FragColor, vUv * iResolution.xy);
    }
`;


const WIDTH = 800;
const HEIGHT = 600;
const BALL_SIZE_RATIO = 0.01;
const BALL_SIZE = Math.min(WIDTH, HEIGHT) * BALL_SIZE_RATIO;
const PADDLE_SPEED = 5.0;
const BALL_SPEED = 5.0;
const PADDLE_THICKNESS = WIDTH / 50;
const PADDLE_WIDTH = WIDTH / 8;
const LEFT_PADDLE_START = new THREE.Vector3(-(WIDTH / 2) + 8, 0, 0);
const RIGHT_PADDLE_START = new THREE.Vector3((WIDTH / 2) - 8, 0, 0);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(WIDTH, HEIGHT);
document.body.appendChild(renderer.domElement);

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
//const helper = new THREE.CameraHelper(camera);
//scene.add(helper);


const composer = new EffectComposer( renderer );
const renderPass = new RenderPass( scene, camera );
composer.addPass( renderPass );





// const effect1 = new ShaderPass( DotScreenShader );
// effect1.uniforms[ 'scale' ].value = 5;
// composer.addPass( effect1 );
const glitchPass = new GlitchPass();
composer.addPass( glitchPass );

const effect2 = new ShaderPass( RGBShiftShader );
effect2.uniforms[ 'amount' ].value = 0.0015;
composer.addPass( effect2 );

const outputPass = new OutputPass();
composer.addPass( outputPass );


// Position the camera for an isometric view
camera.position.set(-400, 400, 400); // Adjust these values for your desired isometric angle
camera.lookAt(0, 0, 0);

// Adjust the zoom or scale as needed
camera.zoom = 2.0;

//var camera = new THREE.OrthographicCamera(WIDTH / -2, WIDTH / 2, WIDTH / 3, 2000);
//const helper = new THREE.CameraHelper(camera);
//scene.add(helper);
// var camera = new THREE.PerspectiveCamera(50, WIDTH / HEIGHT, .1, 2000);
// const helper = new THREE.CameraHelper(camera);
// scene.add(helper);

// Position the camera
//camera.position.set(0, 0, 2000);
// let radius = 900;
// let angle = -5;
// camera.position.set(0, 700, radius * Math.sin(angle));

// Set the camera's initial position
//camera.position.set(radius * Math.cos(angle), 10, radius * Math.sin(angle));

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

// const light = new THREE.PointLight( 0xffffff, 5.1, 100, 0.5 );
// light.position.set( 0, 0, 0 );
// scene.add( light );

class Wall { 
    constructor (pos_z) {
        this.geometry = new THREE.BoxGeometry(WIDTH, 10, 5);
        this.material = new THREE.MeshToonMaterial( { color: 0xFFFFFF});
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        this.mesh.position.set(0, 0, pos_z);
        this.mesh.receiveShadow = true;
        this.boundingBox = new THREE.Box3(new THREE.Vector3(), new THREE.Vector3());
        this.boundingBox.setFromObject(this.mesh);
    }
    addToScene() {
        scene.add(this.mesh);
    }
}

class PlayingField {
    constructor() {
        this.planeGeometry = new THREE.PlaneGeometry(WIDTH, HEIGHT);
        this.shaderMaterial = new THREE.ShaderMaterial({
            vertexShader: vertexShader,
            fragmentShader: fragmentShader,
            transparent: true,
            depthWrite: false,
            uniforms: {
                iTime: { value: 0.0 },
                iResolution: { value: new THREE.Vector2(WIDTH, HEIGHT) },
                xRand: { value: randomX },
                yRand: { value: randomY },
                multiRand: { value: randomMultiplier }
            }
        });
        //this.planeMaterial = new THREE.MeshToonMaterial({ color: 0x606060 });
        this.planeMesh = new THREE.Mesh(this.planeGeometry, this.shaderMaterial);
        this.planeMesh.rotateX(degreesToRads(-90));
        this.planeMesh.position.set(0, -5, 0);
        this.lowerWall = new Wall(HEIGHT / 2);
        this.upperWall = new Wall(HEIGHT / -2);
    }
    addToScene() {
        scene.add(this.planeMesh);
        this.upperWall.addToScene()
        this.lowerWall.addToScene()
    }
}

class Paddle {
    constructor(position, paddleColor) {
        this.geometry = new THREE.BoxGeometry(PADDLE_THICKNESS, PADDLE_THICKNESS, PADDLE_WIDTH);
        this.material = new THREE.MeshToonMaterial({ color: paddleColor});
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        this.mesh.position.copy(position);
        this.mesh.receiveShadow = true;
        this.speed = PADDLE_SPEED;
        this.boundingBox = new THREE.Box3(new THREE.Vector3(), new THREE.Vector3());
        this.boundingBox.setFromObject(this.mesh);
    }
    addToScene()
    {
        scene.add(this.mesh);
    }
    moveUp()
    {
        this.mesh.position.z -= this.speed;
        this.boundingBox.setFromObject(this.mesh);
    }
    moveDown()
    {
        this.mesh.position.z += this.speed;
        this.boundingBox.setFromObject(this.mesh);
    }
    intersectsWall(wallBoundingBox)
    {
        return this.boundingBox.intersectsBox(wallBoundingBox);
    }
}

const degreesToRads = deg =>(deg * Math.PI) / 180.00;

class Ball {
    constructor(){
        this.geometry = new THREE.SphereGeometry(BALL_SIZE);
        this.material = new THREE.MeshToonMaterial( {color: 0xffffff });
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        this.mesh.position.set(0, 0, 0);
        this.direction = 0;
        // console.log(this.direction);
        this.speed = BALL_SPEED;
        this.boundingSphere = new THREE.Sphere(this.mesh.position, BALL_SIZE);
    }
    update() {
        let radians = degreesToRads(this.direction);
        this.mesh.position.x = this.mesh.position.x + Math.cos(radians) * this.speed;
        this.mesh.position.z = this.mesh.position.z + Math.sin(radians) * this.speed;
    }
    hitsWall(wallBoundingBox) {
        return this.boundingSphere.intersectsBox(wallBoundingBox);
    }
    bounceFromPaddle(paddlePos) {
        //this.direction = (360 - this.direction) % 360;
        // console.log(this.direction);
        let hitPosNormalized = (paddlePos.z - this.mesh.position.z) / (PADDLE_WIDTH / 2);
        // console.log("Paddle pos: " + paddlePos.x + " " + paddlePos.z + ", ball pos: " + this.mesh.position.x + " " + this.mesh.position.z)
        // console.log("hitPosNormalized: " + hitPosNormalized);
        if (hitPosNormalized >= 1.0) {
            hitPosNormalized = .9;}
        else if (hitPosNormalized <= -1.0) {
            hitPosNormalized = -.9;
        }
        // console.log("hitPosNormalized: " + hitPosNormalized);

        let directionChange = hitPosNormalized * 85;
        if (paddlePos.x < 0)
            directionChange *= -1;
        // console.log("directionChange: " + directionChange + " degrees")
        this.direction = (180 - this.direction + directionChange) % 360;
        // console.log("new direction: " + this.direction + " degrees")
        this.speed += 0.02 + Math.abs(hitPosNormalized); 
    }
    bounceFromWall() {
        this.direction = (360 - this.direction) % 360; // Reflect the direction
                // console.log(this.direction);

    }
    addToScene(){
        scene.add(this.mesh);
    }
}

var playingField = new PlayingField();
//var wall1 = new Wall(0);
var leftPaddle = new Paddle(LEFT_PADDLE_START, 0x00ff00);
var rightPaddle = new Paddle(RIGHT_PADDLE_START, 0xff0000);
var ball = new Ball();
var geo = new THREE.BoxGeometry(50, 50, 50);
var mat = new THREE.MeshToonMaterial({ color: 0xFFAAAA});
var mesh = new THREE.Mesh(geo, mat);
mesh.position.set(0,0,0);

//scene.add(mesh);
//wall1.addToScene();
leftPaddle.addToScene();
rightPaddle.addToScene();
ball.addToScene();
playingField.addToScene();

// Variables to hold keyboard state
var keys = {};
document.addEventListener('keydown', function(event) {
    keys[event.key] = true;
});
document.addEventListener('keyup', function(event) {
    keys[event.key] = false;
});

// Update function to move cubes based on keyboard input
function update() {
    if ((keys['w'] || keys['W']) && !leftPaddle.intersectsWall(playingField.upperWall.boundingBox)) { // Q key
        leftPaddle.moveUp();
    }
    if ((keys['s'] || keys['S']) && !leftPaddle.intersectsWall(playingField.lowerWall.boundingBox)) { // A key
        leftPaddle.moveDown();
    }
    if (keys['ArrowUp'] && !rightPaddle.intersectsWall(playingField.upperWall.boundingBox)) { // Up arrow key
        rightPaddle.moveUp();
    }
    if (keys['ArrowDown'] && !rightPaddle.intersectsWall(playingField.lowerWall.boundingBox)) { // Down arrow key
        rightPaddle.moveDown();
    }
}

function checkCollision() {
    if (ball.boundingSphere.intersectsBox(leftPaddle.boundingBox)) {
        ball.bounceFromPaddle(leftPaddle.mesh.position);
        effect2.uniforms[ 'amount' ].value = 0.059;
        return true;
    }
    else if (ball.boundingSphere.intersectsBox(rightPaddle.boundingBox)) {
        ball.bounceFromPaddle(rightPaddle.mesh.position);
        effect2.uniforms[ 'amount' ].value = -0.059;
        return true;
    }
    else if (ball.hitsWall(playingField.lowerWall.boundingBox) || ball.hitsWall(playingField.upperWall.boundingBox)) {
        ball.bounceFromWall();
        return true;
    }
    else
        return false;
}

var counter = 0;
function animate() {
    playingField.shaderMaterial.uniforms.iTime.value = performance.now() / 1000;
//    playingField.shaderMaterial.uniforms.ballSpeed.value = ball.speed;
    requestAnimationFrame(animate);
    update();
    ball.update();
    if (checkCollision() === false)
    {
        if (counter % 77 === 0) {
            effect2.uniforms[ 'amount' ].value = 0.0055;
            // console.log("Counter % 77: " + counter);
        }
        else if (counter % 101 === 0) {
             effect2.uniforms[ 'amount' ].value = 0.019;
            //  console.log("Counter % 101: " + counter);
            }
        else {
           effect2.uniforms[ 'amount' ].value = 0.0015;
        }
    }
    counter++;
    camera.lookAt(0,0,0);
    composer.render();
}
animate();