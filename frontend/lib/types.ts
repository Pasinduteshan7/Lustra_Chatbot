export type GenderPreference = "female" | "male" | "non-binary";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  message: string;
  gender_preference: GenderPreference;
  user_name?: string;
}

export interface ChatResponse {
  response: string;
  persona_name: string;
  retrieved_topics: string[];
  response_time_seconds: number;
}
