import {
  scene,
  getControls,
  renderer,
  camera,
  addResize,
  resize,
} from "./modules/renderer.js";
import { Group } from "./third_party/three.module.js";
import {
  mesh,
  mesh2,
  simulation,
  step,
  randomizeColors,
  interpolate,
} from "./wisp.js";
import { Post } from "./post.js";
import { randomInRange, mod, clamp, parabola } from "./modules/Maf.js";
// import { capture } from "./modules/capture.js";

const group = new Group();
mesh.scale.setScalar(0.9);
group.add(mesh);
group.add(mesh2);
scene.add(group);

const post = new Post(renderer);

renderer.shadowMap.enabled = true;

camera.position.set(5, 5, 5);
camera.lookAt(scene.position);

const controls = getControls();
controls.minDistance = 5;
controls.maxDistance = 5;
controls.enablePan = false;
controls.enableZoom = false;
controls.enableRotate = false;

function init() {
  render();
}

let frames = 0;
let invalidate = false;

let time = 0;
let prevTime = performance.now();

// Mouse tracking for orbit controls
let mouseX = 0;
let mouseY = 0;
let targetRotationX = 0;
let targetRotationY = 0;

window.addEventListener('mousemove', (event) => {
  // Normalize mouse position to -1 to 1
  mouseX = (event.clientX / window.innerWidth) * 2 - 1;
  mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
});

function render() {
  const t = performance.now();
  const dt = t - prevTime;
  prevTime = t;

  if (running || invalidate) {
    if (!invalidate) {
      time += dt * 0.1; // Slow down time by 90%

      // Mouse-based rotation
      targetRotationX = mouseY * 0.3; // Even more subtle effect
      targetRotationY = -mouseX * 0.3;

      // Smooth lerp to target rotation
      group.rotation.x += (targetRotationX - group.rotation.x) * 0.03;
      group.rotation.y += (targetRotationY - group.rotation.y) * 0.03;
    }
    step(renderer, time / 1000, dt / 16);

    mesh2.material.uniforms.positions.value = simulation.texture;
    interpolate(time, renderer);
    invalidate = false;
  }

  // renderer.render(scene, camera);

  post.render(scene, camera);

  // capture(renderer.domElement);

  // if (frames > 10 * 60 && window.capturer.capturing) {
  //   window.capturer.stop();
  //   window.capturer.save();
  // }
  // frames++;

  renderer.setAnimationLoop(render);
}

randomize();

function randomize() {
  randomizeColors();
  // Set background to pure black #1B1B1B
  renderer.setClearColor(0x1B1B1B, 1);
  // Fixed offset for consistent particle positioning
  const offset = 500;
  mesh.material.uniforms.offset.value = offset;
  simulation.shader.uniforms.offset.value = offset;
  invalidate = true;
}

function goFullscreen() {
  if (renderer.domElement.webkitRequestFullscreen) {
    renderer.domElement.webkitRequestFullscreen();
  } else {
    renderer.domElement.requestFullscreen();
  }
}

let running = true;

window.addEventListener("keydown", (e) => {
  if (e.code === "Space") {
    running = !running;
  }
  if (e.code === "KeyF") {
    goFullscreen();
  }
});

function myResize(w, h, dPR) {
  post.setSize(w * dPR, h * dPR);
}
addResize(myResize);

resize();
init();

// window.start = () => {
//   frames = 0;
//   window.capturer.start();
// };
