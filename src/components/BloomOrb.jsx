import { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { SimplexNoise } from 'three/examples/jsm/math/SimplexNoise.js';

const BloomOrb = () => {
  const mountRef = useRef(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const currentMount = mountRef.current;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      45,
      currentMount.clientWidth / currentMount.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 0, 15);
    camera.lookAt(scene.position);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
    currentMount.appendChild(renderer.domElement);

    const group = new THREE.Group();
    scene.add(group);

    // Create sphere geometry
    const radius = 2;
    const geometry = new THREE.SphereGeometry(radius, 64, 64);

    // Store original positions for distortion
    const positions = geometry.getAttribute('position');
    geometry.userData.originalPositions = new Float32Array(positions.array);

    const shaderMaterial = new THREE.ShaderMaterial({
      uniforms: {
        rimPower: { value: 2.0 },
        rimIntensity: { value: 1.2 },
      },
      vertexShader: `
        varying vec3 vNormal;
        varying vec3 vViewPosition;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
          vViewPosition = -mvPosition.xyz;
          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        varying vec3 vNormal;
        varying vec3 vViewPosition;
        uniform float rimPower;
        uniform float rimIntensity;
        void main() {
          vec3 viewDir = normalize(vViewPosition);
          float fresnel = 1.0 - dot(viewDir, vNormal);
          fresnel = pow(fresnel, rimPower) * rimIntensity;
          float gray = fresnel * 0.6;
          gl_FragColor = vec4(gray, gray, gray, 1.0);
        }
      `,
      transparent: true,
      depthWrite: false,
    });

    const sphere = new THREE.Mesh(geometry, shaderMaterial);
    sphere.userData.isBloom = true;
    group.add(sphere);

    const noise = new SimplexNoise();
    let animationFrameId;

    const modulate = (val, minVal, maxVal, outMin, outMax) => {
      const fr = (val - minVal) / (maxVal - minVal);
      const delta = outMax - outMin;
      return outMin + fr * delta;
    };

    const distortMesh = (mesh, bassFr, treFr) => {
      const vertices = mesh.geometry.getAttribute('position');
      const originalPositions = mesh.geometry.userData.originalPositions;
      const time = window.performance.now();

      const rf1 = 0.00001, rf2 = 0.00008;
      const amp1 = 2.5, amp2 = 0.7;

      for (let i = 0; i < vertices.count; i++) {
        const origX = originalPositions[i * 3];
        const origY = originalPositions[i * 3 + 1];
        const origZ = originalPositions[i * 3 + 2];

        const origLength = Math.sqrt(origX * origX + origY * origY + origZ * origZ);
        if (origLength === 0) continue;

        const nx = origX / origLength;
        const ny = origY / origLength;
        const nz = origZ / origLength;

        const noiseVal1 = noise.noise3d(
          nx + time * rf1 * 7,
          ny + time * rf1 * 8,
          nz + time * rf1 * 9
        );
        const noiseVal2 = noise.noise3d(
          nx + time * rf2 * 5,
          ny + time * rf2 * 6,
          nz + time * rf2 * 7
        );

        // Bloom multiplier - creates pulsing effect
        const bloomMultiplier = mesh.userData.isBloom
          ? 1.0 + Math.sin(time * 0.001 + origLength * 0.5) * 0.25
          : 1.0;

        const distortion = (noiseVal1 * amp1 * treFr + noiseVal2 * amp2 * treFr) * bloomMultiplier;
        const distance = origLength + bassFr * 0.5 + distortion;

        vertices.setXYZ(i, nx * distance, ny * distance, nz * distance);
      }
      vertices.needsUpdate = true;
    };

    const render = () => {
      // Idle animation with sine waves
      const time = performance.now() * 0.001;
      const bassFr = modulate(Math.sin(time * 0.5) * 0.5 + 0.5, 0, 1, 0.2, 0.5);
      const treFr = modulate(Math.sin(time * 0.8) * 0.5 + 0.5, 0, 1, 0.2, 0.5);

      distortMesh(sphere, bassFr * 0.8, treFr * 0.8);
      group.rotation.x += 0.001;
      group.rotation.y += 0.0015;

      renderer.render(scene, camera);
      animationFrameId = requestAnimationFrame(render);
    };

    const onWindowResize = () => {
      if (currentMount) {
        const width = currentMount.clientWidth;
        const height = currentMount.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
      }
    };

    window.addEventListener('resize', onWindowResize, false);
    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', onWindowResize);
      if (currentMount && renderer.domElement) {
        currentMount.removeChild(renderer.domElement);
      }
      scene.remove(group);
      geometry.dispose();
      shaderMaterial.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={mountRef}
      style={{
        width: '100%',
        height: '100%',
        position: 'absolute',
        top: 0,
        left: 0,
        zIndex: 10,
      }}
    />
  );
};

export default BloomOrb;
