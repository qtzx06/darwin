import { useRef, useCallback } from 'react';
import { playAudioThroughAnalyser } from '../utils/audioContext';

/**
 * Hook for playing commentator audio through the shared audio context
 */
export function useCommentatorAudio() {
  const currentAudioRef = useRef(null);

  /**
   * Play audio from a blob
   */
  const playAudio = useCallback(async (audioBlob) => {
    try {
      console.log('🎵 [Hook] playAudio called');
      console.log('   Blob:', audioBlob);
      console.log('   Blob size:', audioBlob?.size);
      console.log('   Blob type:', audioBlob?.type);

      if (!audioBlob) {
        console.error('❌ [Hook] No audio blob provided!');
        return;
      }

      // Stop any currently playing audio
      if (currentAudioRef.current) {
        console.log('🎵 [Hook] Stopping previous audio');
        currentAudioRef.current.pause();
        currentAudioRef.current = null;
      }

      console.log('🎵 [Hook] Calling playAudioThroughAnalyser...');
      // Play through shared analyser
      const audio = await playAudioThroughAnalyser(audioBlob);
      currentAudioRef.current = audio;
      console.log('✅ [Hook] Audio playback started successfully');

    } catch (error) {
      console.error('❌ [Hook] Error playing audio:', error);
      console.error('   Error message:', error?.message);
      console.error('   Error stack:', error?.stack);
    }
  }, []);

  /**
   * Stop currently playing audio
   */
  const stopAudio = useCallback(() => {
    if (currentAudioRef.current) {
      console.log('🎵 [Hook] Stopping audio');
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
    }
  }, []);

  return {
    playAudio,
    stopAudio,
  };
}
