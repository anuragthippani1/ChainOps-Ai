import React, { useEffect, useMemo, useState } from "react";
import { ComposableMap, Geographies, Geography, Line, Marker } from "react-simple-maps";
import axios from "axios";
import config from "../config";

const geoUrl =
  "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson";

const CHOKEPOINT_COORDS = {
  "Suez Canal": [32.3, 30.3],
  "Strait of Hormuz": [56.2, 26.5],
  "Bab el-Mandeb": [43.3, 12.6],
  "Strait of Malacca": [100.8, 2.5],
  "Panama Canal": [-79.6, 9.1],
  "Taiwan Strait": [119.5, 24.5],
  "Strait of Gibraltar": [-5.6, 36.0],
  "English Channel": [1.5, 50.5],
  "Bosphorus": [29.0, 41.0],
  "Strait of Dover": [1.5, 51.1],
  "Sunda Strait": [105.8, -5.9],
  "Strait of Lombok": [115.8, -8.4],
};

const VOYAGE_ROUTE_WAYPOINTS = [
  { name: "Shanghai", coordinates: [121.5, 31.2] },
  { name: "Singapore", coordinates: [103.8, 1.29] },
  { name: "Suez Canal", coordinates: [32.3, 30.3] },
  { name: "Rotterdam", coordinates: [4.5, 51.9] },
];

const COUNTRY_COORDS = {
  Iran: [53.7, 32.4],
  Yemen: [48.5, 15.6],
  Somalia: [46.2, 5.1],
  Sudan: [30.2, 14.8],
  Ukraine: [31.2, 48.4],
  Egypt: [30.8, 26.8],
  "Saudi Arabia": [45.1, 23.9],
  "United Arab Emirates": [54.3, 23.4],
  Russia: [100.0, 61.0],
  China: [103.8, 35.8],
  Israel: [35.0, 31.5],
};

// DEMO DATA REMOVED – replaced with backend API
// Weather, risk zones, ports, and vessel feeds are now loaded via API endpoints.

const riskColor = (level) => {
  if (level >= 5) return "#DC2626"; // Critical
  if (level >= 4) return "#F97316"; // High
  if (level >= 3) return "#FACC15"; // Medium
  return "#10B981";
};

const getDisruptionCoord = (alert) => {
  const text = `${alert?.message || ""} ${alert?.detail || ""}`.toLowerCase();
  if (text.includes("red sea") || text.includes("bab el-mandeb") || text.includes("bab el mandeb"))
    return CHOKEPOINT_COORDS["Bab el-Mandeb"];
  if (text.includes("hormuz") || text.includes("iran")) return CHOKEPOINT_COORDS["Strait of Hormuz"];
  if (text.includes("suez") || text.includes("egypt")) return CHOKEPOINT_COORDS["Suez Canal"];
  if (text.includes("malacca") || text.includes("singapore")) return CHOKEPOINT_COORDS["Strait of Malacca"];
  if (text.includes("panama")) return CHOKEPOINT_COORDS["Panama Canal"];
  if (text.includes("taiwan")) return CHOKEPOINT_COORDS["Taiwan Strait"];
  if (text.includes("gibraltar")) return CHOKEPOINT_COORDS["Strait of Gibraltar"];
  if (text.includes("bosphorus")) return CHOKEPOINT_COORDS["Bosphorus"];
  if (text.includes("sunda")) return CHOKEPOINT_COORDS["Sunda Strait"];
  if (text.includes("lombok")) return CHOKEPOINT_COORDS["Strait of Lombok"];
  for (const [country, coord] of Object.entries(COUNTRY_COORDS)) {
    if (text.includes(country.toLowerCase())) return coord;
  }
  return null;
};

const inferRiskSignals = (alert) => {
  const text = `${alert?.message || ""} ${alert?.detail || ""}`.toLowerCase();
  const signals = [];
  if (text.includes("attack")) signals.push("maritime attack");
  if (text.includes("strike")) signals.push("port strike");
  if (text.includes("congestion")) signals.push("canal/port congestion");
  if (text.includes("blockade")) signals.push("blockade");
  if (text.includes("hormuz")) signals.push("hormuz chokepoint");
  if (text.includes("suez")) signals.push("suez chokepoint");
  if (text.includes("bab el-mandeb") || text.includes("red sea")) signals.push("bab el-mandeb chokepoint");
  return signals;
};

