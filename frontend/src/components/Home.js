import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDashboard } from "../context/DashboardContext";
import {
  Globe,
  AlertTriangle,
  FileText,
  ArrowRight,
  BarChart3,
  Map,
  Zap,
  Activity,
  Ship,
  Anchor,
  Shield,
} from "lucide-react";
import IntroAnimation from "./IntroAnimation";
import GlobalShippingMap from "./GlobalShippingMap";

// Animated Counter Component
const AnimatedCounter = ({ end, duration = 2000, suffix = "" }) => {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let startTime;
    let animationFrame;
    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min(1, (currentTime - startTime) / duration);
      if (progress < 1) {
        setCount(Math.floor((typeof end === "number" ? end : 0) * progress));
        animationFrame = requestAnimationFrame(animate);
      } else {
        setCount(typeof end === "number" ? end : 0);
      }
    };
    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [end, duration]);
  return (
    <span>
      {count.toLocaleString()}
      {suffix}
    </span>
  );
};

const formatRelativeTime = (isoStr) => {
  if (!isoStr) return "";
  try {
    const d = new Date(isoStr);
    const now = new Date();
    const diffMs = now - d;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins} mins ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return d.toLocaleDateString();
  } catch {
    return "";
  }
};

const getChokepointStatusColor = (status) => {
  if (status === "elevated") return "bg-amber-100 text-amber-800 border-amber-300";
  if (status === "active") return "bg-blue-100 text-blue-800 border-blue-300";
  return "bg-emerald-100 text-emerald-800 border-emerald-300";
};

const getRiskBadgeClass = (level) => {
  if (level === "critical") return "bg-red-100 text-red-800";
  if (level === "high") return "bg-orange-100 text-orange-800";
  if (level === "medium") return "bg-yellow-100 text-yellow-800";
  return "bg-green-100 text-green-800";
};

