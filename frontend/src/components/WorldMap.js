import React, { useState } from "react";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";

const geoUrl =
  "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson";

const WorldMap = ({ worldRiskData = {} }) => {
  const [tooltipContent, setTooltipContent] = useState("");
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

  // Country name mapping to normalize different naming conventions
  // Maps GeoJSON names to backend data names
  const countryNameMapping = {
    // Americas
    "United States of America": "United States",
    USA: "United States",

    // Europe
    "United Kingdom": "United Kingdom",
    "Russian Federation": "Russia",
    "Czech Republic": "Czech Republic",
    Czechia: "Czech Republic",

    // Asia
    "People's Republic of China": "China",
    "Republic of Korea": "South Korea",
    "S. Korea": "South Korea",
    Korea: "South Korea",
    "Dem. Rep. Korea": "North Korea",
    "Democratic People's Republic of Korea": "North Korea",
    "Korea, Dem. Rep.": "North Korea",
    "Iran (Islamic Republic of)": "Iran",
    "Islamic Republic of Iran": "Iran",
    "Syrian Arab Republic": "Syria",
    "Viet Nam": "Vietnam",
    "Myanmar (Burma)": "Myanmar",
    Burma: "Myanmar",
    "Lao PDR": "Laos",
    "Lao People's Democratic Republic": "Laos",

    // Africa
    "Central African Rep.": "Central African Republic",
    "Dem. Rep. Congo": "Democratic Republic of the Congo",
    "Democratic Republic of the Congo": "Democratic Republic of the Congo",
    "Congo, Dem. Rep.": "Democratic Republic of the Congo",
    "Republic of the Congo": "Congo",
    Congo: "Congo",
    "United Republic of Tanzania": "Tanzania",
    "S. Sudan": "South Sudan",
    "Eq. Guinea": "Equatorial Guinea",
    "Equatorial Guinea": "Equatorial Guinea",
    "Côte d'Ivoire": "Ivory Coast",
    "Ivory Coast": "Ivory Coast",

    // Middle East
    Palestine: "Palestine",
    "West Bank": "Palestine",
    Gaza: "Palestine",
    "State of Palestine": "Palestine",

    // Balkans
    "Bosnia and Herz.": "Bosnia and Herzegovina",
    "Bosnia and Herzegovina": "Bosnia and Herzegovina",
    "N. Cyprus": "Cyprus",
    Macedonia: "North Macedonia",
    "North Macedonia": "North Macedonia",
  };

  const getRiskColor = (riskLevel) => {
    if (riskLevel >= 4) return "#EF4444"; // Critical Risk - Bright Red
    if (riskLevel === 3) return "#F97316"; // High Risk - Orange
    if (riskLevel === 2) return "#FDE047"; // Medium Risk - Yellow
    if (riskLevel === 1) return "#10B981"; // Low Risk - Green
    return "#E5E7EB"; // No Data - Very Light Gray
  };

  const getRiskLabel = (riskLevel) => {
    if (riskLevel >= 4) return "Critical Risk";
    if (riskLevel === 3) return "High Risk";
    if (riskLevel === 2) return "Medium Risk";
    if (riskLevel === 1) return "Low Risk";
    return "No Data";
  };

  const getCountryRiskData = (countryName) => {
    // Check if countryName is valid
    if (!countryName || typeof countryName !== "string") {
      return null;
    }

    // Try exact match first
    if (worldRiskData[countryName]) {
      return worldRiskData[countryName];
    }

    // Try mapped name
    const mappedName = countryNameMapping[countryName];
    if (mappedName && worldRiskData[mappedName]) {
      return worldRiskData[mappedName];
    }

    // Try case-insensitive match
    const lowerCountryName = countryName.toLowerCase();
    for (const [key, value] of Object.entries(worldRiskData)) {
      if (key.toLowerCase() === lowerCountryName) {
        return value;
      }
    }

    return null;
  };

  const handleMouseEnter = (geo, event) => {
    const countryName =
      geo.properties?.NAME ||
      geo.properties?.NAME_EN ||
      geo.properties?.name ||
      "Unknown Region";
    const riskData = getCountryRiskData(countryName);

    if (riskData && countryName !== "Unknown Region") {
      const riskLevel = riskData.risk_level;
      const riskColor = getRiskColor(riskLevel);
      const riskLabel = getRiskLabel(riskLevel);

      setTooltipContent(`
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-300 dark:border-gray-600 p-3 max-w-xs">
          <div class="flex items-center space-x-2 mb-2">
            <div class="w-3 h-3 rounded-full" style="background-color: ${riskColor}"></div>
            <div class="font-bold text-gray-900 dark:text-gray-100 text-sm">${countryName}</div>
          </div>
          <div>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium" style="background-color: ${riskColor}; color: white;">
              ${riskLabel}
            </span>
          </div>
        </div>
      `);
    } else if (countryName !== "Unknown Region") {
      setTooltipContent(`
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-300 dark:border-gray-600 p-3">
          <div class="font-semibold text-gray-900 dark:text-gray-100 text-sm mb-1">${countryName}</div>
          <div class="text-xs text-gray-500 dark:text-gray-400">No data available</div>
        </div>
      `);
    }

    setTooltipPosition({ x: event.clientX, y: event.clientY });
  };

  const handleMouseLeave = () => {
    setTooltipContent("");
  };

  return (
    <div className="w-full">
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{
          scale: 130,
          center: [0, 30],
        }}
        width={900}
        height={450}
        className="transition-all duration-300"
      >
        <Geographies geography={geoUrl}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const countryName =
                geo.properties?.NAME ||
                geo.properties?.NAME_EN ||
                geo.properties?.name;
              const riskData = getCountryRiskData(countryName);
              const riskLevel = riskData ? riskData.risk_level : 0;
              const fillColor = getRiskColor(riskLevel);

              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={fillColor}
                  stroke="#FFFFFF"
                  strokeWidth={0.5}
                  style={{
                    default: {
                      fill: fillColor,
                      outline: "none",
                      transition: "all 0.2s ease-in-out",
                    },
                    hover: {
                      fill: fillColor,
                      outline: "none",
                      stroke: "#3B82F6",
                      strokeWidth: 1.5,
                      opacity: 0.85,
                      cursor: "pointer",
                    },
                    pressed: {
                      fill: fillColor,
                      outline: "none",
                    },
                  }}
                  onMouseEnter={(event) => handleMouseEnter(geo, event)}
                  onMouseLeave={handleMouseLeave}
                />
              );
            })
          }
        </Geographies>
      </ComposableMap>

      {/* Tooltip */}
      {tooltipContent && (
        <div
          className="fixed z-50 pointer-events-none"
          style={{
            left: `${tooltipPosition.x + 10}px`,
            top: `${tooltipPosition.y + 10}px`,
          }}
          dangerouslySetInnerHTML={{ __html: tooltipContent }}
        />
      )}

      {/* Simple Legend */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">
          Risk Levels
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {[
            {
              level: 4,
              label: "Critical",
              color: "#EF4444",
            },
            {
              level: 3,
              label: "High",
              color: "#F97316",
            },
            {
              level: 2,
              label: "Medium",
              color: "#FDE047",
            },
            {
              level: 1,
              label: "Low",
              color: "#10B981",
            },
            {
              level: 0,
              label: "No Data",
              color: "#E5E7EB",
            },
          ].map(({ level, label, color }) => (
            <div key={level} className="flex items-center space-x-2">
              <div
                className="w-5 h-5 rounded-sm border border-gray-300"
                style={{ backgroundColor: color }}
              />
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                {label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Summary */}
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="text-xs font-medium text-gray-600 dark:text-gray-400">
            Countries Monitored
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">
            {Object.keys(worldRiskData).length}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="text-xs font-medium text-gray-600 dark:text-gray-400">
            High Risk Countries
          </div>
          <div className="text-2xl font-bold text-red-500 dark:text-red-400 mt-1">
            {
              Object.values(worldRiskData).filter(
                (data) => data.risk_level >= 3
              ).length
            }
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorldMap;
