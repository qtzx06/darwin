import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './App.css';
import Loading from './components/Loading';
import GlassSearchBar from './components/GlassSearchBar';
import DecryptedText from './components/DecryptedText';

function App() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Show loading screen for 1.5 seconds
    const loadingTimer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(loadingTimer);
  }, []);

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
            <GlassSearchBar />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
