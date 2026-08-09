/**
 * ReasoningPanel — right panel placeholder.
 * Phase 2: Will stream LangGraph agent reasoning steps in real time.
 */
export default function ReasoningPanel() {
  return (
    <div className="panel reasoning-panel">
      <div className="panel-header">
        <div className="reasoning-pulse" />
        <span className="panel-title">Agent Reasoning</span>
      </div>

      <div className="panel-body">
        <div className="panel-placeholder">
          <div className="placeholder-icon reasoning-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z" />
              <path d="M10 21h4" />
              <path d="M9 9h1M14 9h1" />
              <path d="M12 6v3" />
            </svg>
          </div>
          <h3 className="placeholder-title">Agent Reasoning</h3>
          <p className="placeholder-subtitle">
            Real-time LangGraph thought stream
            <br />
            arrives in <strong>Phase 2</strong>
          </p>
          <div className="placeholder-tags">
            <span className="tag">LangGraph</span>
            <span className="tag">RAG</span>
            <span className="tag">Tool Calls</span>
          </div>
        </div>
      </div>
    </div>
  );
}
