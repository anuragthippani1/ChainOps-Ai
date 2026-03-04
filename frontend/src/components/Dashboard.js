import React, { useState, useEffect } from "react";
import { useDashboard } from "../context/DashboardContext";
import WorldMap from "./WorldMap";
import RiskTables from "./RiskTables";
import RiskCharts from "./RiskCharts";
import DisruptionAlerts from "./DisruptionAlerts";
import LoadingSpinner from "./LoadingSpinner";
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Ship,
  Globe,
  Activity,
} from "lucide-react";

const Dashboard = () => {
  const { dashboardData, currentSession, loadDashboardData } = useDashboard();
  const [animatedStats, setAnimatedStats] = useState({
    totalCountries: 0,
    highRiskCount: 0,
    lowRiskCount: 0,
    avgRisk: 0,
  });
  const [mounted, setMounted] = useState(false);

  // Calculate statistics
  const totalCountries = Object.keys(dashboardData.worldRiskData || {}).length;
  const highRiskCount = Object.values(dashboardData.worldRiskData || {}).filter(
    (d) => d.risk_level >= 3
  ).length;
  const lowRiskCount = Object.values(dashboardData.worldRiskData || {}).filter(
    (d) => d.risk_level === 1
  ).length;
  const avgRisk =
    totalCountries > 0
      ? (
          Object.values(dashboardData.worldRiskData || {}).reduce(
            (sum, d) => sum + d.risk_level,
            0
          ) / totalCountries
        ).toFixed(1)
      : 0;

  // Mount animation
  useEffect(() => {
    setMounted(true);
  }, []);

  // Animate numbers counting up
  useEffect(() => {
    if (!mounted) return;

    const duration = 1500; // 1.5 seconds
    const steps = 60;
    const interval = duration / steps;

    let currentStep = 0;
    const timer = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;

      setAnimatedStats({
        totalCountries: Math.floor(totalCountries * progress),
        highRiskCount: Math.floor(highRiskCount * progress),
        lowRiskCount: Math.floor(lowRiskCount * progress),
        avgRisk: (avgRisk * progress).toFixed(1),
      });

      if (currentStep >= steps) {
        clearInterval(timer);
        setAnimatedStats({
          totalCountries,
          highRiskCount,
          lowRiskCount,
          avgRisk,
        });
      }
    }, interval);

    return () => clearInterval(timer);
  }, [totalCountries, highRiskCount, lowRiskCount, avgRisk, mounted]);

  if (dashboardData.loading) {
    return <LoadingSpinner />;
  }

  if (dashboardData.error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex flex-col gap-3">
            <div>
              <h3 className="text-sm font-medium text-red-800">
                Error Loading Dashboard
              </h3>
              <div className="mt-2 text-sm text-red-700">
                {dashboardData.error}
              </div>
            </div>
            <button
              type="button"
              onClick={() => loadDashboardData()}
              className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const stats = [
    {
      label: "Total Regions",
      value: animatedStats.totalCountries,
      icon: Globe,
      gradient: "from-[#6D94C5] to-[#5A7DAD]",
      trend: "neutral",
      bgColor: "bg-[#CBDCEB]",
      iconColor: "text-[#6D94C5]",
      delay: "delay-[0ms]",
    },
    {
      label: "High Risk Zones",
      value: animatedStats.highRiskCount,
      icon: AlertTriangle,
      gradient: "from-[#C5946D] to-[#AD7D5A]",
      trend: "down",
      bgColor: "bg-[#F5EFE6]",
      iconColor: "text-[#C5946D]",
      delay: "delay-[100ms]",
    },
    {
      label: "Safe Zones",
      value: animatedStats.lowRiskCount,
      icon: CheckCircle,
      gradient: "from-[#6D94C5] to-[#5A7DAD]",
      trend: "up",
      bgColor: "bg-[#E8DFCA]",
      iconColor: "text-[#6D94C5]",
      delay: "delay-[200ms]",
    },
    {
      label: "Avg Risk Score",
      value: animatedStats.avgRisk,
      icon: TrendingUp,
      gradient: "from-[#E8DFCA] to-[#D4C5AE]",
      trend: "neutral",
      bgColor: "bg-[#F5EFE6]",
      iconColor: "text-[#6D94C5]",
      delay: "delay-[300ms]",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F5EFE6] via-[#CBDCEB] to-[#F5EFE6]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Modern Header with Gradient */}
        <div
          className={`mb-8 relative transform transition-all duration-700 ${
            mounted ? "translate-y-0 opacity-100" : "-translate-y-4 opacity-0"
          }`}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-[#6D94C5] to-[#CBDCEB] rounded-2xl opacity-10 animate-pulse"></div>
          <div className="relative bg-white rounded-2xl shadow-lg border border-[#E8DFCA] p-6 hover:shadow-2xl transition-shadow duration-300">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-3">
                  <div className="bg-gradient-to-br from-[#6D94C5] to-[#5A7DAD] p-3 rounded-xl animate-float">
                    <Ship className="h-8 w-8 text-white" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900">
                      Supply Chain Control Center
                    </h1>
                    <p className="mt-1 text-gray-600">
                      Real-time global logistics risk monitoring
                    </p>
                  </div>
                </div>
                {currentSession && (
                  <div className="mt-4 flex items-center space-x-2 text-sm">
                    <div className="bg-[#CBDCEB] text-[#6D94C5] px-3 py-1 rounded-full flex items-center space-x-2">
                      <div className="w-2 h-2 bg-[#6D94C5] rounded-full animate-pulse"></div>
                      <span className="font-medium">Active Session</span>
                    </div>
                    <span className="text-gray-500">{currentSession.name}</span>
                  </div>
                )}
              </div>
              <div className="hidden lg:flex items-center space-x-4">
                <div className="text-right">
                  <p className="text-sm text-gray-500">Last Updated</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {new Date().toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <div
              key={index}
              className={`relative bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 hover:scale-105 overflow-hidden group cursor-pointer transform ${
                mounted
                  ? "translate-y-0 opacity-100"
                  : "translate-y-8 opacity-0"
              } ${stat.delay}`}
            >
              {/* Animated gradient background */}
              <div
                className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${stat.gradient} opacity-10 rounded-full -mr-16 -mt-16 group-hover:opacity-20 transition-opacity duration-300`}
              ></div>

              {/* Shimmer effect on hover */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 transform -skew-x-12 group-hover:translate-x-full transition-all duration-1000"></div>

              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div
                    className={`${stat.bgColor} p-3 rounded-lg transform group-hover:rotate-6 group-hover:scale-110 transition-all duration-300`}
                  >
                    <stat.icon
                      className={`h-6 w-6 ${stat.iconColor} group-hover:animate-pulse`}
                    />
                  </div>
                  {stat.trend === "up" && (
                    <TrendingUp className="h-5 w-5 text-[#6D94C5] animate-bounce-slow" />
                  )}
                  {stat.trend === "down" && (
                    <TrendingDown className="h-5 w-5 text-[#C5946D] animate-bounce-slow" />
                  )}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1 group-hover:text-gray-900 transition-colors">
                    {stat.label}
                  </p>
                  <p className="text-3xl font-bold text-gray-900 group-hover:scale-110 transform transition-transform inline-block">
                    {stat.value}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-6">
          {/* World Risk Map - Modern Card */}
          <div
            className={`bg-white rounded-2xl shadow-xl border border-[#E8DFCA] overflow-hidden hover:shadow-2xl transition-all duration-500 transform ${
              mounted ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
            } delay-[400ms]`}
          >
            <div className="bg-gradient-to-r from-[#6D94C5] to-[#8AABCE] px-6 py-4 relative overflow-hidden">
              {/* Animated shimmer effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-10 animate-shimmer"></div>

              <div className="flex items-center space-x-3 relative z-10">
                <Globe className="h-6 w-6 text-white animate-spin-slow" />
                <div>
                  <h3 className="text-xl font-bold text-white">
                    Global Risk Heatmap
                  </h3>
                  <p className="text-sm text-[#CBDCEB] flex items-center space-x-2">
                    <Activity className="h-3 w-3 animate-pulse" />
                    <span>
                      Interactive world risk assessment & route monitoring
                    </span>
                  </p>
                </div>
              </div>
            </div>
            <div className="p-6 bg-gradient-to-br from-[#F5EFE6] to-[#E8DFCA]">
              <WorldMap worldRiskData={dashboardData.worldRiskData} />
            </div>
          </div>

          {/* Latest Disruption Alerts - Real-time supply chain news */}
          <DisruptionAlerts alerts={dashboardData.disruptionAlerts} />

          {/* Risk Tables - Modern Layout */}
          <RiskTables
            politicalRisks={dashboardData.politicalRisks}
            scheduleRisks={dashboardData.scheduleRisks}
          />

          {/* Risk Charts - Enhanced */}
          <RiskCharts
            politicalRisks={dashboardData.politicalRisks}
            scheduleRisks={dashboardData.scheduleRisks}
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
