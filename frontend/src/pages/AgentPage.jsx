import Navbar from "../components/Navbar";
import BrowserPanel from "../components/BrowserPanel";
import ReasoningPanel from "../components/ReasoningPanel";
import ChatInput from "../components/ChatInput";

/**
 * AgentPage — main application layout.
 *
 * Layout:
 * ┌─────────────────────────────────┐
 * │           Navbar                │
 * ├──────────────┬──────────────────┤
 * │ BrowserPanel │ ReasoningPanel   │
 * ├──────────────┴──────────────────┤
 * │           ChatInput             │
 * └─────────────────────────────────┘
 */
export default function AgentPage() {
  return (
    <div className="app-shell">
      <Navbar />

      <main className="main-grid">
        <BrowserPanel />
        <ReasoningPanel />
      </main>

      <ChatInput />
    </div>
  );
}
