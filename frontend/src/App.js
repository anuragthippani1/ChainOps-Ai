import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AppShell from "./components/AppShell";
import Home from "./components/Home";
import Dashboard from "./components/Dashboard";
import ChainOpsAIAssistantPage from "./components/ChainOpsAIAssistantPage";
import Reports from "./components/Reports";
import ThinkingLogs from "./components/ThinkingLogs";
import SessionManagerPage from "./components/SessionManagerPage";
import MultiPortRoutePlanner from "./components/MultiPortRoutePlanner";
import { DashboardProvider } from "./context/DashboardContext";
import { ThemeProvider } from "./context/ThemeContext";
import "./index.css";

function App() {
  return (
    <ThemeProvider>
      <DashboardProvider>
        <Router>
          <AppShell>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/assistant" element={<ChainOpsAIAssistantPage />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/thinking-logs" element={<ThinkingLogs />} />
              <Route path="/session-manager" element={<SessionManagerPage />} />
              <Route path="/route-planner" element={<MultiPortRoutePlanner />} />
            </Routes>
          </AppShell>
        </Router>
      </DashboardProvider>
    </ThemeProvider>
  );
}

export default App;
