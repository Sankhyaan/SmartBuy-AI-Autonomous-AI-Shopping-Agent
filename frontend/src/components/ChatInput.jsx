import { useState, useRef, useEffect } from "react";
import apiClient from "../api/client";

/**
 * ChatInput — message input bar + chat history display.
 *
 * Handles:
 * - Input state
 * - POST /chat API call
 * - Rendering message history (user + agent bubbles)
 * - Loading and error states
 */
export default function ChatInput() {
  const [messages, setMessages] = useState([
    {
      id: 0,
      role: "agent",
      text: "Hello! I'm ShopAgent AI. Ask me to find any product, compare prices, or research deals. Full AI capabilities arrive in Phase 2. 🛒",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = { id: Date.now(), role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const { data } = await apiClient.post("/chat", { message: text });
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: "agent", text: data.reply },
      ]);
    } catch {
      setError("Could not reach the backend. Is it running?");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-section">
      {/* Message history */}
      <div className="chat-history">
        {messages.map((msg) => (
          <div key={msg.id} className={`chat-bubble ${msg.role}`}>
            <div className="bubble-avatar">
              {msg.role === "agent" ? "🤖" : "🧑"}
            </div>
            <div className="bubble-content">
              <span className="bubble-role">
                {msg.role === "agent" ? "ShopAgent AI" : "You"}
              </span>
              <p className="bubble-text">{msg.text}</p>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="chat-bubble agent">
            <div className="bubble-avatar">🤖</div>
            <div className="bubble-content">
              <span className="bubble-role">ShopAgent AI</span>
              <div className="typing-dots">
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="chat-error">
            <span>⚠️ {error}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div className="chat-input-bar">
        <textarea
          id="chat-input"
          className="chat-textarea"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me to find a product, compare prices, or research deals..."
          rows={1}
          disabled={loading}
        />
        <button
          id="send-button"
          className={`send-btn ${loading ? "loading" : ""}`}
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          aria-label="Send message"
        >
          {loading ? (
            <div className="spinner" />
          ) : (
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}
