/**
 * Shared audio context for the entire app
 * Prevents multiple AudioContext instances from being created
 */

let sharedAudioContext = null;
let sharedAnalyser = null;
let currentAudioSource = null; // Track current audio source to avoid multiple MediaElementSource

export function getAudioContext() {
  if (!sharedAudioContext) {
    sharedAudioContext = new (window.AudioContext || window.webkitAudioContext)();
    console.log('🎵 [Global] Created shared audio context');
  }
  return sharedAudioContext;
}

export function getAnalyser() {
  if (!sharedAnalyser) {
    const ctx = getAudioContext();
    sharedAnalyser = ctx.createAnalyser();
    sharedAnalyser.fftSize = 512;
    // Connect analyser to destination for playback
    sharedAnalyser.connect(ctx.destination);
    console.log('🎵 [Global] Created shared analyser');
  }
  return sharedAnalyser;
}

/**
 * Play audio through the shared audio context and analyser
 */
export async function playAudioThroughAnalyser(audioBlob) {
  const ctx = getAudioContext();
  const analyser = getAnalyser();

  try {
    console.log('🎵 [Global] Playing audio through analyser...');
    console.log('   Audio blob size:', audioBlob.size, 'bytes');
    console.log('   Audio blob type:', audioBlob.type);

    // Disconnect previous source if exists
    if (currentAudioSource) {
      console.log('🎵 [Global] Disconnecting previous audio source');
      currentAudioSource.disconnect();
      currentAudioSource = null;
    }

    // Resume context if suspended (autoplay policy)
    if (ctx.state === 'suspended') {
      console.log('🎵 [Global] Audio context suspended, resuming...');
      await ctx.resume();
      console.log('🎵 [Global] Audio context resumed, state:', ctx.state);
    }

    // Create audio element
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    
    console.log('🎵 [Global] Created Audio element');

    // Wait for audio to be loaded
    await new Promise((resolve, reject) => {
      audio.onloadedmetadata = () => {
        console.log('🎵 [Global] Audio metadata loaded, duration:', audio.duration);
        resolve();
      };
      audio.onerror = (e) => {
        console.error('❌ [Global] Audio load error:', e);
        reject(e);
      };
      audio.load();
    });

    // Create source and connect to analyser
    console.log('🎵 [Global] Creating MediaElementSource...');
    const source = ctx.createMediaElementSource(audio);
    currentAudioSource = source;
    
    source.connect(analyser);
    // Analyser is already connected to destination
    console.log('🎵 [Global] Connected source -> analyser -> destination');

    // Play audio
    console.log('🎵 [Global] Calling audio.play()...');
    await audio.play();
    console.log('🔊 [Global] Audio playing! Duration:', audio.duration, 'seconds');

    // Cleanup
    audio.onended = () => {
      console.log('🎵 [Global] Audio playback ended');
      URL.revokeObjectURL(audioUrl);
      if (currentAudioSource === source) {
        source.disconnect();
        currentAudioSource = null;
      }
    };

    audio.onerror = (e) => {
      console.error('❌ [Global] Audio playback error:', e);
      console.error('   Error details:', audio.error);
      URL.revokeObjectURL(audioUrl);
      if (currentAudioSource === source) {
        source.disconnect();
        currentAudioSource = null;
      }
    };

    return audio; // Return for potential control

  } catch (error) {
    console.error('❌ [Global] Error in playAudioThroughAnalyser:', error);
    console.error('   Error message:', error.message);
    console.error('   Error stack:', error.stack);
    throw error;
  }
}
