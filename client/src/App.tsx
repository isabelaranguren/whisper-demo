import React, { useState, useEffect } from "react";
import "./App.css";
import ModelSelector from "./components/ModelSelector";

function App() {

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="container mx-auto max-w-4xl">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-800">
            Meeting Transcription System
          </h1>
          <ModelSelector onModelChange={(model, modelInfo) => { /* handle model change */ }} />
          <p className="text-gray-600">Convert speech to text with Whisper</p>
        </header>
        <div className="text-center">
        </div>
      </div>
    </div>
  );
}

export default App;