const toRiskLevel = (level) => {
  if (typeof level === "number") return level;
  if (level === "critical") return 5;
  if (level === "high") return 4;
  if (level === "medium") return 3;
  return 2;
};

const riskZoneColor = (level) => {
  const normalized = toRiskLevel(level);
  if (normalized >= 5) return "#DC2626";
  if (normalized >= 4) return "#F97316";
  return "#FACC15";
};

const GlobalShippingMap = ({ intelligenceData = {} }) => {
  const [layers, setLayers] = useState({
    routes: true,
    chokepoints: true,
    disruptions: true,
    riskSnapshot: true,
    weather: true,
    ports: true,
    vessels: true,
  });
  const [tooltip, setTooltip] = useState(null);
  // DEMO DATA REMOVED – replaced with backend API
  const [weatherEvents, setWeatherEvents] = useState([]);
  const [riskZones, setRiskZones] = useState([]);
  const [ports, setPorts] = useState([]);
  const [vessels, setVessels] = useState([]);

  const {
    chokepoint_status = [],
    critical_alerts = [],
    world_risk_data = {},
  } = intelligenceData;

  const routeSegments = useMemo(() => {
    const segments = [];
    for (let i = 0; i < VOYAGE_ROUTE_WAYPOINTS.length - 1; i += 1) {
      segments.push({
        id: `segment-${i}`,
        from: VOYAGE_ROUTE_WAYPOINTS[i].coordinates,
        to: VOYAGE_ROUTE_WAYPOINTS[i + 1].coordinates,
      });
    }
    return segments;
  }, []);

  const chokepoints = useMemo(() => {
    const statusByName = {};
    for (const cp of chokepoint_status || []) {
      if (cp?.name) statusByName[cp.name] = cp;
    }
    return Object.keys(CHOKEPOINT_COORDS).map((name) => ({
      name,
      coordinates: CHOKEPOINT_COORDS[name],
      status: statusByName[name]?.status || "clear",
      disruptions: statusByName[name]?.disruption_count || 0,
    }));
  }, [chokepoint_status]);

  const disruptionMarkers = useMemo(
    () =>
      (critical_alerts || [])
        .filter((a) => a?.type === "disruption" || a?.type === "political")
        .map((a, idx) => {
          const coordinates = getDisruptionCoord(a);
          if (!coordinates) return null;
          return {
            id: `alert-${idx}`,
            coordinates,
            title: a.message || "Disruption alert",
            country: a.detail || "Unknown location",
            severity: a.severity || "high",
            riskSignals: Array.isArray(a.risk_signals) && a.risk_signals.length > 0 ? a.risk_signals : inferRiskSignals(a),
          };
        })
        .filter(Boolean)
        .slice(0, 12),
    [critical_alerts]
  );

  const riskSnapshotMarkers = useMemo(() => {
    const markers = [];
    for (const [country, data] of Object.entries(world_risk_data || {})) {
      const level = data?.risk_level || 0;
      if (level < 3) continue;
      const coord = COUNTRY_COORDS[country];
      if (!coord) continue;
      markers.push({
        id: `risk-${country}`,
        country,
        level,
        coordinates: coord,
      });
    }
    return markers.slice(0, 20);
  }, [world_risk_data]);

  useEffect(() => {
    let isMounted = true;

    const normalizeCoord = (value) =>
      Array.isArray(value) && value.length === 2 ? [Number(value[0]), Number(value[1])] : null;

    const loadStaticLayers = async () => {
      try {
        const [weatherResponse, riskResponse, portsResponse] = await Promise.all([
          axios.get(`${config.API_URL}/api/weather`, { timeout: 12000 }),
          axios.get(`${config.API_URL}/api/risk-zones`, { timeout: 12000 }),
          axios.get(`${config.API_URL}/api/ports`, { timeout: 12000 }),
        ]);
        if (!isMounted) return;

        const weatherItems = Array.isArray(weatherResponse.data?.events)
          ? weatherResponse.data.events
          : Array.isArray(weatherResponse.data)
          ? weatherResponse.data
          : [];
        setWeatherEvents(
          weatherItems
            .map((item, idx) => {
              const coordinates = normalizeCoord(item?.coordinates);
              if (!coordinates) return null;
              return {
                id: item?.id || `weather-${idx}`,
                name: item?.name || "Marine weather event",
                coordinates,
                radius: Number(item?.radius) || 12,
              };
            })
            .filter(Boolean)
        );

        const riskItems = Array.isArray(riskResponse.data?.zones)
          ? riskResponse.data.zones
          : Array.isArray(riskResponse.data)
          ? riskResponse.data
          : [];
        setRiskZones(
          riskItems
            .map((item, idx) => {
              const coordinates = normalizeCoord(item?.coordinates);
              if (!coordinates) return null;
              return {
                id: item?.id || `risk-zone-${idx}`,
                coordinates,
                riskLevel: toRiskLevel(item?.risk_level ?? item?.level),
                radius: Number(item?.radius) || 12,
              };
            })
            .filter(Boolean)
        );

        const portItems = Array.isArray(portsResponse.data?.ports)
          ? portsResponse.data.ports
          : Array.isArray(portsResponse.data)
          ? portsResponse.data
          : [];
        setPorts(
          portItems
            .map((item, idx) => {
              const coordinates = normalizeCoord(item?.coordinates);
              if (!coordinates) return null;
              return {
                id: item?.port_name || `port-${idx}`,
                portName: item?.port_name || "Port",
                coordinates,
                congestionLevel: item?.congestion_level || "Unknown",
                shipsWaiting: Number(item?.ships_waiting) || 0,
              };
            })
            .filter(Boolean)
        );
      } catch (error) {
        console.error("Error loading GlobalShippingMap static layers:", error);
      }
    };

    loadStaticLayers();
    const intervalId = setInterval(loadStaticLayers, 60000);
    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  useEffect(() => {
    let isMounted = true;

    // DEMO DATA REMOVED – replaced with backend API
    const loadVessels = async () => {
      try {
        const response = await axios.get(`${config.API_URL}/api/vessels`, { timeout: 10000 });
        if (!isMounted) return;

        const vesselItems = Array.isArray(response.data?.vessels)
          ? response.data.vessels
          : Array.isArray(response.data)
          ? response.data
          : [];
        setVessels(
          vesselItems
            .map((item, idx) => {
              const lat = Number(item?.lat);
              const lon = Number(item?.lon);
              if (Number.isNaN(lat) || Number.isNaN(lon)) return null;
              return {
                id: item?.id || item?.vessel_name || `vessel-${idx}`,
                vesselName: item?.vessel_name || "Tracked vessel",
                lat,
                lon,
                speed: Number(item?.speed) || 0,
                heading: Number(item?.heading) || 0,
              };
            })
            .filter(Boolean)
        );
      } catch (error) {
        console.error("Error loading GlobalShippingMap vessel data:", error);
      }
    };

    loadVessels();
    const intervalId = setInterval(loadVessels, 5000);
    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  const toggleLayer = (key) => {
    setLayers((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const layerButtonClass = (enabled) =>
    `px-3 py-1.5 text-xs font-medium rounded-md border transition-all duration-300 ${
      enabled
        ? "bg-blue-600 text-white border-blue-600"
        : "bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border-gray-300 dark:border-gray-600"
    }`;

  return (
    <div className="w-full">
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <button
          className={layerButtonClass(layers.disruptions)}
          onClick={() => toggleLayer("disruptions")}
        >
          Show Disruptions
        </button>
        <button
          className={layerButtonClass(layers.riskSnapshot)}
          onClick={() => toggleLayer("riskSnapshot")}
        >
          Show Risk Snapshot
        </button>
        <button className={layerButtonClass(layers.weather)} onClick={() => toggleLayer("weather")}>
          Show Weather
        </button>
        <button className={layerButtonClass(layers.ports)} onClick={() => toggleLayer("ports")}>
          Show Ports
        </button>
        <button className={layerButtonClass(layers.vessels)} onClick={() => toggleLayer("vessels")}>
          Show Vessels
        </button>
      </div>

      <div className="relative rounded-xl border border-gray-200 dark:border-gray-700 bg-[#0B1E33] overflow-hidden">
        <ComposableMap
          projection="geoMercator"
          projectionConfig={{ scale: 130, center: [0, 25] }}
          width={980}
          height={460}
          className="w-full h-auto"
        >
          <Geographies geography={geoUrl}>
            {({ geographies }) =>
              geographies.map((geo) => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  style={{
                    default: { fill: "#2C4A6B", stroke: "#4F6F91", strokeWidth: 0.55, transition: "all 220ms ease" },
                    hover: { fill: "#355778", stroke: "#5E7FA2", strokeWidth: 0.6 },
                    pressed: { fill: "#274564", stroke: "#5E7FA2", strokeWidth: 0.6 },
                  }}
                />
              ))
            }
          </Geographies>

          <g style={{ opacity: layers.riskSnapshot ? 1 : 0, transition: "opacity 260ms ease" }}>
            {riskZones.map((zone) => (
              <Marker key={zone.id} coordinates={zone.coordinates}>
                <circle
                  r={zone.radius}
                  fill={riskZoneColor(zone.riskLevel)}
                  fillOpacity={0.22}
                  stroke={riskZoneColor(zone.riskLevel)}
                  strokeOpacity={0.7}
                  strokeWidth={0.9}
                />
              </Marker>
            ))}
          </g>

          <g style={{ opacity: layers.routes ? 1 : 0, transition: "opacity 360ms ease" }}>
            {routeSegments.map((route) => (
              <Line
                key={route.id}
                lineType="straight"
                from={route.from}
                to={route.to}
                stroke="#60A5FA"
                strokeWidth={2}
                strokeLinecap="round"
                strokeOpacity={0.85}
                strokeDasharray="5 3"
              />
            ))}

            {VOYAGE_ROUTE_WAYPOINTS.map((wp) => (
              <Marker key={wp.name} coordinates={wp.coordinates}>
                <circle r={3.5} fill="#FFFFFF" stroke="#60A5FA" strokeWidth={1.4} />
              </Marker>
            ))}
          </g>

          <g style={{ opacity: layers.weather ? 1 : 0, transition: "opacity 260ms ease" }}>
            {weatherEvents.map((wx) => (
              <Marker key={wx.id} coordinates={wx.coordinates}>
                <circle r={wx.radius} fill="#60A5FA" opacity={0.25} stroke="#60A5FA" strokeWidth={0.8} />
              </Marker>
            ))}
          </g>

          <g style={{ opacity: layers.chokepoints ? 1 : 0, transition: "opacity 260ms ease" }}>
            {chokepoints.map((cp) => (
              <Marker key={cp.name} coordinates={cp.coordinates}>
                <g>
                  <path d="M0,-6 L5,4 L-5,4 Z" fill="#F59E0B" stroke="#FFFFFF" strokeWidth={1} />
                  <circle r={1.1} fill="#FFFFFF" />
                </g>
              </Marker>
            ))}
          </g>

          <g style={{ opacity: layers.disruptions ? 1 : 0, transition: "opacity 260ms ease" }}>
            {disruptionMarkers.map((alert) => (
              <Marker key={alert.id} coordinates={alert.coordinates}>
                <g
                  onMouseEnter={(e) => {
                    setTooltip({
                      type: "disruption",
                      x: e.clientX,
                      y: e.clientY,
                      title: alert.title,
                      country: alert.country,
                      riskSignals: alert.riskSignals,
                    });
                  }}
                  onMouseMove={(e) => {
                    setTooltip((prev) => (prev ? { ...prev, x: e.clientX, y: e.clientY } : prev));
                  }}
                  onMouseLeave={() => setTooltip(null)}
                >
                  <g>
                    <circle r={12} fill="rgba(239,68,68,0.18)" stroke="#EF4444" strokeWidth={1.2} />
                    <circle r={3.2} fill="#EF4444" stroke="#FFFFFF" strokeWidth={1.1} />
                  </g>
                </g>
              </Marker>
            ))}
          </g>

          <g style={{ opacity: layers.ports ? 1 : 0, transition: "opacity 260ms ease" }}>
            {ports.map((port) => (
              <Marker key={port.id} coordinates={port.coordinates}>
                <g
                  onMouseEnter={(e) =>
                    setTooltip({
                      type: "port",
                      x: e.clientX,
                      y: e.clientY,
                      title: port.portName,
                      congestion: port.congestionLevel,
                      shipsWaiting: port.shipsWaiting,
                    })
                  }
                  onMouseMove={(e) => {
                    setTooltip((prev) => (prev ? { ...prev, x: e.clientX, y: e.clientY } : prev));
                  }}
                  onMouseLeave={() => setTooltip(null)}
                >
                  <circle r={4.2} fill="#FFFFFF" stroke="#4DA3FF" strokeWidth={1.4} />
                </g>
              </Marker>
            ))}
          </g>

          <g style={{ opacity: layers.vessels ? 1 : 0, transition: "opacity 260ms ease" }}>
            {vessels.map((v) => (
              <Marker key={v.id} coordinates={[v.lon, v.lat]}>
                <g
                  onMouseEnter={(e) =>
                    setTooltip({
                      type: "vessel",
                      x: e.clientX,
                      y: e.clientY,
                      title: v.vesselName,
                      speed: v.speed,
                      heading: v.heading,
                    })
                  }
                  onMouseMove={(e) => {
                    setTooltip((prev) => (prev ? { ...prev, x: e.clientX, y: e.clientY } : prev));
                  }}
                  onMouseLeave={() => setTooltip(null)}
                >
                  <path d="M0,-4 L3,3 L-3,3 Z" fill="#FFFFFF" stroke="#9CA3AF" strokeWidth={0.8} />
                </g>
              </Marker>
            ))}
          </g>

          <g style={{ opacity: layers.riskSnapshot ? 1 : 0, transition: "opacity 260ms ease" }}>
            {riskSnapshotMarkers.map((risk) => (
              <Marker key={risk.id} coordinates={risk.coordinates}>
                <circle r={4.8} fill={riskColor(risk.level)} stroke="#FFFFFF" strokeWidth={1.1} />
              </Marker>
            ))}
          </g>
        </ComposableMap>

        {tooltip && (
          <div
            className="pointer-events-none fixed z-50 max-w-xs rounded-lg border border-slate-600 bg-slate-900/95 px-3 py-2 text-xs text-slate-100 shadow-2xl"
            style={{ left: tooltip.x + 12, top: tooltip.y + 12 }}
          >
            <div className="font-semibold text-slate-100">{tooltip.title}</div>
            {tooltip.type === "port" ? (
              <div className="mt-1 text-slate-300 space-y-0.5">
                <div>Congestion: {tooltip.congestion}</div>
                <div>Ships waiting: {tooltip.shipsWaiting}</div>
              </div>
            ) : tooltip.type === "vessel" ? (
              <div className="mt-1 text-slate-300 space-y-0.5">
                <div>Speed: {tooltip.speed} kn</div>
                <div>Heading: {tooltip.heading}°</div>
              </div>
            ) : (
              <>
                <div className="mt-1 text-slate-300">{tooltip.country}</div>
                <div className="mt-1 text-slate-400">
                  Signals: {tooltip.riskSignals?.length ? tooltip.riskSignals.join(", ") : "N/A"}
                </div>
              </>
            )}
          </div>
        )}
      </div>

      <div className="mt-3 rounded-lg border border-slate-600 bg-[#112D4A] px-4 py-3 text-xs text-slate-100">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="inline-block h-1.5 w-6 rounded bg-[#60A5FA]" />
            <span>Voyage Route</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-full bg-white border border-[#60A5FA]" />
            <span>Waypoints</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-full bg-[#F59E0B]" />
            <span>Chokepoint Warnings</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-full bg-[#EF4444]" />
            <span>Disruption Zones</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-full bg-[#FACC15]" />
            <span>Risk Zones</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-full bg-[#60A5FA]" />
            <span>Weather</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-full bg-white border border-[#4DA3FF]" />
            <span>Ports</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-0 w-0 border-l-[5px] border-r-[5px] border-b-[8px] border-l-transparent border-r-transparent border-b-white" />
            <span>Vessels</span>
          </div>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3 text-xs transition-all duration-300">
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
          <span className="font-semibold text-gray-900 dark:text-white">Voyage Route</span>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Shanghai -> Singapore -> Suez -> Rotterdam</p>
        </div>
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
          <span className="font-semibold text-gray-900 dark:text-white">Waypoints</span>
          <p className="text-gray-500 dark:text-gray-400 mt-1">{VOYAGE_ROUTE_WAYPOINTS.length} plotted</p>
        </div>
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
          <span className="font-semibold text-gray-900 dark:text-white">Chokepoint Warnings</span>
          <p className="text-gray-500 dark:text-gray-400 mt-1">{chokepoints.length} strategic nodes</p>
        </div>
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
          <span className="font-semibold text-gray-900 dark:text-white">Disruption Zones</span>
          <p className="text-gray-500 dark:text-gray-400 mt-1">{disruptionMarkers.length} active alert zones</p>
        </div>
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
          <span className="font-semibold text-gray-900 dark:text-white">Ports / Vessels</span>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            {ports.length} monitored ports • {vessels.length} tracked vessels
          </p>
        </div>
      </div>
    </div>
  );
};

export default GlobalShippingMap;
