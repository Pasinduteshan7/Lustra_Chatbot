"use client";

import { useState, useRef, useEffect } from "react";
import { sendChatMessage } from "@/lib/api";
import type { ChatMessage, GenderPreference } from "@/lib/types";

const PERSONA_NAMES: Record<GenderPreference, string> = {
  female: "Luna",
  male: "Marcus",
  "non-binary": "Alex",
};

export default function Home() {
  const [started, setStarted] = useState(false);
  const [userName, setUserName] = useState("");
  const [gender, setGender] = useState<GenderPreference>("non-binary");

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function handleStart() {
    if (!userName.trim()) return;
    setStarted(true);
    setMessages([
      {
        role: "assistant",
        content: `Hi ${userName}! I'm ${PERSONA_NAMES[gender]}, your personalized beauty expert. What can I help you with today?`,
      },
    ]);
  }

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    setError(null);
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const res = await sendChatMessage({
        message: text,
        gender_preference: gender,
        user_name: userName,
      });
      setMessages((prev) => [...prev, { role: "assistant", content: res.response }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") handleSend();
  }

  if (!started) {
    return (
      <div className="app">
        <div className="header">
          <h1>Lustra</h1>
          <p>Your personalized beauty assistant</p>
        </div>
        <div className="setup">
          <div>
            <label>What&apos;s your name?</label>
            <input
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="Enter your name"
            />
          </div>
          <div>
            <label>How should I tailor advice?</label>
            <div className="gender-options" style={{ marginTop: 8 }}>
              {(["female", "male", "non-binary"] as GenderPreference[]).map((g) => (
                <button
                  key={g}
                  className={`gender-btn ${gender === g ? "selected" : ""}`}
                  onClick={() => setGender(g)}
                >
                  {g === "non-binary" ? "Non-binary" : g[0].toUpperCase() + g.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <button className="start-btn" onClick={handleStart} disabled={!userName.trim()}>
            Start chatting
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="header">
        <h1>{PERSONA_NAMES[gender]}</h1>
        <p>Beauty & skincare assistant</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            {m.content}
          </div>
        ))}
        {loading && <div className="typing">{PERSONA_NAMES[gender]} is thinking…</div>}
        <div ref={scrollRef} />
      </div>

      <div className="input-bar">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about skincare, makeup, routines…"
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
