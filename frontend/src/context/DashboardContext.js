import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";
import config from "../config";

const DashboardContext = createContext();

export const useDashboard = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error("useDashboard must be used within a DashboardProvider");
  }
  return context;
};

export const DashboardProvider = ({ children }) => {
  const [dashboardData, setDashboardData] = useState({
    worldRiskData: {},
    politicalRisks: [],
    scheduleRisks: [],
    disruptionAlerts: [],
    loading: true,
    error: null,
  });

  const [sessionId, setSessionId] = useState(null);
  const [currentSession, setCurrentSession] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [reports, setReports] = useState([]);

  // Generate session ID on component mount
  useEffect(() => {
    const newSessionId = `SENTRIX-${Date.now()}-${Math.random()
      .toString(36)
      .substr(2, 9)}`;
    setSessionId(newSessionId);
  }, []);

  // Load dashboard data (dynamic political risk providers may need extra time)
  const loadDashboardData = async () => {
    try {
      setDashboardData((prev) => ({ ...prev, loading: true, error: null }));
      const apiUrl = `${config.API_URL}/api/dashboard`;
      const response = await axios.get(apiUrl, { timeout: 30000 });

      setDashboardData({
        worldRiskData: response.data.world_risk_data || {},
        politicalRisks: response.data.political_risks || [],
        scheduleRisks: response.data.schedule_risks || [],
        disruptionAlerts: response.data.disruption_alerts || [],
        loading: false,
        error: null,
      });
    } catch (error) {
      console.error("Error loading dashboard data:", error);
      const isTimeout = error.message?.includes("timeout");
      const isNetwork = error.code === "ECONNREFUSED" || error.message === "Network Error";
      const message = isTimeout
        ? `Dashboard request timed out after 30s. The backend is running but upstream news providers may be slow. Please retry.`
        : isNetwork
        ? `Cannot reach the backend at ${config.API_URL}. Start it with: npm run server (or npm run dev from project root).`
        : `Failed to load dashboard: ${error.message}`;
      setDashboardData((prev) => ({
        ...prev,
        loading: false,
        error: message,
      }));
    }
  };

  // Load reports
  const loadReports = async () => {
    try {
      console.log(`Fetching reports from ${config.API_URL}/api/reports`);
      const response = await axios.get(`${config.API_URL}/api/reports`);
      const allReports = response.data.reports || [];

      // Filter reports by current session if we have one
      if (sessionId) {
        const sessionReports = allReports.filter(
          (report) => report.session_id === sessionId
        );
        setReports(sessionReports);
      } else {
        setReports(allReports);
      }
    } catch (error) {
      console.error("Error loading reports:", error);
    }
  };

  // Send chat message
  const sendChatMessage = async (message) => {
    const userMessage = {
      id: Date.now(),
      type: "user",
      content: message,
      timestamp: new Date().toISOString(),
    };

    setChatMessages((prev) => [...prev, userMessage]);

    try {
      const response = await axios.post(`${config.API_URL}/api/query`, {
        query: message,
        session_id: sessionId,
      });

      const botMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: response.data.response?.message || "Analysis complete",
        timestamp: new Date().toISOString(),
        data: response.data,
      };

      setChatMessages((prev) => [...prev, botMessage]);

      // If it's a report, refresh the reports list
      if (response.data.type === "report") {
        loadReports();
      }

      return response.data;
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: "Sorry, I encountered an error processing your request.",
        timestamp: new Date().toISOString(),
      };
      setChatMessages((prev) => [...prev, errorMessage]);
    }
  };

  // Download report
  const downloadReport = async (reportId) => {
    try {
      const response = await axios.get(
        `${config.API_URL}/api/reports/${reportId}/download`,
        {
          responseType: "blob",
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `chainops_report_${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading report:", error);
    }
  };

  const uploadShipmentData = async (data) => {
    try {
      const response = await axios.post(
        `${config.API_URL}/api/shipment/upload`,
        { data }
      );
      await loadDashboardData();
      return response.data;
    } catch (e) {
      console.error("Upload failed", e);
      throw e;
    }
  };

  const generateCombinedReport = async () => {
    try {
      const response = await axios.post(
        `${config.API_URL}/api/report/combined`
      );
      await loadReports();
      return response.data;
    } catch (e) {
      console.error("Combined report failed", e);
      throw e;
    }
  };

  // Session Management Functions
  const loadSessions = async () => {
    try {
      const response = await axios.get(`${config.API_URL}/api/sessions`);
      setSessions(response.data.sessions || []);
    } catch (error) {
      console.error("Error loading sessions:", error);
    }
  };

  const createSession = async (name, description = "") => {
    try {
      const response = await axios.post(`${config.API_URL}/api/sessions`, {
        name,
        description,
      });
      const newSession = response.data.session;
      setSessions((prev) => [newSession, ...prev]);
      return newSession;
    } catch (error) {
      console.error("Error creating session:", error);
      throw error;
    }
  };

  const switchToSession = async (sessionId) => {
    try {
      const response = await axios.get(
        `${config.API_URL}/api/sessions/${sessionId}`
      );
      const session = response.data.session;
      setCurrentSession(session);
      setSessionId(sessionId);

      // Clear current chat messages and load session-specific data
      setChatMessages([]);
      await loadReports();

      return session;
    } catch (error) {
      console.error("Error switching to session:", error);
      throw error;
    }
  };

  const updateSession = async (sessionId, updates) => {
    try {
      const response = await axios.put(
        `${config.API_URL}/api/sessions/${sessionId}`,
        updates
      );
      const updatedSession = response.data.session;

      setSessions((prev) =>
        prev.map((s) => (s.session_id === sessionId ? updatedSession : s))
      );

      if (currentSession && currentSession.session_id === sessionId) {
        setCurrentSession(updatedSession);
      }

      return updatedSession;
    } catch (error) {
      console.error("Error updating session:", error);
      throw error;
    }
  };

  const deleteSession = async (sessionId) => {
    try {
      await axios.delete(`${config.API_URL}/api/sessions/${sessionId}`);
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));

      // If we're deleting the current session, create a new one
      if (currentSession && currentSession.session_id === sessionId) {
        const newSession = await createSession(
          "New Session",
          "Auto-created session"
        );
        await switchToSession(newSession.session_id);
      }
    } catch (error) {
      console.error("Error deleting session:", error);
      throw error;
    }
  };

  // Load initial data
  useEffect(() => {
    loadDashboardData();
    loadReports();
    loadSessions();

    // Removed automatic polling to prevent page reloads
    // Users can manually refresh data when needed
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Reload reports when sessionId changes
  useEffect(() => {
    if (sessionId) {
      loadReports();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const value = {
    dashboardData,
    sessionId,
    currentSession,
    sessions,
    chatMessages,
    reports,
    loadDashboardData,
    loadReports,
    sendChatMessage,
    downloadReport,
    uploadShipmentData,
    generateCombinedReport,
    loadSessions,
    createSession,
    switchToSession,
    updateSession,
    deleteSession,
  };

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
};
