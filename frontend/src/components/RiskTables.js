import React, { useState, useEffect } from "react";
import {
  AlertTriangle,
  MapPin,
  ExternalLink,
  Package,
  Activity,
} from "lucide-react";

const RiskTables = ({ politicalRisks, scheduleRisks }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);
  const getRiskBadgeColor = (level) => {
    if (level >= 4) return "bg-red-100 text-red-800";
    if (level === 3) return "bg-orange-100 text-orange-800";
    if (level === 2) return "bg-yellow-100 text-yellow-800";
    if (level === 1) return "bg-green-100 text-green-800";
    return "bg-gray-100 text-gray-800";
  };

  const getRiskLabel = (level) => {
    if (level >= 4) return "Critical";
    if (level === 3) return "High";
    if (level === 2) return "Medium";
    if (level === 1) return "Low";
    return "Unknown";
  };

  return (
    <div className="space-y-6">
      {/* Political Risk Table */}
      <div
        className={`bg-white rounded-2xl shadow-xl border border-[#E8DFCA] overflow-hidden hover:shadow-2xl transition-all duration-500 transform ${
          mounted ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
        } delay-[500ms]`}
      >
        <div className="bg-gradient-to-r from-[#C5946D] to-[#D4A98A] px-6 py-4 relative overflow-hidden group">
          {/* Animated shimmer effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-10 animate-shimmer"></div>

          <div className="flex items-center space-x-3 relative z-10">
            <div className="animate-float">
              <AlertTriangle className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">
                Political Risk Analysis
              </h3>
              <p className="text-sm text-[#F5EFE6] flex items-center space-x-2">
                <Activity className="h-3 w-3 animate-pulse" />
                <span>Latest geopolitical events and policy changes</span>
              </p>
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Country
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Reasoning
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Source
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {politicalRisks.length > 0 ? (
                politicalRisks.map((risk, index) => (
                  <tr
                    key={index}
                    className="hover:bg-gradient-to-r hover:from-[#F5EFE6] hover:to-[#CBDCEB] transition-all duration-300 cursor-pointer transform hover:scale-[1.01]"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm font-medium text-gray-900">
                          {risk.country}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">
                        {risk.risk_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskBadgeColor(
                          risk.likelihood_score
                        )}`}
                      >
                        {getRiskLabel(risk.likelihood_score)} (
                        {risk.likelihood_score}/5)
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className="text-sm text-gray-900 max-w-xs truncate"
                        title={risk.reasoning}
                      >
                        {risk.reasoning}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {risk.source_url ? (
                        <a
                          href={risk.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 text-sm flex items-center"
                        >
                          {risk.source_title.length > 30
                            ? `${risk.source_title.substring(0, 30)}...`
                            : risk.source_title}
                          <ExternalLink className="h-3 w-3 ml-1" />
                        </a>
                      ) : (
                        <span className="text-sm text-gray-500">
                          {risk.source_title}
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan="5"
                    className="px-6 py-4 text-center text-gray-500"
                  >
                    No political risks identified
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Schedule Risk Table */}
      <div
        className={`bg-white rounded-2xl shadow-xl border border-[#E8DFCA] overflow-hidden hover:shadow-2xl transition-all duration-500 transform ${
          mounted ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
        } delay-[600ms]`}
      >
        <div className="bg-gradient-to-r from-[#6D94C5] to-[#8AABCE] px-6 py-4 relative overflow-hidden group">
          {/* Animated shimmer effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-10 animate-shimmer"></div>

          <div className="flex items-center space-x-3 relative z-10">
            <div className="animate-float">
              <Package className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">
                Schedule Risk Analysis
              </h3>
              <p className="text-sm text-[#CBDCEB] flex items-center space-x-2">
                <Activity className="h-3 w-3 animate-pulse" />
                <span>Equipment delivery delays and timeline risks</span>
              </p>
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Equipment ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Country
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Delay Days
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Factors
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {scheduleRisks.length > 0 ? (
                scheduleRisks.map((risk, index) => (
                  <tr
                    key={index}
                    className="hover:bg-gradient-to-r hover:from-[#F5EFE6] hover:to-[#CBDCEB] transition-all duration-300 cursor-pointer transform hover:scale-[1.01]"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-medium text-gray-900">
                        {risk.equipment_id}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-900">
                          {risk.country}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`text-sm font-medium ${
                          risk.delay_days > 0
                            ? "text-red-600"
                            : "text-green-600"
                        }`}
                      >
                        {risk.delay_days > 0
                          ? `+${risk.delay_days} days`
                          : "On time"}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskBadgeColor(
                          risk.risk_level
                        )}`}
                      >
                        {getRiskLabel(risk.risk_level)} ({risk.risk_level}/5)
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {risk.risk_factors.map((factor, factorIndex) => (
                          <span
                            key={factorIndex}
                            className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                          >
                            {factor}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan="5"
                    className="px-6 py-4 text-center text-gray-500"
                  >
                    No schedule risks identified
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RiskTables;
