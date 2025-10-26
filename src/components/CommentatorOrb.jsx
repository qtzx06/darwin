import { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { SimplexNoise } from 'three/examples/jsm/math/SimplexNoise.js';

const CommentatorOrb = ({ analyser, onSoundActiveChange }) => {
  const mountRef = useRef(null);
  const groupRef = useRef(null);
  const [hasStarted, setHasStarted] = useState(false);

  useEffect(() => {
    if (!mountRef.current) return;
    if (!analyser) return;

    const currentMount = mountRef.current;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      45,
      currentMount.clientWidth / currentMount.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 0, 100);
    camera.lookAt(scene.position);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(currentMount.clientWidth, currentMount.clientHeight);
    currentMount.appendChild(renderer.domElement);

    const group = new THREE.Group();
    groupRef.current = group;
    group.scale.set(0.8, 0.8, 0.8);
    scene.add(group);

    const geometry = new THREE.TorusKnotGeometry(8, 1.2, 256, 20);

    const shaderMaterial = new THREE.ShaderMaterial({
      uniforms: {
        rimPower: { value: 1.5 },
        rimIntensity: { value: 1.0 },
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
          float gray = fresnel;
          gl_FragColor = vec4(gray, gray, gray, 1.0);
        }
      `,
      transparent: true,
      depthWrite: false,
    });

    const mesh = new THREE.Mesh(geometry, shaderMaterial);
    group.add(mesh);

    analyser.fftSize = 512;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const noise = new SimplexNoise();
    let animationFrameId;
    let wasActive = false;

    const modulate = (val, minVal, maxVal, outMin, outMax) => {
      const fr = (val - minVal) / (maxVal - minVal);
      const delta = outMax - outMin;
      return outMin + fr * delta;
    };

    const distortMesh = (mesh, bassFr, treFr) => {
      const vertices = mesh.geometry.getAttribute('position');
      const radius = mesh.geometry.parameters.radius;
      const time = window.performance.now();

      const rf1 = 0.00001,
        rf2 = 0.00008,
        amp1 = 2,
        amp2 = 0.5;

      for (let i = 0; i < vertices.count; i++) {
        const vertex = new THREE.Vector3().fromBufferAttribute(vertices, i);
        vertex.normalize();

        const noiseVal1 = noise.noise3d(
          vertex.x + time * rf1 * 7,
          vertex.y + time * rf1 * 8,
          vertex.z + time * rf1 * 9
        );
        const noiseVal2 = noise.noise3d(
          vertex.x + time * rf2 * 5,
          vertex.y + time * rf2 * 6,
          vertex.z + time * rf2 * 7
        );

        const distortion = noiseVal1 * amp1 * treFr + noiseVal2 * amp2 * treFr;
        const distance = radius + bassFr + distortion;

        vertex.multiplyScalar(distance);
        vertices.setXYZ(i, vertex.x, vertex.y, vertex.z);
      }
      vertices.needsUpdate = true;
      mesh.geometry.computeVertexNormals();
    };

    const render = () => {
      analyser.getByteFrequencyData(dataArray);
      const averageFrequency = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
      const isActive = averageFrequency > 2;

      if (isActive !== wasActive) {
        if (onSoundActiveChange) onSoundActiveChange(isActive);
        wasActive = isActive;
      }

      if (isActive) {
        // Audio-reactive mode
        const lowerHalfArray = dataArray.slice(0, dataArray.length / 2 - 1);
        const upperHalfArray = dataArray.slice(dataArray.length / 2 - 1, dataArray.length - 1);
        const lowerMax = Math.max(...lowerHalfArray);
        const upperAvg = upperHalfArray.reduce((sum, a) => sum + a, 0) / upperHalfArray.length;
        const lowerMaxFr = lowerMax / lowerHalfArray.length;
        const upperAvgFr = upperAvg / upperHalfArray.length;

        distortMesh(mesh, modulate(Math.pow(lowerMaxFr, 0.8), 0, 1, 1, 4), modulate(upperAvgFr, 0, 1, 0.5, 2));
        group.rotation.y += 0.005;
      } else {
        // Idle animation
        const time = performance.now() * 0.001;
        const bassFr = modulate(Math.sin(time * 0.5) * 0.5 + 0.5, 0, 1, 0.3, 0.8);
        const treFr = modulate(Math.sin(time * 0.8) * 0.5 + 0.5, 0, 1, 0.2, 0.6);

        distortMesh(mesh, bassFr, treFr);
        group.rotation.y += 0.003;
      }

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
  }, [analyser, onSoundActiveChange]);

  // Effect for the expansion and initial rotation animation
  useEffect(() => {
    if (groupRef.current && !hasStarted) {
      setHasStarted(true);
      const group = groupRef.current;
      const targetScale = 1.5;
      const duration = 1200;
      const delay = 0;
      const startTime = performance.now() + delay;
      let animationFrameId;

      const initialRotationZ = Math.PI * 2;
      group.rotation.z = initialRotationZ;

      const animate = (currentTime) => {
        if (currentTime < startTime) {
          animationFrameId = requestAnimationFrame(animate);
          return;
        }

        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / duration, 1);
        const easeOutProgress = 1 - Math.pow(1 - progress, 4);

        const currentScale = 0.8 + (targetScale - 0.8) * easeOutProgress;
        group.scale.set(currentScale, currentScale, currentScale);

        const currentRotationZ = initialRotationZ * (1 - easeOutProgress);
        group.rotation.z = currentRotationZ;

        if (progress < 1) {
          animationFrameId = requestAnimationFrame(animate);
        } else {
          group.rotation.z = 0;
        }
      };

      animationFrameId = requestAnimationFrame(animate);

      return () => {
        cancelAnimationFrame(animationFrameId);
      };
    }
  }, [hasStarted]);

  return (
    <div
      ref={mountRef}
      style={{
        width: '100%',
        height: '100%',
        position: 'absolute',
        top: 0,
        left: 0,
        zIndex: 2,
      }}
    />
  );
};

export default CommentatorOrb;
