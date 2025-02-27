import { useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

const AudioStreamer: React.FC = () => {
  const [recording, setRecording] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<Socket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  useEffect(() => {
    try {
      socketRef.current = io("http://localhost:5000", {
        reconnectionAttempts: 3,
      });

      socketRef.current.on("connect_error", (err) => {
        setError(`WebSocket Error: ${err.message}`);
      });
    } catch (err) {
      setError("Failed to initialize WebSocket.");
    }

    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream: MediaStream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: "audio/webm",
      });

      mediaRecorderRef.current.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0 && socketRef.current?.connected) {
          socketRef.current.emit("audio_stream", event.data);
        } else {
          setError("WebSocket disconnected while recording.");
        }
      };

      mediaRecorderRef.current.onerror = (event: Event) => {
        setError(`MediaRecorder Error: ${(event as ErrorEvent).message}`);
      };

      mediaRecorderRef.current.start(250);
      setRecording(true);
    } catch (err: any) {
      setError(`Failed to start recording: ${err.message}`);
    }
  };

  const stopRecording = () => {
    try {
      mediaRecorderRef.current?.stop();
      setRecording(false);
      socketRef.current?.emit("audio_stream_end");
    } catch (err: any) {
      setError(`Failed to stop recording: ${err.message}`);
    }
  };

  return (
    <div>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <button onClick={recording ? stopRecording : startRecording}>
        {recording ? "Stop Recording" : "Start Recording"}
      </button>

    </div>
  );
};

export default AudioStreamer;
