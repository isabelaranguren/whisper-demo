export interface Transcript {
  id: string;
  participant: string;
  content: string;
  timestamp: string;
  type: "transcript";
}

export interface Summary {
  id: string;
  content: string;
  timestamp: string;
  type: "summary";
}

export interface Participant {
  id: string;
  name: string;
  isActive: boolean;
}

export interface AudioFile {
  id: string;
  name: string;
  duration: number;
  status: "processing" | "completed" | "error";
  transcription?: string;
}

export type WebSocketMessage = {
  type:
    | "transcript"
    | "summary"
    | "participants"
    | "error"
    | "fileStatus"
    | "connected"
    | "disconnected";
  payload: any;
};
