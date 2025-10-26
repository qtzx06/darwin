import { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { SimplexNoise } from 'three/examples/jsm/math/SimplexNoise.js';

const AgentOrb = () => {
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
    camera.position.set(0, 0, 25);
    camera.lookAt(scene.position);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
    currentMount.appendChild(renderer.domElement);

    const group = new THREE.Group();
    scene.add(group);

    // Create 6-point shuriken geometry
    const createShurikenGeometry = () => {
      const shape = new THREE.Shape();
      const numPoints = 6;
      const innerRadius = 1.0;
      const outerRadius = 3.0;

      for (let i = 0; i < numPoints; i++) {
        const angle = (i / numPoints) * Math.PI * 2;
        const nextAngle = ((i + 1) / numPoints) * Math.PI * 2;
        const midAngle = (angle + nextAngle) / 2;

        if (i === 0) {
          shape.moveTo(Math.cos(angle) * innerRadius, Math.sin(angle) * innerRadius);
        }

        shape.lineTo(Math.cos(midAngle) * outerRadius, Math.sin(midAngle) * outerRadius);
        shape.lineTo(Math.cos(nextAngle) * innerRadius, Math.sin(nextAngle) * innerRadius);
      }

      const extrudeSettings = {
        depth: 0.5,
        bevelEnabled: true,
        bevelThickness: 0.2,
        bevelSize: 0.15,
        bevelSegments: 5
      };

      const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
      geometry.center();

      // Store original positions for distortion
      const positions = geometry.getAttribute('position');
      geometry.userData.originalPositions = new Float32Array(positions.array);

      return geometry;
    };

    const geometry = createShurikenGeometry();

    const shaderMaterial = new THREE.ShaderMaterial({
      uniforms: {
        rimPower: { value: 1.5 },
        rimIntensity: { value: 2.5 },
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
          float gray = fresnel * 1.5;
          gl_FragColor = vec4(gray, gray, gray, 1.0);
        }
      `,
      transparent: true,
      depthWrite: false,
    });

    const mesh = new THREE.Mesh(geometry, shaderMaterial);
    group.add(mesh);

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
      const amp1 = 4, amp2 = 1.0;

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

        const distortion = noiseVal1 * amp1 * treFr + noiseVal2 * amp2 * treFr;
        const distance = origLength + bassFr + distortion;

        vertices.setXYZ(i, nx * distance, ny * distance, nz * distance);
      }
      vertices.needsUpdate = true;
      mesh.geometry.computeVertexNormals();
    };

    const render = () => {
      // Idle animation with sine waves
      const time = performance.now() * 0.001;
      const bassFr = modulate(Math.sin(time * 0.5) * 0.5 + 0.5, 0, 1, 0.3, 0.8);
      const treFr = modulate(Math.sin(time * 0.8) * 0.5 + 0.5, 0, 1, 0.3, 0.8);

      distortMesh(mesh, bassFr, treFr);
      group.rotation.z += 0.005;

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

export default AgentOrb;
