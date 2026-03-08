import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bot,
  Ship,
  TerminalSquare,
  Waves,
} from "lucide-react";
import { useDashboard } from "../context/DashboardContext";
import IntroAnimation from "./IntroAnimation";
import GlobalShippingMap from "./GlobalShippingMap";

const AnimatedCounter = ({ end, duration = 1400 }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime;
    let animationFrame;
    const finalValue = typeof end === "number" ? end : 0;
    const run = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min(1, (timestamp - startTime) / duration);
      setCount(Math.floor(finalValue * progress));
      if (progress < 1) animationFrame = requestAnimationFrame(run);
    };
    animationFrame = requestAnimationFrame(run);
    return () => cancelAnimationFrame(animationFrame);
  }, [end, duration]);

  return <span>{count.toLocaleString()}</span>;
};

const formatRelativeTime = (isoStr) => {
  if (!isoStr) return "recently";
  const d = new Date(isoStr);
  const diffMins = Math.max(1, Math.floor((Date.now() - d.getTime()) / 60000));
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
  return `${Math.floor(diffMins / 1440)}d ago`;
};

const Home = () => {
  const navigate = useNavigate();
  const { shippingIntelligence, loadShippingIntelligence } = useDashboard();
  const [showIntro, setShowIntro] = useState(true);

  const {
    active_routes = 0,
    high_risk_routes = 0,
    disruption_alerts = 0,
    chokepoint_alerts = 0,
    recent_route_analysis = [],
    critical_alerts = [],
    world_risk_data = {},
    loading: intelLoading,
    error: intelError,
  } = shippingIntelligence;

  const elevatedCountries = Object.values(world_risk_data).filter((d) => d?.risk_level >= 3).length;

  const stats = [
    { label: "Active Routes", value: active_routes, trend: "+8.1%", icon: Ship },
    { label: "High Risk Routes", value: high_risk_routes, trend: "+2.4%", icon: AlertTriangle },
    { label: "Disruption Alerts", value: disruption_alerts, trend: "+4.9%", icon: Waves },
    { label: "Chokepoint Alerts", value: chokepoint_alerts, trend: "+3.2%", icon: Activity },
  ];

  const activityItems = useMemo(() => {
    const alerts = critical_alerts.slice(0, 4).map((alert) => ({
      title: alert.message || "Critical shipping alert",
      subtitle: `${alert.detail || "Global corridor"} - ${formatRelativeTime(alert.timestamp)}`,
    }));
    const routes = recent_route_analysis.slice(0, 3).map((route) => ({
      title: route.route || "Route intelligence updated",
      subtitle: `${route.risk_level || "low"} risk - ${route.distance_nm || 0} nm`,
    }));
    const rows = [...alerts, ...routes];
    return rows.length ? rows : [{ title: "Monitoring in progress", subtitle: "No critical activity in feed" }];
  }, [critical_alerts, recent_route_analysis]);

  const pulseMetrics = useMemo(
    () => [
      { label: "Threat Correlation Engine", value: Math.min(100, 36 + disruption_alerts * 8) },
      { label: "Route Stability Sensor", value: Math.min(100, 48 + active_routes * 4) },
      { label: "Chokepoint Pressure Index", value: Math.min(100, 34 + chokepoint_alerts * 9) },
      { label: "Geo-Risk Inference", value: Math.min(100, 52 + elevatedCountries * 2) },
    ],
    [active_routes, chokepoint_alerts, disruption_alerts, elevatedCountries]
  );

  const terminalLines = useMemo(
    () => [
      `> sync maritime-intelligence --status ${intelLoading ? "loading" : "live"}`,
      `> ingest disruptions :: ${disruption_alerts} events`,
      `> chokepoint monitor :: ${chokepoint_alerts} active`,
      `> elevated countries :: ${elevatedCountries}`,
      `> route risk model :: ${high_risk_routes} high-risk routes`,
    ],
    [intelLoading, disruption_alerts, chokepoint_alerts, elevatedCountries, high_risk_routes]
  );

  const createRipple = (event) => {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const ripple = document.createElement("span");
    ripple.className = "nm-ripple";
    ripple.style.width = `${size}px`;
    ripple.style.height = `${size}px`;
    ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
    ripple.style.top = `${event.clientY - rect.top - size / 2}px`;
    button.appendChild(ripple);
    setTimeout(() => ripple.remove(), 700);
  };

  if (showIntro) return <IntroAnimation onComplete={() => setShowIntro(false)} />;

  return (
    <div className="nm-page space-y-8">
      <section className="nm-flat nm-hero-card">
        <div>
          <p className="nm-subtext text-sm mb-3">Maritime Intelligence - refreshed every 60s</p>
          <h1 className="nm-heading text-4xl md:text-5xl">ChainOps AI</h1>
          <p className="nm-subtext mt-4 max-w-2xl">
            Soft UI dashboard for route risk awareness, disruption monitoring, and operator decision support.
          </p>
        </div>
        <div className="flex gap-3 flex-wrap">
          <button
            onClick={(e) => {
              createRipple(e);
              navigate("/dashboard");
            }}
            className="nm-button nm-ripple-btn"
          >
            <BarChart3 className="h-4 w-4" />
            Open Dashboard
          </button>
          <button
            onClick={(e) => {
              createRipple(e);
              navigate("/assistant");
            }}
            className="nm-button nm-ripple-btn"
          >
            <Bot className="h-4 w-4" />
            Try Assistant
          </button>
        </div>
      </section>

      {intelError && (
        <section className="nm-flat p-4 text-sm">
          <span className="text-amber-600 dark:text-amber-300">Intel feed warning: {intelError}</span>
          <button className="ml-3 underline nm-subtext" onClick={() => loadShippingIntelligence()}>
            Retry
          </button>
        </section>
      )}

      <section className="nm-stats-grid">
        {stats.map((card, idx) => {
          const Icon = card.icon;
          return (
            <article
              key={card.label}
              className="nm-flat nm-flat-hover nm-stat-card"
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              <div className="flex items-start justify-between">
                <div className="nm-inset nm-stat-icon">
                  <Icon className="h-5 w-5" />
                </div>
                <span className="nm-trend">{card.trend}</span>
              </div>
              <p className="nm-subtext text-xs uppercase tracking-[0.08em] mt-5">{card.label}</p>
              <p className="nm-heading text-3xl mt-2">
                <AnimatedCounter end={card.value} />
              </p>
            </article>
          );
        })}
      </section>

      <section className="nm-flat p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="nm-heading text-xl">Global Maritime Intelligence Snapshot</h2>
          <p className="nm-subtext text-sm">
            Routes {active_routes} - Disruptions {disruption_alerts} - Elevated Countries {elevatedCountries}
          </p>
        </div>
        <GlobalShippingMap intelligenceData={shippingIntelligence} />
      </section>

      <section className="nm-widget-grid">
        <article className="nm-flat p-5">
          <h3 className="nm-heading text-lg">Recent Activity</h3>
          <div className="mt-4 space-y-3">
            {activityItems.map((item, idx) => (
              <div
                key={`${item.title}-${idx}`}
                className="nm-activity-row"
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                <p className="nm-heading text-sm">{item.title}</p>
                <p className="nm-subtext text-xs mt-1">{item.subtitle}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="nm-flat p-5">
          <h3 className="nm-heading text-lg">Hardware Pulse</h3>
          <div className="mt-4 space-y-4">
            {pulseMetrics.map((metric, idx) => (
              <div key={metric.label} style={{ animationDelay: `${idx * 50}ms` }}>
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="nm-subtext">{metric.label}</span>
                  <span className="nm-heading">{metric.value}%</span>
                </div>
                <div className="nm-progress-track">
                  <div className="nm-progress-fill" style={{ width: `${metric.value}%` }} />
                </div>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="nm-inset nm-terminal p-5">
        <div className="flex items-center gap-2 mb-4">
          <span className="nm-dot nm-dot-red" />
          <span className="nm-dot nm-dot-amber" />
          <span className="nm-dot nm-dot-green" />
          <div className="flex items-center gap-2 ml-2 nm-subtext text-xs">
            <TerminalSquare className="h-3.5 w-3.5" />
            ChainOps Runtime Terminal
          </div>
        </div>
        <div className="nm-terminal-lines">
          {terminalLines.map((line, idx) => (
            <p key={line} style={{ animationDelay: `${idx * 300}ms` }}>
              {line}
            </p>
          ))}
          <span className="nm-cursor">_</span>
        </div>
      </section>
    </div>
  );
};

export default Home;
