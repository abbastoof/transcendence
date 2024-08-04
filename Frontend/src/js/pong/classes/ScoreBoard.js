import * as THREE from 'three';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import fontJson from 'three/examples/fonts/droid/droid_sans_regular.typeface.json'; // Adjust path if necessary

class ScoreBoard {
    constructor(scene) {
        this.scene = scene;
        this.scores = null;
        this.font = new FontLoader().parse(fontJson);
    }

    createText(text, size) {
        const geometry = new TextGeometry(text, {
            font: this.font,
            size: size,
            height: 1,
            curveSegments: 12,
        });
        const material = new THREE.MeshPhongMaterial({ color: 0xFFFFFF });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(0, 0, -400); // Adjust position as needed
        return mesh;
    }

    createScoreBoard(text) {
        this.scores = this.createText(text, 30);
        this.scene.add(this.scores);
    }

    updateScores(player1Score, player2Score) {
        this.clearScores();
        const text = `Player 1: ${player1Score}\nPlayer 2: ${player2Score}`;
        this.createScoreBoard(text);
    }

    showGoalText() {
        this.clearScores();
        this.scores = this.createText('GOAL!!!', 50);
        this.scene.add(this.scores);
    }

    clearScores() {
        if (this.scores) {
            this.scene.remove(this.scores);
            this.scores.geometry.dispose();
            this.scores.material.dispose();
            this.scores = null;
        }
    }
}

export default ScoreBoard;
