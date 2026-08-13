import axios from "axios";

/**
 * Pre-configured Axios instance.
 * Base URL is read from the Vite env variable — never hardcoded.
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000, // 60s — browser automation requests can take a while
});

// Request interceptor for logging and header injection
apiClient.interceptors.request.use(
  (config) => {
    config.headers["X-Client-Version"] = "0.2.0";
    return config;
  },
  (error) => Promise.reject(error)
);

export default apiClient;

// ── Browser API Helpers ──────────────────────────────────────────────────────

export const browserAPI = {
  start:           () => apiClient.post("/browser/start"),
  stop:            () => apiClient.post("/browser/stop"),
  status:          () => apiClient.get("/browser/status"),
  open:       (url) => apiClient.post("/browser/open", { url }),
  screenshot:      () => apiClient.post("/browser/screenshot"),
  scroll: (direction = "down", amount = 500) =>
    apiClient.post("/browser/scroll", { direction, amount }),

  searchAmazon: (query, max_results = 50) =>
    apiClient.post("/browser/amazon/search", { query: query.trim(), max_results }),

  searchFlipkart: (query, max_results = 50) =>
    apiClient.post("/browser/flipkart/search", { query: query.trim(), max_results }),
};
