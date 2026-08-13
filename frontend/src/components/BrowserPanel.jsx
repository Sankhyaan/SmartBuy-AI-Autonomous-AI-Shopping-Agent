import { useState, useEffect, useCallback } from "react";
import { browserAPI } from "../api/client";

/**
 * BrowserPanel — live browser automation dashboard.
 *
 * Features:
 * - Start/Stop browser controls
 * - Status indicator (online/offline)
 * - Amazon & Flipkart search tabs
 * - Product results grid with cards
 * - Screenshot preview
 */
export default function BrowserPanel() {
  const [status, setStatus] = useState({ is_running: false, current_url: null, title: null });
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("amazon");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [screenshot, setScreenshot] = useState(null);
  const [showScreenshot, setShowScreenshot] = useState(false);
  const [searchInfo, setSearchInfo] = useState(null);

  // Poll browser status periodically
  const fetchStatus = useCallback(async () => {
    try {
      const { data } = await browserAPI.status();
      setStatus(data);
    } catch {
      setStatus({ is_running: false, current_url: null, title: null });
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const handleStart = async () => {
    setActionLoading(true);
    setError(null);
    try {
      await browserAPI.start();
      await fetchStatus();
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to start browser");
    } finally {
      setActionLoading(false);
    }
  };

  const handleStop = async () => {
    setActionLoading(true);
    setError(null);
    try {
      await browserAPI.stop();
      setProducts([]);
      setScreenshot(null);
      setSearchInfo(null);
      await fetchStatus();
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to stop browser");
    } finally {
      setActionLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim() || loading) return;
    setLoading(true);
    setError(null);
    setProducts([]);
    setSearchInfo(null);
    try {
      const searchFn = activeTab === "amazon" ? browserAPI.searchAmazon : browserAPI.searchFlipkart;
      const { data } = await searchFn(searchQuery.trim());
      setProducts(data.products || []);
      setSearchInfo({ query: data.query, source: data.source, total: data.total });
    } catch (e) {
      setError(e.response?.data?.detail || `${activeTab} search failed`);
    } finally {
      setLoading(false);
    }
  };

  const handleScreenshot = async () => {
    setActionLoading(true);
    setError(null);
    try {
      const { data } = await browserAPI.screenshot();
      setScreenshot(data.image_base64);
      setShowScreenshot(true);
    } catch (e) {
      setError(e.response?.data?.detail || "Screenshot failed");
    } finally {
      setActionLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSearch();
    }
  };

  return (
    <div className="panel browser-panel">
      {/* Header */}
      <div className="panel-header">
        <div className={`status-dot-sm ${status.is_running ? "online" : "offline"}`} />
        <span className="panel-title">Browser Automation</span>
        <div className="panel-header-actions">
          {!status.is_running ? (
            <button
              className="btn-panel btn-start"
              onClick={handleStart}
              disabled={actionLoading}
              title="Launch Chromium Browser"
              aria-label="Start Playwright Browser"
            >
              {actionLoading ? "Starting..." : "▶ Start"}
            </button>
          ) : (
            <>
              <button
                className="btn-panel btn-screenshot"
                onClick={handleScreenshot}
                disabled={actionLoading}
                title="Capture live screenshot"
                aria-label="Capture page screenshot"
              >
                📷
              </button>
              <button
                className="btn-panel btn-stop"
                onClick={handleStop}
                disabled={actionLoading}
                title="Stop browser instance"
                aria-label="Stop Playwright Browser"
              >
                ⏹ Stop
              </button>
            </>
          )}
        </div>
      </div>

      <div className="panel-body">
        {!status.is_running ? (
          /* Idle state */
          <div className="panel-placeholder">
            <div className="placeholder-icon browser-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <rect x="2" y="3" width="20" height="14" rx="2" />
                <path d="M8 21h8M12 17v4" />
                <path d="M2 7h20" />
                <circle cx="5" cy="5" r="0.5" fill="currentColor" />
                <circle cx="7.5" cy="5" r="0.5" fill="currentColor" />
                <circle cx="10" cy="5" r="0.5" fill="currentColor" />
              </svg>
            </div>
            <h3 className="placeholder-title">Browser Offline</h3>
            <p className="placeholder-subtitle">
              Click <strong>Start</strong> to launch Playwright Chromium
            </p>
          </div>
        ) : (
          /* Active browser state */
          <div className="browser-active">
            {/* Current URL bar */}
            {status.current_url && (
              <div className="browser-url-bar">
                <span className="url-lock">🔒</span>
                <span className="url-text">{status.current_url}</span>
              </div>
            )}

            {/* Search tabs */}
            <div className="search-section">
              <div className="search-tabs">
                <button
                  className={`tab-btn ${activeTab === "amazon" ? "active" : ""}`}
                  onClick={() => setActiveTab("amazon")}
                >
                  🛒 Amazon
                </button>
                <button
                  className={`tab-btn ${activeTab === "flipkart" ? "active" : ""}`}
                  onClick={() => setActiveTab("flipkart")}
                >
                  🛍️ Flipkart
                </button>
              </div>

              <div className="search-bar">
                <input
                  type="text"
                  className="search-input"
                  placeholder={`Search ${activeTab === "amazon" ? "Amazon" : "Flipkart"}...`}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={loading}
                />
                {searchQuery && !loading && (
                  <button
                    className="search-clear-btn"
                    onClick={() => {
                      setSearchQuery("");
                      setProducts([]);
                      setSearchInfo(null);
                    }}
                    title="Clear search"
                  >
                    ✕
                  </button>
                )}
                <button
                  className="search-btn"
                  onClick={handleSearch}
                  disabled={loading || !searchQuery.trim()}
                >
                  {loading ? <div className="spinner-sm" /> : "🔍"}
                </button>
              </div>
              {/* Quick suggestion tags */}
              {!searchInfo && !loading && (
                <div className="quick-suggestions">
                  <span className="suggestion-label">Try searching:</span>
                  {["laptop", "headphones", "smartwatch", "running shoes"].map((tag) => (
                    <button
                      key={tag}
                      className="suggestion-chip"
                      onClick={() => {
                        setSearchQuery(tag);
                        setActiveTab(activeTab);
                      }}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Search info */}
            {searchInfo && (
              <div className="search-info">
                <span>{searchInfo.total} results for "<strong>{searchInfo.query}</strong>" on {searchInfo.source}</span>
              </div>
            )}

            {/* Loading state */}
            {loading && (
              <div className="browser-loading">
                <div className="spinner" />
                <span>Searching {activeTab === "amazon" ? "Amazon" : "Flipkart"}...</span>
              </div>
            )}

            {/* Product grid — 4 clean items only: Image, Title, Price, Rating */}
            {products.length > 0 && (
              <div className="product-grid">
                {products.map((product, idx) => (
                  <div key={idx} className="product-card">
                    {product.url ? (
                      <a href={product.url} target="_blank" rel="noopener noreferrer" className="product-image-link">
                        {product.image_url ? (
                          <div className="product-image">
                            <img src={product.image_url} alt={product.title} loading="lazy" />
                          </div>
                        ) : (
                          <div className="product-image placeholder">
                            <span>No Image</span>
                          </div>
                        )}
                      </a>
                    ) : (
                      product.image_url && (
                        <div className="product-image">
                          <img src={product.image_url} alt={product.title} loading="lazy" />
                        </div>
                      )
                    )}
                    <div className="product-info">
                      {product.url ? (
                        <a href={product.url} target="_blank" rel="noopener noreferrer" className="product-title-link">
                          <h4 className="product-title" title={product.title}>{product.title}</h4>
                        </a>
                      ) : (
                        <h4 className="product-title" title={product.title}>{product.title}</h4>
                      )}
                      <div className="product-meta">
                        <span className="product-price">{product.price}</span>
                        {product.rating ? (
                          <span className="product-rating">
                            ⭐ {product.rating}
                            {product.rating_count && ` (${product.rating_count})`}
                          </span>
                        ) : (
                          <span className="product-rating muted">⭐ N/A</span>
                        )}
                      </div>
                      {product.bought_past_month && (
                        <div className="product-bought">
                          🔥 {product.bought_past_month}
                        </div>
                      )}
                      <div className="product-footer">
                        <a
                          href={product.url || "#"}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="product-link"
                        >
                          View Product →
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* No results */}
            {!loading && searchInfo && products.length === 0 && (
              <div className="no-results">
                <span>No products found. Try a different search term.</span>
              </div>
            )}
          </div>
        )}

        {/* Error display */}
        {error && (
          <div className="browser-error">
            <span>⚠️ {error}</span>
            <button className="error-dismiss" onClick={() => setError(null)}>✕</button>
          </div>
        )}
      </div>

      {/* Screenshot modal with exit button */}
      {showScreenshot && screenshot && (
        <div className="screenshot-overlay" onClick={() => setShowScreenshot(false)}>
          <div className="screenshot-modal" onClick={(e) => e.stopPropagation()}>
            <div className="screenshot-header">
              <span className="modal-title">Live Browser Viewport</span>
              <button
                className="btn-back-to-search"
                onClick={() => setShowScreenshot(false)}
                title="Return to search dashboard"
              >
                ← Back to Search
              </button>
            </div>
            <div className="screenshot-body">
              <img
                src={`data:image/png;base64,${screenshot}`}
                alt="Browser screenshot"
                className="screenshot-img"
              />
            </div>
            <div className="screenshot-footer">
              <button
                className="btn-back-to-search-large"
                onClick={() => setShowScreenshot(false)}
              >
                ← Exit View & Return to Search
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