const Home = () => {
  const navigate = useNavigate();
  const { shippingIntelligence, loadShippingIntelligence } = useDashboard();

  const [showIntro, setShowIntro] = useState(true);
  const handleIntroComplete = () => setShowIntro(false);

  if (showIntro) {
    return <IntroAnimation onComplete={handleIntroComplete} />;
  }

  const {
    active_routes = 0,
    high_risk_routes = 0,
    disruption_alerts = 0,
    chokepoint_alerts = 0,
    recent_route_analysis = [],
    critical_alerts = [],
    chokepoint_status = [],
    world_risk_data = {},
    loading: intelLoading,
    error: intelError,
  } = shippingIntelligence;

  const shippingMetrics = [
    { label: "Active Shipping Routes", value: active_routes, icon: Ship, color: "blue" },
    { label: "High Risk Routes", value: high_risk_routes, icon: AlertTriangle, color: "amber" },
    { label: "Disruption Alerts", value: disruption_alerts, icon: Shield, color: "red" },
    { label: "Chokepoint Alerts", value: chokepoint_alerts, icon: Anchor, color: "purple" },
  ];

  const quickActions = [
    {
      title: "Control Center",
      description: "Global risk heatmap, disruptions, and political risks",
      icon: BarChart3,
      path: "/dashboard",
    },
    {
      title: "AI Assistant",
      description: "Route analysis, chokepoint detection, logistics advice",
      icon: Zap,
      path: "/assistant",
    },
    {
      title: "Reports",
      description: "Download PDF logistics intelligence reports",
      icon: FileText,
      path: "/reports",
    },
    {
      title: "Route Planner",
      description: "Multi-port route planning and risk analysis",
      icon: Map,
      path: "/route-planner",
    },
  ];

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 transition-colors">
      {/* Hero Section - Clean & Simple */}
      <div className="relative h-[600px] bg-gray-900 dark:bg-black text-white overflow-hidden">
        {/* Background Ship Image */}
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat brightness-90"
          style={{ backgroundImage: "url(/ship.jpg)" }}
        ></div>

        {/* Vignette Effect */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/30 to-black/50"></div>
        <div className="absolute inset-0 bg-gradient-to-r from-black/40 via-transparent to-black/40"></div>

        {/* Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-center relative z-10">
          <div className="text-center w-full">
            <div className="max-w-4xl mx-auto bg-black/40 backdrop-blur-lg rounded-2xl p-8 md:p-12 border border-white/10 shadow-2xl">
              <div className="inline-block mb-6">
                <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm px-6 py-3 rounded-full border border-white/20">
                  <Activity className="h-5 w-5 animate-pulse text-white" />
                  <span className="text-sm font-semibold text-white">
                    Maritime Intelligence • Refreshed every 60s
                  </span>
                </div>
              </div>

              <h1 className="text-5xl md:text-7xl font-extrabold mb-6 text-white drop-shadow-2xl leading-tight">
                ChainOps AI
              </h1>

              <p className="text-2xl md:text-3xl font-semibold text-gray-100 mb-6 drop-shadow-lg">
                AI-Powered Shipping Risk & Route Intelligence
              </p>

              <p className="text-base md:text-lg text-gray-200 max-w-3xl mx-auto leading-relaxed mb-4">
                <strong className="text-white">ChainOps AI</strong> aggregates
                political risks, supply chain disruptions, chokepoint status, and
                route analyses so <strong className="text-white">ship captains</strong>,{" "}
                <strong className="text-white">shipping operators</strong>, and{" "}
                <strong className="text-white">cargo logistics managers</strong> can
                make fast decisions without manually checking multiple systems.
              </p>

              <p className="text-sm md:text-base text-gray-300 max-w-3xl mx-auto leading-relaxed mb-8">
                Monitor global shipping risks, get route intelligence, and receive
                critical alerts in one place.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
                <button
                  onClick={() => navigate("/dashboard")}
                  className="group bg-white text-gray-900 px-8 py-4 rounded-lg font-semibold text-base shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center space-x-2"
                >
                  <span>View Dashboard</span>
                  <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </button>
                <button
                  onClick={() => navigate("/assistant")}
                  className="group bg-transparent text-white px-8 py-4 rounded-lg font-semibold text-base border-2 border-white/60 hover:bg-white/10 transform hover:scale-105 transition-all duration-200 flex items-center space-x-2"
                >
                  <Zap className="h-5 w-5" />
                  <span>Try AI Assistant</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* What ChainOps AI Does Section */}
      <div className="bg-gray-50 dark:bg-gray-800 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-6">
            What ChainOps AI Does
          </h2>
          <div className="space-y-6">
            {/* Real-Time Monitoring */}
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                  <Shield className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
              </div>
              <p className="text-base md:text-lg text-gray-700 dark:text-gray-300 leading-relaxed flex-1">
                ChainOps AI monitors real-time political risks, supply chain
                disruptions, and schedule delays across 100+ countries to help
                you make smarter shipping decisions. Track geopolitical
                tensions, trade policy changes, and potential delays before they
                impact your shipments.
              </p>
            </div>

            {/* AI-Powered Analysis */}
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                  <BarChart3 className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
              </div>
              <p className="text-base md:text-lg text-gray-700 dark:text-gray-300 leading-relaxed flex-1">
                Our AI-powered route analysis provides comprehensive insights
                including timing breakdowns, weather conditions, ocean climate
                data, and detailed risk assessments for every shipping route.
                Get smart recommendations to choose safer, faster routes and
                avoid costly disruptions.
              </p>
            </div>

            {/* Report Generation */}
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                  <FileText className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
              </div>
              <p className="text-base md:text-lg text-gray-700 dark:text-gray-300 leading-relaxed flex-1">
                Generate detailed PDF reports instantly with complete risk
                assessments, country-by-country analysis, mitigation strategies,
                and actionable insights. Download and share professional reports
                with your team to keep everyone informed and prepared.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Section 1 — Global Shipping Metrics */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Global Shipping Metrics
          </h2>
          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
            <Activity className="h-4 w-4 mr-1 animate-pulse" />
            <span>{intelLoading ? "Loading…" : "Live"}</span>
          </div>
        </div>
        {intelError && (
          <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg text-amber-800 dark:text-amber-200 text-sm">
            {intelError}
            <button
              onClick={() => loadShippingIntelligence()}
              className="ml-2 underline font-medium"
            >
              Retry
            </button>
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {shippingMetrics.map((metric, index) => (
            <div
              key={index}
              className="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md p-6 transform transition-all duration-200 hover:scale-105"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    {metric.label}
                  </p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                    <AnimatedCounter end={metric.value} duration={1500} />
                  </p>
                </div>
                <div className={`p-3 rounded-lg ${
                  metric.color === "blue" ? "bg-blue-100 dark:bg-blue-900/30" :
                  metric.color === "amber" ? "bg-amber-100 dark:bg-amber-900/30" :
                  metric.color === "red" ? "bg-red-100 dark:bg-red-900/30" :
                  "bg-purple-100 dark:bg-purple-900/30"
                }`}>
                  <metric.icon className={`h-6 w-6 ${
                    metric.color === "blue" ? "text-blue-600 dark:text-blue-400" :
                    metric.color === "amber" ? "text-amber-600 dark:text-amber-400" :
                    metric.color === "red" ? "text-red-600 dark:text-red-400" :
                    "text-purple-600 dark:text-purple-400"
                  }`} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Section 2 — Global Maritime Intelligence Snapshot */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Global Maritime Intelligence Snapshot
        </h2>
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
          <div className="p-4 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-600">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Routes: {active_routes} • Disruptions: {disruption_alerts} • Chokepoints: {chokepoint_alerts} • Elevated countries: {Object.values(world_risk_data).filter((d) => d.risk_level >= 3).length}
            </p>
          </div>
          <div className="p-6 min-h-[280px]">
            <GlobalShippingMap intelligenceData={shippingIntelligence} />
          </div>
        </div>
      </div>

      {/* Section 3 — Critical Shipping Alerts & Section 4 — Recent Route Intelligence */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Critical Shipping Alerts */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                Critical Shipping Alerts
              </h3>
              <Shield className="h-5 w-5 text-amber-500" />
            </div>
            <div className="space-y-3 max-h-[320px] overflow-y-auto">
              {critical_alerts.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400 py-4">
                  No critical alerts. Monitor continues.
                </p>
              ) : (
                critical_alerts.slice(0, 8).map((alert, idx) => (
                  <div
                    key={idx}
                    className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50"
                  >
                    <div className={`p-1.5 rounded ${
                      alert.severity === "critical" ? "bg-red-100 dark:bg-red-900/30" :
                      alert.severity === "high" ? "bg-amber-100 dark:bg-amber-900/30" :
                      "bg-blue-100 dark:bg-blue-900/30"
                    }`}>
                      <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {alert.message}
                        {alert.detail && <span className="text-gray-500 dark:text-gray-400"> — {alert.detail}</span>}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {formatRelativeTime(alert.timestamp)}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
            <button
              onClick={() => navigate("/dashboard")}
              className="mt-4 w-full text-center text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white font-medium"
            >
              View full dashboard →
            </button>
          </div>

          {/* Recent Route Intelligence */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                Recent Route Intelligence
              </h3>
              <Ship className="h-5 w-5 text-blue-500" />
            </div>
            <div className="space-y-3 max-h-[320px] overflow-y-auto">
              {recent_route_analysis.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400 py-4">
                  No route analyses yet. Use AI Assistant or Route Planner to analyze routes.
                </p>
              ) : (
                recent_route_analysis.slice(0, 6).map((r, idx) => (
                  <div
                    key={idx}
                    className="flex items-start justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 gap-3"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">
                        {r.route || "Route"}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                        {r.distance_nm != null && `${r.distance_nm} nm`}
                        {r.eta_days != null && ` • ${r.eta_days} days ETA`}
                        {r.chokepoints?.length > 0 && ` • ${r.chokepoints.join(", ")}`}
                      </p>
                    </div>
                    <span className={`shrink-0 px-2 py-0.5 text-xs font-medium rounded ${getRiskBadgeClass(r.risk_level || "low")}`}>
                      {r.risk_level || "low"}
                    </span>
                  </div>
                ))
              )}
            </div>
            <button
              onClick={() => navigate("/route-planner")}
              className="mt-4 w-full text-center text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white font-medium"
            >
              Plan new route →
            </button>
          </div>
        </div>
      </div>

      {/* Section 5 — Chokepoint Monitor */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Chokepoint Monitor
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {(chokepoint_status.length > 0 ? chokepoint_status : [
            { name: "Suez Canal", status: "unknown", disruption_count: 0, routes_affected: 0 },
            { name: "Strait of Hormuz", status: "unknown", disruption_count: 0, routes_affected: 0 },
            { name: "Strait of Malacca", status: "unknown", disruption_count: 0, routes_affected: 0 },
            { name: "Panama Canal", status: "unknown", disruption_count: 0, routes_affected: 0 },
            { name: "Bab el-Mandeb", status: "unknown", disruption_count: 0, routes_affected: 0 },
          ]).map((cp, idx) => (
            <div
              key={idx}
              className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <Anchor className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                <span className={`px-2 py-0.5 text-xs font-medium rounded border ${getChokepointStatusColor(cp.status)}`}>
                  {cp.status}
                </span>
              </div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">
                {cp.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {cp.disruption_count > 0 ? `${cp.disruption_count} disruption(s)` : "No disruptions"}
                {cp.routes_affected > 0 && ` • ${cp.routes_affected} route(s)`}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 relative bg-white dark:bg-gray-900">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Operator Tools
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Control center, AI assistant, reports, and route planner
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => navigate(action.path)}
              className="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md p-6 text-left transform transition-all duration-200 hover:scale-105"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg">
                  <action.icon className="h-6 w-6 text-gray-700 dark:text-gray-300" />
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 dark:text-gray-500 group-hover:translate-x-1 group-hover:text-gray-700 dark:group-hover:text-gray-300 transition-all" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {action.title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                {action.description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Features Section */}
      <div className="relative py-20 bg-gray-50 dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Maritime Intelligence Platform
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              Built for ship captains, shipping operators, and cargo logistics managers
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="group text-center transform transition-all duration-200 hover:scale-105">
              <div className="bg-white dark:bg-gray-700 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-sm border border-gray-200 dark:border-gray-600">
                <Globe className="h-8 w-8 text-gray-700 dark:text-gray-300" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Global Risk Monitoring</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Political risks, disruptions, and chokepoint status across 190+ countries</p>
            </div>
            <div className="group text-center transform transition-all duration-200 hover:scale-105">
              <div className="bg-white dark:bg-gray-700 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-sm border border-gray-200 dark:border-gray-600">
                <Ship className="h-8 w-8 text-gray-700 dark:text-gray-300" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Route Intelligence</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Distance, ETA, chokepoints, costs, and risk scores for maritime routes</p>
            </div>
            <div className="group text-center transform transition-all duration-200 hover:scale-105">
              <div className="bg-white dark:bg-gray-700 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-sm border border-gray-200 dark:border-gray-600">
                <AlertTriangle className="h-8 w-8 text-gray-700 dark:text-gray-300" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Critical Alerts</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Real-time disruption and political alerts affecting shipping corridors</p>
            </div>
            <div className="group text-center transform transition-all duration-200 hover:scale-105">
              <div className="bg-white dark:bg-gray-700 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-sm border border-gray-200 dark:border-gray-600">
                <FileText className="h-8 w-8 text-gray-700 dark:text-gray-300" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">PDF Reports</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Download logistics intelligence and route analysis reports</p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 relative">
        <div className="relative bg-gray-900 rounded-2xl shadow-xl p-12 md:p-16 text-center text-white overflow-hidden">
          <div className="relative z-10">
            <div className="inline-flex items-center space-x-2 bg-white/10 px-4 py-2 rounded-full mb-6">
              <Zap className="h-4 w-4" />
              <span className="text-sm font-semibold">Get Started Now</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Monitor Global Shipping Risks?
            </h2>
            <p className="text-lg text-gray-300 mb-8 max-w-2xl mx-auto">
              Access the control center and AI assistant for maritime intelligence
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <button
                onClick={() => navigate("/dashboard")}
                className="group bg-white text-gray-900 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all transform hover:scale-105 shadow-lg flex items-center justify-center"
              >
                <span>View Dashboard</span>
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={() => navigate("/assistant")}
                className="group bg-transparent text-white px-8 py-3 rounded-lg font-semibold border-2 border-white/40 hover:bg-white/10 transition-all transform hover:scale-105 flex items-center justify-center"
              >
                <Zap className="mr-2 h-5 w-5" />
                <span>Try Assistant</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="relative bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <img src="/logo.png" alt="ChainOps AI Logo" className="h-8 w-8" />
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                ChainOps AI
              </span>
            </div>
            <p className="text-gray-600 dark:text-gray-400 mb-2">
              © 2025 ChainOps AI. Maritime Intelligence Control Tower for Shipping Operators.
            </p>
            <p className="text-gray-500 dark:text-gray-500 text-sm flex items-center justify-center space-x-4">
              <span className="flex items-center">
                <Zap className="h-4 w-4 mr-1" /> Powered by AI
              </span>
              <span>•</span>
              <span className="flex items-center">
                <Globe className="h-4 w-4 mr-1" /> Global Coverage
              </span>
              <span>•</span>
              <span className="flex items-center">
                <Activity className="h-4 w-4 mr-1" /> 24/7 Monitoring
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
