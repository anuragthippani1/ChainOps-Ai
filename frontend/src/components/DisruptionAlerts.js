import React from "react";
import { ExternalLink, AlertTriangle, Clock } from "lucide-react";

const ALLOWED_CATEGORIES = ["maritime", "freight", "port disruption", "customs delay"];

const DisruptionAlerts = ({ alerts }) => {
  const filtered = (alerts || []).filter(
    (a) => !a.category || ALLOWED_CATEGORIES.includes((a.category || "").toLowerCase())
  );
  if (!filtered.length) return null;

  const getSeverityStyle = (severity) => {
    switch ((severity || "").toLowerCase()) {
      case "critical":
        return "bg-red-100 text-red-800 border-red-200";
      case "high":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "low":
      default:
        return "bg-green-100 text-green-800 border-green-200";
    }
  };

  const formatTimestamp = (isoStr) => {
    if (!isoStr) return "";
    try {
      const d = new Date(isoStr);
      const now = new Date();
      const diffMs = now - d;
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      if (diffHours < 1) return "Less than 1 hour ago";
      if (diffHours < 24) return `${diffHours}h ago`;
      return d.toLocaleDateString();
    } catch {
      return "";
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-[#E8DFCA] overflow-hidden">
      <div className="bg-gradient-to-r from-amber-500 to-orange-600 px-6 py-4">
        <div className="flex items-center space-x-3">
          <AlertTriangle className="h-6 w-6 text-white" />
          <div>
            <h3 className="text-xl font-bold text-white">
              Latest Disruption Alerts
            </h3>
              <p className="text-sm text-amber-100 flex items-center gap-2">
              <Clock className="h-3 w-3" />
              Logistics & shipment disruptions only • Last 24 hours
            </p>
          </div>
        </div>
      </div>
      <div className="divide-y divide-gray-100 max-h-[400px] overflow-y-auto">
        {filtered.map((alert, idx) => (
          <div
            key={alert.alert_id || idx}
            className="px-6 py-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex justify-between items-start gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  {alert.category && (
                    <span className="inline-flex px-2 py-0.5 text-xs font-medium rounded bg-slate-100 text-slate-700">
                      {alert.category}
                    </span>
                  )}
                  <span
                    className={`inline-flex px-2 py-0.5 text-xs font-semibold rounded border ${getSeverityStyle(
                      alert.risk_severity
                    )}`}
                  >
                    {alert.risk_severity || "medium"} ({(alert.risk_score || 2)}/5)
                  </span>
                  {alert.risk_signals?.slice(0, 3).map((s, i) => (
                    <span
                      key={i}
                      className="inline-flex px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded"
                    >
                      {s}
                    </span>
                  ))}
                </div>
                <h4 className="text-sm font-medium text-gray-900 mb-1">
                  {alert.title}
                </h4>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {alert.summary}
                </p>
                <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatTimestamp(alert.published_at)}
                  </span>
                  <span>{alert.source_name}</span>
                </div>
              </div>
              {alert.source_url && (
                <a
                  href={alert.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-shrink-0 inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
                >
                  Source
                  <ExternalLink className="h-4 w-4" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DisruptionAlerts;
