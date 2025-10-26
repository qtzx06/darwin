import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './App.css';
import Loading from './components/Loading';
import GlassSearchBar from './components/GlassSearchBar';
import DecryptedText from './components/DecryptedText';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isZooming, setIsZooming] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);
  const wispIframeRef = useRef(null);

  useEffect(() => {
    // Show loading screen for 1.5 seconds
    const loadingTimer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(loadingTimer);
  }, []);

  const handleSearchSubmit = (query) => {
    console.log('Starting zoom animation with query:', query);
    setIsZooming(true);

    // Start fade to black
    setShowOverlay(true);

    // Send zoom message to wisp iframe
    if (wispIframeRef.current && wispIframeRef.current.contentWindow) {
      wispIframeRef.current.contentWindow.postMessage({ type: 'ZOOM_IN' }, '*');
    }

    // Navigate after animation completes (1.5 seconds for zoom + fade)
    setTimeout(() => {
      window.location.hash = `#orchestration?q=${encodeURIComponent(query)}`;
    }, 1500);
  };

  return (
    <div className="app-container">
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
            transition={{ duration: 1 }}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              backgroundColor: '#FFFFFF',
              zIndex: 10,
              pointerEvents: 'none'
            }}
          />
        )}
      </AnimatePresence>

      {/* Foreground Layer: Title and Glass Search Bar */}
      {!isLoading && (
        <div className="content-container">
          <div className="page-header">
            <h1 className="title">
              <DecryptedText
                text="darwin"
                animateOn="view"
                sequential={true}
                speed={150}
              />
            </h1>
          </div>
          <div className="glass-wrapper">
            <GlassSearchBar onSubmit={handleSearchSubmit} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
