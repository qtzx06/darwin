import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './App.css';
import Loading from './components/Loading';

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
    <div style={{
      width: '100%',
      height: '100%',
      margin: 0,
      padding: 0,
      overflow: 'hidden',
      backgroundColor: '#1B1B1B'
    }}>
      <AnimatePresence>
        {isLoading && <Loading />}
      </AnimatePresence>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: isLoading ? 0 : 1 }}
        transition={{ duration: 1, delay: 0.3 }}
        style={{
          width: '100%',
          height: '100%'
        }}
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
    </div>
  );
}

export default App;
