import React, { useState, useRef } from 'react';
import { Mic, StopCircle, Volume2, Search, Calendar, HelpCircle } from 'lucide-react';
import './App.css';
const App: React.FC = () => {
  const [isListening, setIsListening] = useState(false);
  const [response, setResponse] = useState('');
  const [transcript, setTranscript] = useState('');
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);


const speakResponse = (text: string) => {
  if ('speechsynthesis' in window ) {
    const speech = new SpeechSynthesisUtterance(text);
  }else {
console.warn('text-to-speech is not supported in this browser.')
  }
}



  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = async () => {

        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        audioChunks.current = [];

const formData = new FormData();
formData.append('audio', audioBlob, 'recording.wav');

try{

const response = await fetch('/api/process-audio', {
       method: 'POST',
       body: formData,
}); 

if(!response.ok) {
    throw new Error('Failed to process audio')
}

const result = await response.json(); 
 setResponse(result.response)

const assistantResponse = result.response; // this shows the response on the ui
setResponse(assistantResponse);

speakResponse(assistantResponse); //make the response audible



} catch(error) {
console.error('Error sending audio to the backend', error);
setResponse('Failed to process audio')
}

        // TODO: Send audioBlob to backend (e.g., Flask)
        // const formData = new FormData();
        // formData.append('audio', audioBlob, 'recording.wav');
        // await fetch('/api/process-audio', { method: 'POST', body: formData });
        // Simulating response for demo purposes
       
      };
      mediaRecorder.current.start();
      setIsListening(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };
  const stopListening = () => {
    if (mediaRecorder.current && isListening) {
      mediaRecorder.current.stop();
      setIsListening(false);
    }
  };

  const handleVoiceCommand = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <div className="voice-assistant">
      <div className="assistant-container">
        <div className="assistant-header">
          <h1>Voice Assistant</h1>
        </div>
        <div className="assistant-body">
          <div className="response-area">
            {response ? (
              <>
                <Volume2 className="response-icon" />
                <p>{response}</p>
              </>
            ) : (
              <p>How can I help you today?</p>
            )}
          </div>
          <div className="transcript-area">
            <p>{transcript || "Your voice input will appear here..."}</p>
          </div>
          <div className="feature-list">
            <div className="feature">
              <Search /> Web Search
            </div>
            <div className="feature">
              <Calendar /> Set Reminders
            </div>
            <div className="feature">
              <HelpCircle /> Answer Questions
            </div>
          </div>
        </div>
        <div className="assistant-footer">
          <button 
            className={`voice-button ${isListening ? 'listening' : ''}`} 
            onClick={handleVoiceCommand}
            aria-label={isListening ? "Stop recording" : "Start recording"}
          >
            {isListening ? <StopCircle /> : <Mic />}
          </button>
          <p>{isListening ? 'Listening...' : 'Press to speak'}</p>
        </div>
      </div>
    </div>
  );
};

export default App;


