import { useState } from "react";
import { AudioFile } from "../lib/types";
import { WebSocketService } from "../services/websocket";

export const useFileUpload = (websocket: WebSocketService) => {
  const [files, setFiles] = useState<AudioFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadFile = async (file: File) => {
    try {
      setIsUploading(true);
      setError(null);

      // Create a new FileReader
      const reader = new FileReader();

      reader.onload = async (e) => {
        const arrayBuffer = e.target?.result as ArrayBuffer;

        // Create a new audio file entry
        const newFile: AudioFile = {
          id: crypto.randomUUID(),
          name: file.name,
          duration: 0, // Will be updated after processing
          status: "processing",
        };

        setFiles((prev) => [...prev, newFile]);

        // Send the file data through WebSocket
        websocket.send({
          type: "fileUpload",
          payload: {
            id: newFile.id,
            name: file.name,
            data: arrayBuffer,
          },
        });
      };

      reader.onerror = () => {
        setError("Error reading file");
        setIsUploading(false);
      };

      reader.readAsArrayBuffer(file);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error uploading file");
      setIsUploading(false);
    }
  };

  const removeFile = (fileId: string) => {
    setFiles((prev) => prev.filter((file) => file.id !== fileId));
  };

  return {
    files,
    isUploading,
    error,
    uploadFile,
    removeFile,
  };
};
