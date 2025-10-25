import { motion } from 'framer-motion';
import WebglNoise from './WebglNoise';

const Loading = () => {
  return (
    <motion.div
      className="loading-screen"
      initial={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8, delay: 0.1 }}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 50,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#1B1B1B'
      }}
    >
      <WebglNoise />
    </motion.div>
  );
};

export default Loading;
