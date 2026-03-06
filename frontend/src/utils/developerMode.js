export const isDeveloperModeEnabled = () => {
  if (typeof window === "undefined") return false;

  const storedValue = window.localStorage.getItem("chainops-ai-developer-mode");
  if (storedValue === "true") return true;

  const params = new URLSearchParams(window.location.search || "");
  const devParam = (params.get("dev") || "").toLowerCase();
  if (["1", "true", "on"].includes(devParam)) return true;

  return process.env.REACT_APP_DEVELOPER_MODE === "true";
};
