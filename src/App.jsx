import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './App.css';
import Loading from './components/Loading';
import GlassSearchBar from './components/GlassSearchBar';
import DecryptedText from './components/DecryptedText';
import Dither from './components/Dither';
import LogoLoop from './components/LogoLoop';
import DevpostCard from './components/DevpostCard';
import Orchestration from './components/Orchestration';
import { TbBrandThreejs } from 'react-icons/tb';
import { FaReact, FaPython } from 'react-icons/fa';
import { RiClaudeFill, RiGeminiFill } from 'react-icons/ri';
import { SiTypescript, SiLangchain } from 'react-icons/si';
import livekitLogo from './assets/livekit-text.svg';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isZooming, setIsZooming] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);
  const [currentPage, setCurrentPage] = useState('landing');
  const wispIframeRef = useRef(null);

  // Logo Loop data
  const logos = [
    { node: <TbBrandThreejs style={{ color: 'white' }} />, title: 'Three.js' },
    { node: <FaReact style={{ color: 'white' }} />, title: 'React' },
    { node: <RiClaudeFill style={{ color: 'white' }} />, title: 'Claude' },
    { node: <SiTypescript style={{ color: 'white' }} />, title: 'TypeScript' },
    { node: <FaPython style={{ color: 'white' }} />, title: 'Python' },
    { node: <SiLangchain style={{ color: 'white' }} />, title: 'LangChain' },
    { node: <RiGeminiFill style={{ color: 'white' }} />, title: 'Gemini' },
    { src: 'https://raw.githubusercontent.com/letta-ai/letta/main/assets/Letta-logo-RGB_GreyonTransparent_cropped_small.png', alt: 'Letta', title: 'Letta' },
    { node: <img src={livekitLogo} alt="LiveKit" style={{ height: '24px', width: 'auto', filter: 'brightness(0) invert(1)' }} />, title: 'LiveKit' },
  ];

  useEffect(() => {
    // Show loading screen for 1.5 seconds
    const loadingTimer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(loadingTimer);
  }, []);

  useEffect(() => {
    // Handle hash changes for routing
    const handleHashChange = () => {
      const hash = window.location.hash;
      if (hash.startsWith('#orchestration')) {
        setCurrentPage('orchestration');
      } else {
        setCurrentPage('landing');
      }
    };

    // Check initial hash on mount
    handleHashChange();

    // Listen for hash changes
    window.addEventListener('hashchange', handleHashChange);

    return () => {
      window.removeEventListener('hashchange', handleHashChange);
    };
  }, []);

  const handleSearchSubmit = (query) => {
    console.log('Starting zoom animation with query:', query);
    setIsZooming(true);

    // Send zoom message to wisp iframe
    if (wispIframeRef.current && wispIframeRef.current.contentWindow) {
      wispIframeRef.current.contentWindow.postMessage({ type: 'ZOOM_IN' }, '*');
    }

    // Start fade to black after 0.8 seconds to cover the deep zoom
    setTimeout(() => {
      setShowOverlay(true);
    }, 800);

    // Navigate after animation completes (0.8s delay + 1.5s fade = 2.3 total)
    setTimeout(() => {
      window.location.hash = `#orchestration?q=${encodeURIComponent(query)}`;
    }, 2300);
  };

  return (
    <div className="app-container">
      {/* Render Orchestration page if on #orchestration route */}
      {currentPage === 'orchestration' ? (
        <Orchestration />
      ) : (
        <>
          <AnimatePresence>
            {isLoading && <Loading />}
          </AnimatePresence>

          {/* Background Layer: Wisp Animation */}
          <motion.div
            className="wisp-background"
            initial={{ opacity: 0 }}
            animate={{ opacity: isLoading ? 0 : 1 }}
            transition={{ duration: 1, delay: 0.3 }}
          >
            <iframe
              ref={wispIframeRef}
              src="/wisp/index.html"
              style={{
                width: '100%',
                height: '100%',
                border: 'none',
                display: 'block',
                margin: 0,
                padding: 0
              }}
              title="Wisp Animation"
            />
          </motion.div>

      {/* Overlay for zoom transition */}
      <AnimatePresence>
        {showOverlay && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5 }}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              backgroundColor: '#000000',
              zIndex: 10,
              pointerEvents: 'none'
            }}
          />
        )}
      </AnimatePresence>

      {/* Side Cards */}
      {!isLoading && (
        <>
          <motion.div
            className="side-card side-card-left"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: isZooming ? 0 : 1, x: isZooming ? -50 : 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <div className="dither-wrapper dither-wrapper-left">
              <Dither
                waveColor={[0.7, 0.4, 0.5]}
                disableAnimation={false}
                enableMouseInteraction={false}
                colorNum={6}
                waveAmplitude={0.3}
                waveFrequency={5}
                waveSpeed={-0.04}
                pixelSize={4}
                mouseRadius={0.3}
              />
            </div>
          </motion.div>
          <motion.div
            className="side-card side-card-right"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: isZooming ? 0 : 1, x: isZooming ? 50 : 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <div className="dither-wrapper dither-wrapper-right">
              <Dither
                waveColor={[0.7, 0.4, 0.5]}
                disableAnimation={false}
                enableMouseInteraction={false}
                colorNum={6}
                waveAmplitude={0.3}
                waveFrequency={5}
                waveSpeed={0.04}
                pixelSize={4}
                mouseRadius={0.3}
              />
            </div>
          </motion.div>
        </>
      )}

      {/* Foreground Layer: Title and Glass Search Bar */}
      {!isLoading && (
        <div className="content-container">
          <motion.div
            className="page-header"
            animate={{ opacity: isZooming ? 0 : 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <h1 className="title">
              <DecryptedText
                text="darwin"
                animateOn="view"
                sequential={true}
                speed={150}
              />
            </h1>
            <p className="subheader">evolve your agents.</p>
          </motion.div>
          <motion.div
            className="glass-wrapper"
            animate={{ opacity: isZooming ? 0 : 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <GlassSearchBar onSubmit={handleSearchSubmit} />
          </motion.div>
          <motion.div
            className="logo-loop-wrapper"
            animate={{ opacity: isZooming ? 0 : 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <p className="built-with-label">built with:</p>
            <LogoLoop
              logos={logos}
              speed={30}
              direction="left"
              logoHeight={32}
              gap={60}
              pauseOnHover={false}
              scaleOnHover={false}
              fadeOut={true}
              ariaLabel="AI Companies"
            />
          </motion.div>
        </div>
      )}

          {/* Devpost Card - Fixed to Bottom */}
          {!isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: isZooming ? 0 : 1 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            >
              <DevpostCard />
            </motion.div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
