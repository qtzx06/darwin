import { useEffect, useRef } from 'react';

const SideParticles = ({ side = 'left' }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const particles = [];
    const particleCount = 200;

    // Resize canvas
    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    // Particle colors matching wisp
    const colors = [
      'rgba(221, 160, 221, 0.4)',
      'rgba(200, 162, 200, 0.35)',
      'rgba(177, 156, 217, 0.3)',
      'rgba(147, 112, 219, 0.25)',
      'rgba(255, 182, 193, 0.3)'
    ];

    class Particle {
      constructor() {
        this.reset();
      }

      reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.radius = Math.random() * 2 + 1;
        this.color = colors[Math.floor(Math.random() * colors.length)];
        this.life = Math.random() * 100 + 100;
        this.maxLife = this.life;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life--;

        // Fade out
        if (this.life <= 0) {
          this.reset();
        }

        // Wrap around
        if (this.x < 0) this.x = canvas.width;
        if (this.x > canvas.width) this.x = 0;
        if (this.y < 0) this.y = canvas.height;
        if (this.y > canvas.height) this.y = 0;
      }

      draw() {
        const opacity = this.life / this.maxLife;

        // Bloom effect - draw multiple layers with decreasing opacity
        const baseColor = this.color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (baseColor) {
          const r = baseColor[1];
          const g = baseColor[2];
          const b = baseColor[3];

          // Outer glow
          ctx.beginPath();
          ctx.arc(this.x, this.y, this.radius * 3, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${opacity * 0.15})`;
          ctx.fill();

          // Middle glow
          ctx.beginPath();
          ctx.arc(this.x, this.y, this.radius * 2, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${opacity * 0.4})`;
          ctx.fill();

          // Core
          ctx.beginPath();
          ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${opacity * 0.7})`;
          ctx.fill();
        }
      }
    }

    // Create particles
    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle());
    }

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach(particle => {
        particle.update();
        particle.draw();
      });

      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resize);
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
        pointerEvents: 'none'
      }}
    />
  );
};

export default SideParticles;
