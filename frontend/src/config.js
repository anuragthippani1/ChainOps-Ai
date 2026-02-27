// API Configuration
// In development, use 127.0.0.1 (more reliable than localhost on some systems).
// Set REACT_APP_API_URL in .env for production or custom backend.
const getApiUrl = () => {
  if (process.env.REACT_APP_API_URL) return process.env.REACT_APP_API_URL;
  if (typeof process.env.NODE_ENV !== "undefined" && process.env.NODE_ENV === "development") {
    return "http://127.0.0.1:8000";
  }
  return "http://127.0.0.1:8000";
};

const config = {
  API_URL: getApiUrl(),
};

export default config;
