import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDashboard } from "../context/DashboardContext";
import {
  TrendingUp,
  Globe,
  AlertTriangle,
  FileText,
  ArrowRight,
  Shield,
  BarChart3,
  Map,
  Zap,
  Activity,
  Package,
  Ship,
  Clock,
  CheckCircle,
  TrendingDown,
} from "lucide-react";
import IntroAnimation from "./IntroAnimation";

// Animated Counter Component
const AnimatedCounter = ({ end, duration = 2000, suffix = "" }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime;
    let animationFrame;

    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime;
      const progress = (currentTime - startTime) / duration;

      if (progress < 1) {
        setCount(Math.floor(end * progress));
        animationFrame = requestAnimationFrame(animate);
      } else {
        setCount(end);
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

const Home = () => {
  const navigate = useNavigate();
  const { dashboardData, reports } = useDashboard();

  // Always show intro when landing on home page
  const [showIntro, setShowIntro] = useState(true);

  // Live Activity Feed - MUST be defined before any conditional returns
  const [activities] = useState([
    {
      type: "success",
      icon: CheckCircle,
      message: "Shipment #SX-1234 delivered to Dubai",
      time: "2 mins ago",
    },
    {
      type: "info",
      icon: Ship,
      message: "Route optimized for cargo #SX-5678",
      time: "5 mins ago",
    },
    {
      type: "warning",
      icon: AlertTriangle,
      message: "Weather delay detected in Pacific route",
      time: "8 mins ago",
    },
    {
      type: "success",
      icon: CheckCircle,
      message: "Customs clearance completed - Port of Singapore",
      time: "12 mins ago",
    },
  ]);

  const handleIntroComplete = () => {
    setShowIntro(false);
  };

  // Show intro animation only on page refresh
  if (showIntro) {
    return <IntroAnimation onComplete={handleIntroComplete} />;
  }

  // Calculate statistics
  const totalCountries = Object.keys(dashboardData.worldRiskData || {}).length;
  const highRiskCountries = Object.values(
    dashboardData.worldRiskData || {}
  ).filter((data) => data.risk_level >= 3).length;
  const totalReports = reports.length;
  const criticalAlerts = Object.values(
    dashboardData.worldRiskData || {}
  ).filter((data) => data.risk_level === 4).length;

  const stats = [
    {
      label: "Countries Monitored",
      value: totalCountries,
      icon: Globe,
    },
    {
      label: "High Risk Countries",
      value: highRiskCountries,
      icon: AlertTriangle,
    },
    {
      label: "Reports Generated",
      value: totalReports,
      icon: FileText,
    },
    {
      label: "Critical Alerts",
      value: criticalAlerts,
      icon: Shield,
    },
  ];

  const quickActions = [
    {
      title: "Live Dashboard",
      description: "Real-time shipment tracking and analytics",
      icon: BarChart3,
      path: "/dashboard",
    },
    {
      title: "AI Assistant",
      description: "Smart route optimization and recommendations",
      icon: Zap,
      path: "/assistant",
    },
    {
      title: "Shipping Reports",
      description: "Detailed route analysis and performance reports",
      icon: FileText,
      path: "/reports",
    },
    {
      title: "Route Planner",
      description: "Interactive global shipping route visualization",
      icon: Map,
      path: "/dashboard",
    },
  ];

  const features = [
    {
      title: "Real-Time Tracking",
      description:
        "Monitor shipments across 100+ countries with live location updates and ETAs.",
      icon: Globe,
    },
    {
      title: "Smart Automation",
      description:
        "AI-powered route optimization, automated alerts, and intelligent scheduling.",
      icon: TrendingUp,
    },
    {
      title: "Instant Updates",
      description:
        "Get real-time notifications for delays, route changes, and delivery milestones.",
      icon: FileText,
    },
    {
      title: "Simplified Process",
      description:
        "Streamlined workflows with intuitive dashboards and one-click actions.",
      icon: BarChart3,
    },
  ];

  // Key Metrics Data
  const keyMetrics = [
    {
      label: "Active Shipments",
      value: 1247,
      trend: "+12%",
      icon: Package,
      color: "blue",
    },
    {
      label: "Routes Optimized",
      value: 89,
      trend: "+23%",
      icon: Ship,
      color: "green",
    },
    {
      label: "Avg Delivery Time",
      value: 12.3,
      suffix: " days",
      trend: "-8%",
      icon: Clock,
      color: "purple",
    },
    {
      label: "On-Time Delivery",
      value: 98.7,
      suffix: "%",
      trend: "+2%",
      icon: CheckCircle,
      color: "emerald",
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
                    Live Tracking • Real-Time Updates
                  </span>
                </div>
              </div>

              <h1 className="text-5xl md:text-7xl font-extrabold mb-6 text-white drop-shadow-2xl leading-tight">
                Welcome to ChainOps AI
              </h1>

              <p className="text-2xl md:text-3xl font-semibold text-gray-100 mb-6 drop-shadow-lg">
                AI-Powered Supply Chain Intelligence
              </p>

              <p className="text-base md:text-lg text-gray-200 max-w-3xl mx-auto leading-relaxed mb-4">
                <strong className="text-white">ChainOps AI</strong> is your
                intelligent shipping risk management platform that monitors
                <strong className="text-white"> political risks</strong>,{" "}
                <strong className="text-white">supply chain disruptions</strong>
                , and
                <strong className="text-white"> schedule delays</strong> across
                100+ countries in real-time.
              </p>

              <p className="text-sm md:text-base text-gray-300 max-w-3xl mx-auto leading-relaxed mb-8">
                Get AI-powered route analysis, automated risk reports, and
                instant alerts to make smarter logistics decisions and avoid
                costly delays before they happen.
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

      {/* Stats Section with Animated Counters */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md p-6 transform transition-all duration-200 hover:scale-105 cursor-pointer"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    {stat.label}
                  </p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                    <AnimatedCounter end={stat.value} duration={1500} />
                  </p>
                </div>
                <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg">
                  <stat.icon className="h-6 w-6 text-gray-600 dark:text-gray-300" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Metrics & Live Activity Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Key Metrics Dashboard */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                Key Metrics
              </h3>
              <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                <Activity className="h-4 w-4 mr-1 animate-pulse" />
                <span>Live</span>
              </div>
            </div>
            <div className="space-y-4">
              {keyMetrics.map((metric, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`p-2 bg-${metric.color}-100 dark:bg-${metric.color}-900/30 rounded-lg`}
                    >
                      <metric.icon
                        className={`h-5 w-5 text-${metric.color}-600 dark:text-${metric.color}-400`}
                      />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                        {metric.label}
                      </p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        <AnimatedCounter
                          end={metric.value}
                          duration={2000}
                          suffix={metric.suffix || ""}
                        />
                      </p>
                    </div>
                  </div>
                  <div
                    className={`flex items-center space-x-1 text-sm font-semibold ${
                      metric.trend.startsWith("+")
                        ? "text-green-600 dark:text-green-400"
                        : "text-red-600 dark:text-red-400"
                    }`}
                  >
                    {metric.trend.startsWith("+") ? (
                      <TrendingUp className="h-4 w-4" />
                    ) : (
                      <TrendingDown className="h-4 w-4" />
                    )}
                    <span>{metric.trend}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Live Activity Feed */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                Live Activity
              </h3>
              <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse mr-2"></div>
                <span>Real-time</span>
              </div>
            </div>
            <div className="space-y-3">
              {activities.map((activity, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors animate-fadeIn"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div
                    className={`p-2 rounded-lg ${
                      activity.type === "success"
                        ? "bg-green-100 dark:bg-green-900/30"
                        : activity.type === "warning"
                        ? "bg-yellow-100 dark:bg-yellow-900/30"
                        : "bg-blue-100 dark:bg-blue-900/30"
                    }`}
                  >
                    <activity.icon
                      className={`h-4 w-4 ${
                        activity.type === "success"
                          ? "text-green-600 dark:text-green-400"
                          : activity.type === "warning"
                          ? "text-yellow-600 dark:text-yellow-400"
                          : "text-blue-600 dark:text-blue-400"
                      }`}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 dark:text-white font-medium">
                      {activity.message}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {activity.time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <button
              onClick={() => navigate("/dashboard")}
              className="mt-4 w-full text-center text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white font-medium transition-colors"
            >
              View all activity →
            </button>
          </div>
        </div>
      </div>

      {/* Quick Actions Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 relative bg-white dark:bg-gray-900">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Quick Access
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Jump into action with our streamlined tools
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
              Why Choose ChainOps AI?
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              Modern shipping solutions that save time and reduce complexity
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group text-center transform transition-all duration-200 hover:scale-105"
              >
                <div className="bg-white dark:bg-gray-700 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-sm border border-gray-200 dark:border-gray-600 group-hover:shadow-md transition-all">
                  <feature.icon className="h-8 w-8 text-gray-700 dark:text-gray-300" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
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
              Ready to Streamline Your Shipping?
            </h2>
            <p className="text-lg text-gray-300 mb-8 max-w-2xl mx-auto">
              Experience real-time tracking and intelligent automation today
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
              © 2025 ChainOps AI. Modern Shipping Platform for Real-Time
              Updates.
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
