# LiveKit Audio Simplification

## 🎯 Problem

The React frontend (`Orchestration.jsx`) was trying to use **LiveKit WebRTC** for audio streaming, which caused endless issues:
- Participant identity conflicts (frontend + backend both connecting as "commentator")
- DataChannel errors
- Complex `AudioContext` + `MediaStream` setup
- Audio never actually playing despite successful backend TTS generation

Meanwhile, `simple_frontend.html` worked perfectly using a **simple HTTP TTS approach**.

## ✅ Solution

**Ditched LiveKit WebRTC entirely** and adopted the same simple HTTP approach from `simple_frontend.html`.

### Changes Made

#### 1. **Orchestration.jsx** - Removed LiveKit WebRTC

**Before:**
```jsx
import { useLiveKit } from '../hooks/useLiveKit';
import { useCommentatorAudio } from '../hooks/useCommentatorAudio';

const { audioStream, isConnected } = useLiveKit(roomUrl, roomToken);
const { playAudio, stopAudio } = useCommentatorAudio();
```

**After:**
```jsx
// Simple audio playback (same as simple_frontend.html)
const [currentAudio, setCurrentAudio] = useState(null);

const playCommentatorAudio = async (text, voiceId = 'gnPxliFHTp6OK6tcoA6i') => {
  const response = await fetch('http://localhost:5003/api/livekit/speak-text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, voice_id: voiceId })
  });

  if (response.ok) {
    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    setCurrentAudio(audio);
    await audio.play();
  }
};
```

#### 2. **Commentator.jsx** - Simplified

**Before:**
- Tried to connect LiveKit `audioStream` to `AudioContext`
- Complex `MediaStreamSource` setup
- Required `audioStream` prop

**After:**
- Just creates a simple `AudioContext` for orb visualization
- No LiveKit stream connection needed
- No props required

#### 3. **Backend** (`tts_publisher.py`)

**Note:** Backend still uses LiveKit for publishing audio, but with a **different identity** ("tts-bot" instead of "commentator") to avoid conflicts. However, the React frontend **no longer listens** to LiveKit tracks - it just gets audio via HTTP.

## 🎉 Benefits

1. **Actually works** ✅
2. **Much simpler** - No WebRTC complexity
3. **Same as proven HTML approach** - Consistency
4. **No identity conflicts** - Frontend doesn't connect to LiveKit room
5. **Direct audio playback** - HTML5 Audio API is reliable

## 🧪 Testing

Click the **"🎤 Test Audio"** button in Orchestration page. You should hear:
> "Welcome to the AI coding battle arena! Let's go! 🔥"

If you hear audio, it's working! 🎊

## 📝 Files Changed

- `/src/components/Orchestration.jsx` - Removed LiveKit hooks, added simple HTTP TTS
- `/src/components/Commentator.jsx` - Removed audioStream dependency
- `/ai-agents/src/livekit/tts_publisher.py` - Uses "tts-bot" identity (already done)

## 🎨 Orb Visualization (IMPLEMENTED!)

The orb now reacts to audio! Here's how it works:

1. **Orchestration.jsx** creates an `AudioContext` and `AnalyserNode`
2. When playing audio, we create a `MediaElementSource` from the HTML5 Audio
3. Connect: `Audio → MediaElementSource → AnalyserNode → Destination`
4. Pass the `analyserRef` to `<Commentator analyser={analyserRef.current} />`
5. The orb visualizes the audio frequencies in real-time! 🎵

**Result:** Simple HTTP TTS playback + Beautiful reactive orb visualization! 🎉

