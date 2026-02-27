import React, { useState, useEffect } from "react";
import {
  MapPin,
  Plus,
  X,
  Navigation,
  DollarSign,
  Clock,
  TrendingUp,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Ship,
  Anchor,
} from "lucide-react";
import config from "../config";

const MultiPortRoutePlanner = () => {
  const [ports, setPorts] = useState(["", ""]);
  const [availablePorts, setAvailablePorts] = useState([]);
  const [optimization, setOptimization] = useState("balanced");
  const [routeAnalysis, setRouteAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedLegs, setExpandedLegs] = useState([]);

  // Fetch available ports on component mount
  useEffect(() => {
    fetchAvailablePorts();
  }, []);

  const fetchAvailablePorts = async () => {
    try {
      const response = await fetch(`${config.API_URL}/api/route/ports`);
      const data = await response.json();
      setAvailablePorts(data.ports || []);
    } catch (err) {
      console.error("Error fetching ports:", err);
    }
  };

  const addPort = () => {
    setPorts([...ports, ""]);
  };

  const removePort = (index) => {
    if (ports.length > 2) {
      const newPorts = ports.filter((_, i) => i !== index);
      setPorts(newPorts);
    }
  };

  const updatePort = (index, value) => {
    const newPorts = [...ports];
    newPorts[index] = value;
    setPorts(newPorts);
  };

  const planRoute = async () => {
    const filledPorts = ports.filter((p) => p.trim() !== "");

    if (filledPorts.length < 2) {
      setError("Please select at least 2 ports");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${config.API_URL}/api/route/plan-multi-port`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ports: filledPorts,
            optimization: optimization,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to plan route");
      }

      const data = await response.json();
      setRouteAnalysis(data.route_analysis);
      setExpandedLegs([0]); // Expand first leg by default
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleLeg = (index) => {
    setExpandedLegs((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    );
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case "high":
        return "text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400";
      case "medium":
        return "text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20 dark:text-yellow-400";
      case "low":
        return "text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400";
      default:
        return "text-gray-600 bg-gray-50 dark:bg-gray-700 dark:text-gray-400";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center space-x-3 mb-2">
            <Ship className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Multi-Port Route Planner
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Plan and optimize shipping routes across multiple ports worldwide
          </p>
        </div>

        {/* Route Planning Form */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <MapPin className="h-5 w-5 mr-2 text-blue-600 dark:text-blue-400" />
            Select Ports
          </h2>

          <div className="space-y-3 mb-6">
            {ports.map((port, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                  <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                    {index + 1}
                  </span>
                </div>
                <select
                  value={port}
                  onChange={(e) => updatePort(index, e.target.value)}
                  className="flex-1 p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select a port...</option>
                  {availablePorts.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
                {ports.length > 2 && (
                  <button
                    onClick={() => removePort(index)}
                    className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                )}
              </div>
            ))}
          </div>

          <button
            onClick={addPort}
            className="w-full mb-6 p-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-gray-600 dark:text-gray-400 hover:border-blue-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors flex items-center justify-center space-x-2"
          >
            <Plus className="h-5 w-5" />
            <span>Add Port</span>
          </button>

          {/* Optimization Options */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Optimization Strategy
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { value: "fastest", icon: Clock, label: "Fastest" },
                { value: "cheapest", icon: DollarSign, label: "Cheapest" },
                { value: "balanced", icon: TrendingUp, label: "Balanced" },
                { value: "safest", icon: AlertTriangle, label: "Safest" },
              ].map(({ value, icon: Icon, label }) => (
                <button
                  key={value}
                  onClick={() => setOptimization(value)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    optimization === value
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300"
                      : "border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:border-blue-300"
                  }`}
                >
                  <Icon className="h-5 w-5 mx-auto mb-1" />
                  <span className="text-sm font-medium">{label}</span>
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          <button
            onClick={planRoute}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Planning Route...</span>
              </>
            ) : (
              <>
                <Navigation className="h-5 w-5" />
                <span>Plan Route</span>
              </>
            )}
          </button>
        </div>

        {/* Route Analysis Results */}
        {routeAnalysis && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Total Distance
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {routeAnalysis.summary.total_distance_nm.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      nautical miles
                    </p>
                  </div>
                  <Navigation className="h-8 w-8 text-blue-600 dark:text-blue-400" />
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Total Time
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {routeAnalysis.summary.total_time_days.toFixed(1)}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      days
                    </p>
                  </div>
                  <Clock className="h-8 w-8 text-purple-600 dark:text-purple-400" />
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Total Cost
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      $
                      {(routeAnalysis.summary.total_cost_usd / 1000).toFixed(0)}
                      K
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      USD
                    </p>
                  </div>
                  <DollarSign className="h-8 w-8 text-green-600 dark:text-green-400" />
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Total Ports
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {routeAnalysis.total_ports}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {routeAnalysis.total_legs} legs
                    </p>
                  </div>
                  <Anchor className="h-8 w-8 text-orange-600 dark:text-orange-400" />
                </div>
              </div>
            </div>

            {/* Route Legs */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Route Legs
              </h2>
              <div className="space-y-3">
                {routeAnalysis.legs.map((leg, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
                  >
                    <button
                      onClick={() => toggleLeg(index)}
                      className="w-full p-4 bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center justify-between"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                          {index + 1}
                        </div>
                        <div className="text-left">
                          <p className="font-semibold text-gray-900 dark:text-white">
                            {leg.from} → {leg.to}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {leg.distance_nm.toLocaleString()} nm •{" "}
                            {leg.total_time_days.toFixed(1)} days • $
                            {(leg.total_cost_usd / 1000).toFixed(0)}K
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${getRiskColor(
                            leg.risk_level
                          )}`}
                        >
                          {leg.risk_level} risk
                        </span>
                        {expandedLegs.includes(index) ? (
                          <ChevronUp className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                        ) : (
                          <ChevronDown className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                        )}
                      </div>
                    </button>

                    {expandedLegs.includes(index) && (
                      <div className="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                          <div>
                            <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                              Distance
                            </p>
                            <p className="font-semibold text-gray-900 dark:text-white">
                              {leg.distance_nm.toLocaleString()} nm
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {leg.distance_km.toLocaleString()} km
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                              Transit Time
                            </p>
                            <p className="font-semibold text-gray-900 dark:text-white">
                              {leg.transit_time_days.toFixed(1)} days
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                              Port Wait
                            </p>
                            <p className="font-semibold text-gray-900 dark:text-white">
                              {leg.port_wait_time_days.toFixed(1)} days
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                              Fuel Cost
                            </p>
                            <p className="font-semibold text-gray-900 dark:text-white">
                              ${(leg.fuel_cost_usd / 1000).toFixed(1)}K
                            </p>
                          </div>
                        </div>
                        {leg.canal_name && (
                          <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                            <p className="text-sm font-medium text-blue-900 dark:text-blue-300">
                              🚢 Passes through {leg.canal_name}
                            </p>
                            <p className="text-xs text-blue-700 dark:text-blue-400 mt-1">
                              Canal toll: ${leg.canal_cost_usd.toLocaleString()}
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiPortRoutePlanner;
