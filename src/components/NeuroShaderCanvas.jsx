import { useRef, useEffect } from 'react';

const NeuroShaderCanvas = () => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const parent = canvas.parentElement;
        if (!parent) return;

        // Get WebGL context
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (!gl) {
            console.error('WebGL not supported');
            return;
        }

        // Vertex shader
        const vertexShaderSource = `
            precision mediump float;
            attribute vec2 a_position;
            varying vec2 vUv;

            void main() {
                vUv = 0.5 * (a_position + 1.0);
                gl_Position = vec4(a_position, 0.0, 1.0);
            }
        `;

        // Fragment shader
        const fragmentShaderSource = `
            precision mediump float;
            varying vec2 vUv;
            uniform float u_time;
            uniform float u_ratio;
            uniform vec2 u_pointer_position;

            vec2 rotate(vec2 uv, float th) {
                return mat2(cos(th), sin(th), -sin(th), cos(th)) * uv;
            }

            float neuro_shape(vec2 uv, float t, float p) {
                vec2 sine_acc = vec2(0.0);
                vec2 res = vec2(0.0);
                float scale = 8.0;

                for (int j = 0; j < 15; j++) {
                    uv = rotate(uv, 1.0);
                    sine_acc = rotate(sine_acc, 1.0);
                    vec2 layer = uv * scale + float(j) + sine_acc - t;
                    sine_acc += sin(layer);
                    res += (0.5 + 0.5 * cos(layer)) / scale;
                    scale *= (1.2 - 0.07 * p);
                }
                return res.x + res.y;
            }

            void main() {
                vec2 uv = 0.5 * vUv;
                uv.x *= u_ratio;

                vec2 pointer = vUv - u_pointer_position;
                pointer.x *= u_ratio;
                float p = clamp(length(pointer), 0.0, 1.0);
                p = 0.5 * pow(1.0 - p, 2.0);

                float t = 0.001 * u_time;

                float noise = neuro_shape(uv, t, p);
                noise = 1.2 * pow(noise, 3.0);
                noise += pow(noise, 10.0);
                noise = max(0.0, noise - 0.5);
                noise *= (1.0 - length(vUv - 0.5));

                vec3 color = vec3(noise);

                gl_FragColor = vec4(color, noise);
            }
        `;

        // Compile shader
        function compileShader(source, type) {
            const shader = gl.createShader(type);
            gl.shaderSource(shader, source);
            gl.compileShader(shader);

            if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                console.error('Shader compile error:', gl.getShaderInfoLog(shader));
                gl.deleteShader(shader);
                return null;
            }
            return shader;
        }

        // Create program
        const vertexShader = compileShader(vertexShaderSource, gl.VERTEX_SHADER);
        const fragmentShader = compileShader(fragmentShaderSource, gl.FRAGMENT_SHADER);

        if (!vertexShader || !fragmentShader) return;

        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);

        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            console.error('Program link error:', gl.getProgramInfoLog(program));
            return;
        }

        gl.useProgram(program);

        // Set up geometry
        const vertices = new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]);
        const buffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
        gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

        const positionLocation = gl.getAttribLocation(program, 'a_position');
        gl.enableVertexAttribArray(positionLocation);
        gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

        // Get uniform locations
        const timeLocation = gl.getUniformLocation(program, 'u_time');
        const ratioLocation = gl.getUniformLocation(program, 'u_ratio');
        const pointerLocation = gl.getUniformLocation(program, 'u_pointer_position');

        // Mouse tracking
        const pointer = { x: 0.5, y: 0.5, tX: 0.5, tY: 0.5 };

        const handlePointerMove = (e) => {
            const rect = canvas.getBoundingClientRect();
            pointer.tX = (e.clientX - rect.left) / rect.width;
            pointer.tY = 1.0 - (e.clientY - rect.top) / rect.height;
        };

        canvas.addEventListener('pointermove', handlePointerMove);

        // Resize
        const resize = () => {
            const dpr = Math.min(window.devicePixelRatio, 2);
            canvas.width = parent.clientWidth * dpr;
            canvas.height = parent.clientHeight * dpr;
            gl.viewport(0, 0, canvas.width, canvas.height);
            gl.uniform1f(ratioLocation, canvas.width / canvas.height);
        };

        window.addEventListener('resize', resize);
        resize();

        // Render loop
        let animationId;
        const render = () => {
            pointer.x += (pointer.tX - pointer.x) * 0.5;
            pointer.y += (pointer.tY - pointer.y) * 0.5;

            gl.uniform1f(timeLocation, performance.now());
            gl.uniform2f(pointerLocation, pointer.x, pointer.y);

            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            animationId = requestAnimationFrame(render);
        };

        render();

        // Cleanup
        return () => {
            cancelAnimationFrame(animationId);
            canvas.removeEventListener('pointermove', handlePointerMove);
            window.removeEventListener('resize', resize);
            gl.deleteProgram(program);
            gl.deleteShader(vertexShader);
            gl.deleteShader(fragmentShader);
            gl.deleteBuffer(buffer);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                zIndex: 1,
            }}
        />
    );
};

export default NeuroShaderCanvas;
