import React from 'react'

interface AudioRecorderProps {
    onAudioCaptured?: (audioBlob: Blob) => void; 

}

const AudioRecorder = () => {
  return (
    <div>AudioRecorder</div>
  )
}

export default AudioRecorder