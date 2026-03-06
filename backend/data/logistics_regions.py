"""
Major supply chain regions for Global Risk Heatmap.
Base list of countries that should always appear on the map.
Default risk_level = 1 (low) when no disruptions.
"""

# Full global country coverage for heatmap base data (~195)
ALL_WORLD_COUNTRIES = [
    "United States",
    "Canada",
    "Mexico",
    "Brazil",
    "Argentina",
    "United Kingdom",
    "France",
    "Germany",
    "Italy",
    "Spain",
    "Netherlands",
    "Belgium",
    "Poland",
    "Turkey",
    "Russia",
    "Saudi Arabia",
    "United Arab Emirates",
    "Qatar",
    "Kuwait",
    "Oman",
    "Iran",
    "Egypt",
    "South Africa",
    "India",
    "China",
    "Japan",
    "South Korea",
    "Vietnam",
    "Thailand",
    "Malaysia",
    "Singapore",
    "Indonesia",
    "Philippines",
    "Australia",
    "New Zealand",
    "Taiwan",
    "Afghanistan",
    "Albania",
    "Algeria",
    "Andorra",
    "Angola",
    "Antigua and Barbuda",
    "Armenia",
    "Austria",
    "Azerbaijan",
    "Bahamas",
    "Bahrain",
    "Bangladesh",
    "Barbados",
    "Belarus",
    "Belize",
    "Benin",
    "Bhutan",
    "Bolivia",
    "Bosnia and Herzegovina",
    "Botswana",
    "Brunei",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cambodia",
    "Cameroon",
    "Cape Verde",
    "Central African Republic",
    "Chad",
    "Chile",
    "Colombia",
    "Comoros",
    "Congo",
    "Costa Rica",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czech Republic",
    "Democratic Republic of the Congo",
    "Denmark",
    "Djibouti",
    "Dominica",
    "Dominican Republic",
    "Ecuador",
    "El Salvador",
    "Equatorial Guinea",
    "Eritrea",
    "Estonia",
    "Eswatini",
    "Ethiopia",
    "Fiji",
    "Finland",
    "Gabon",
    "Gambia",
    "Georgia",
    "Ghana",
    "Greece",
    "Grenada",
    "Guatemala",
    "Guinea",
    "Guinea-Bissau",
    "Guyana",
    "Haiti",
    "Honduras",
    "Hungary",
    "Iceland",
    "Iraq",
    "Ireland",
    "Israel",
    "Ivory Coast",
    "Jamaica",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kiribati",
    "Kyrgyzstan",
    "Laos",
    "Latvia",
    "Lebanon",
    "Lesotho",
    "Liberia",
    "Libya",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Madagascar",
    "Malawi",
    "Maldives",
    "Mali",
    "Malta",
    "Marshall Islands",
    "Mauritania",
    "Mauritius",
    "Micronesia",
    "Moldova",
    "Monaco",
    "Mongolia",
    "Montenegro",
    "Morocco",
    "Mozambique",
    "Myanmar",
    "Namibia",
    "Nauru",
    "Nepal",
    "Nicaragua",
    "Niger",
    "Nigeria",
    "North Korea",
    "North Macedonia",
    "Norway",
    "Pakistan",
    "Palau",
    "Palestine",
    "Panama",
    "Papua New Guinea",
    "Paraguay",
    "Peru",
    "Portugal",
    "Romania",
    "Rwanda",
    "Saint Kitts and Nevis",
    "Saint Lucia",
    "Saint Vincent and the Grenadines",
    "Samoa",
    "San Marino",
    "Sao Tome and Principe",
    "Senegal",
    "Serbia",
    "Seychelles",
    "Sierra Leone",
    "Slovakia",
    "Slovenia",
    "Solomon Islands",
    "Somalia",
    "South Sudan",
    "Sri Lanka",
    "Sudan",
    "Suriname",
    "Sweden",
    "Switzerland",
    "Syria",
    "Tajikistan",
    "Tanzania",
    "Timor-Leste",
    "Togo",
    "Tonga",
    "Trinidad and Tobago",
    "Tunisia",
    "Turkmenistan",
    "Tuvalu",
    "Uganda",
    "Ukraine",
    "Uruguay",
    "Uzbekistan",
    "Vanuatu",
    "Venezuela",
    "Yemen",
    "Zambia",
    "Zimbabwe",
]

# Normalize to canonical names for map matching
COUNTRY_ALIASES = {
    "USA": "United States",
    "US": "United States",
    "United States of America": "United States",
    "UK": "United Kingdom",
    "UAE": "United Arab Emirates",
    "Russian Federation": "Russia",
    "Republic of Korea": "South Korea",
    "Korea, Republic of": "South Korea",
    "Viet Nam": "Vietnam",
    "Iran (Islamic Republic of)": "Iran",
    "Syrian Arab Republic": "Syria",
    "Czechia": "Czech Republic",
    "Cabo Verde": "Cape Verde",
    "Cote d'Ivoire": "Ivory Coast",
    "Côte d'Ivoire": "Ivory Coast",
    "Bolivia (Plurinational State of)": "Bolivia",
    "Moldova, Republic of": "Moldova",
    "Venezuela (Bolivarian Republic of)": "Venezuela",
    "Brunei Darussalam": "Brunei",
    "Lao People's Democratic Republic": "Laos",
    "Democratic People's Republic of Korea": "North Korea",
    "Korea, Dem. Rep.": "North Korea",
    "Micronesia (Federated States of)": "Micronesia",
    "United Republic of Tanzania": "Tanzania",
}

# Port/city to country mapping
PORT_TO_COUNTRY = {
    "shanghai": "China",
    "rotterdam": "Netherlands",
    "dubai": "United Arab Emirates",
    "singapore": "Singapore",
    "los angeles": "United States",
    "hamburg": "Germany",
    "long beach": "United States",
    "busan": "South Korea",
    "hong kong": "China",
    "shenzhen": "China",
    "antwerp": "Belgium",
    "ningbo": "China",
    "qingdao": "China",
    "tianjin": "China",
    "guangzhou": "China",
    "kaohsiung": "Taiwan",
    "ho chi minh": "Vietnam",
    "saigon": "Vietnam",
    "manila": "Philippines",
    "bangkok": "Thailand",
    "jakarta": "Indonesia",
    "port klang": "Malaysia",
    "tanjung pelepas": "Malaysia",
    "port said": "Egypt",
    "suez": "Egypt",
    "suez canal": "Egypt",
    "colón": "Panama",
    "colon": "Panama",
    "panama canal": "Panama",
    "panama city": "Panama",
    "jebel ali": "United Arab Emirates",
    "fujairah": "United Arab Emirates",
    "dammam": "Saudi Arabia",
    "jeddah": "Saudi Arabia",
    "yanbu": "Saudi Arabia",
    "basra": "Iraq",
    "gdańsk": "Poland",
    "gdansk": "Poland",
    "bremen": "Germany",
    "le havre": "France",
    "mumbai": "India",
    "chennai": "India",
    "kolkata": "India",
    "yokohama": "Japan",
    "nagoya": "Japan",
    "osaka": "Japan",
    "kobe": "Japan",
    "houston": "United States",
    "new york": "United States",
    "savannah": "United States",
    "santos": "Brazil",
    "valencia": "Spain",
    "barcelona": "Spain",
    "algeciras": "Spain",
    "marseille": "France",
    "fos": "France",
    "izmir": "Turkey",
    "istanbul": "Turkey",
    "vancouver": "Canada",
}


def get_canonical_country(name: str) -> str:
    """Normalize country name to canonical form."""
    n = (name or "").strip()
    return COUNTRY_ALIASES.get(n, n)


# Geographic mapping: chokepoint name -> countries in/near that chokepoint.
# Used to assign chokepoint_conflict_score when alerts mention chokepoint activity.
CHOKEPOINT_TO_COUNTRIES = {
    "Suez Canal": ["Egypt"],
    "Strait of Hormuz": ["Iran", "United Arab Emirates", "Oman"],
    "Strait of Malacca": ["Singapore", "Malaysia", "Indonesia"],
    "Panama Canal": ["Panama", "Colombia"],
    "Bab el-Mandeb": ["Yemen", "Somalia", "Djibouti", "Saudi Arabia", "Eritrea"],
    "Red Sea": ["Yemen", "Saudi Arabia", "Egypt", "Somalia", "Djibouti"],
}

# Human-readable labels for risk_sources (for tooltip display)
RISK_SOURCE_DISPLAY = {
    "geopolitical_risk": "Geopolitical conflict",
    "disruption_alerts": "Shipping disruption",
    "conflict": "Geopolitical conflict",
    "war": "War / armed conflict",
    "sanctions": "Trade sanctions",
    "military_tension": "Military tension",
    "naval_activity": "Naval activity",
    "maritime_attack": "Maritime attack",
    "shipping_disruption": "Shipping disruption",
    "blockade": "Blockade risk",
    "hormuz_chokepoint": "Hormuz chokepoint tension",
    "suez_canal": "Suez Canal disruption",
    "malacca_chokepoint": "Malacca chokepoint tension",
    "panama_canal": "Panama Canal disruption",
    "bab_el_mandeb": "Bab el-Mandeb chokepoint tension",
    "red_sea_conflict": "Red Sea conflict",
    "weather_risk": "Weather event",
    "port_congestion": "Port congestion",
}

POLITICAL_HIGH_KEYWORDS = {
    "war": "war",
    "conflict": "conflict",
    "instability": "conflict",
    "regional instability": "conflict",
    "sanctions": "sanctions",
    "trade sanctions": "sanctions",
    "military tension": "military_tension",
    "military": "military_tension",
}

POLITICAL_MARITIME_KEYWORDS = {
    "shipping disruption": "shipping_disruption",
    "maritime attack": "maritime_attack",
    "naval activity": "naval_activity",
    "blockade": "blockade",
    "chokepoint": "shipping_disruption",
}

CHOKEPOINT_BASELINE_BY_COUNTRY = {
    "Iran": "hormuz_chokepoint",
    "United Arab Emirates": "hormuz_chokepoint",
    "Oman": "hormuz_chokepoint",
    "Yemen": "bab_el_mandeb",
    "Somalia": "bab_el_mandeb",
    "Djibouti": "bab_el_mandeb",
    "Saudi Arabia": "bab_el_mandeb",
    "Eritrea": "bab_el_mandeb",
    "Egypt": "suez_canal",
}


def _political_text_level_and_sources(risk: dict) -> tuple[int, list]:
    """Escalate political risk using reasoning/source text and chokepoint awareness."""
    country = get_canonical_country((risk.get("country") or "").strip())
    text = " ".join(
        str(v)
        for v in [
            risk.get("reasoning", ""),
            risk.get("source_title", ""),
            risk.get("risk_type", ""),
        ]
        if v
    ).lower()

    existing_level = risk.get("risk_level")
    if isinstance(existing_level, (int, float)):
        level = int(max(1, min(5, round(float(existing_level)))))
    else:
        score = risk.get("likelihood_score")
        level = risk_score_to_level(score) if isinstance(score, (int, float)) else 1

    sources = [s for s in (risk.get("risk_sources") or []) if isinstance(s, str)]

    if any(keyword in text for keyword in POLITICAL_HIGH_KEYWORDS):
        level = max(level, 4)
        for keyword, source in POLITICAL_HIGH_KEYWORDS.items():
            if keyword in text:
                sources.append(source)

    if any(keyword in text for keyword in POLITICAL_MARITIME_KEYWORDS):
        level = max(level, 3)
        for keyword, source in POLITICAL_MARITIME_KEYWORDS.items():
            if keyword in text:
                sources.append(source)

    chokepoint_source = CHOKEPOINT_BASELINE_BY_COUNTRY.get(country)
    if chokepoint_source:
        level = max(level, 3)
        sources.append(chokepoint_source)

    return level, list(dict.fromkeys(sources))


def _chokepoint_mentioned_in_alert(alert: dict) -> list:
    """Extract chokepoint names mentioned in alert text/signals."""
    title = (alert.get("title") or "") + " " + (alert.get("description") or "")
    summary = (alert.get("summary") or "")
    signals = alert.get("risk_signals") or []
    combined = (title + " " + summary + " " + " ".join(s for s in signals if isinstance(s, str))).lower()
    found = []
    for keyword, name in [
        ("red sea", "Red Sea"),
        ("bab el-mandeb", "Bab el-Mandeb"),
        ("bab el mandeb", "Bab el-Mandeb"),
        ("suez", "Suez Canal"),
        ("hormuz", "Strait of Hormuz"),
        ("malacca", "Strait of Malacca"),
        ("panama canal", "Panama Canal"),
    ]:
        if keyword in combined and name not in found:
            found.append(name)
    return found


def _has_weather_signal(alert: dict) -> bool:
    """Check if alert indicates weather-related disruption."""
    signals = [s.lower() for s in (alert.get("risk_signals") or []) if isinstance(s, str)]
    title = (alert.get("title") or "").lower()
    desc = (alert.get("description") or "").lower()
    combined = " ".join(signals) + " " + title + " " + desc
    return any(
        w in combined
        for w in ["typhoon", "hurricane", "cyclone", "storm", "weather", "monsoon", "flood"]
    )


def _has_congestion_signal(alert: dict) -> bool:
    """Check if alert indicates port/congestion disruption."""
    signals = [s.lower() for s in (alert.get("risk_signals") or []) if isinstance(s, str)]
    title = (alert.get("title") or "").lower()
    desc = (alert.get("description") or "").lower()
    combined = " ".join(signals) + " " + title + " " + desc
    return any(
        c in combined
        for c in ["port congestion", "congestion", "terminal congestion", "berth", "queue"]
    )


def port_to_country(port_or_city: str):
    """Map port/city name to country. Returns None if unknown."""
    key = (port_or_city or "").strip().lower()
    return PORT_TO_COUNTRY.get(key)


def risk_score_to_level(score: float) -> int:
    """Map risk_score (1-5) to risk_level (1-5) for heatmap. 5=critical, 4=high, 2-3=medium, 1=low."""
    if not isinstance(score, (int, float)):
        return 1
    s = float(score)
    if s >= 4.5:
        return 5
    if s >= 4:
        return 4
    if s >= 3:
        return 3
    if s >= 2:
        return 2
    return 1


def risk_level_to_label(level: int) -> str:
    """Map risk_level 1-5 to label. 5=critical, 4=high, 2-3=medium, 1=low."""
    if level >= 5:
        return "critical"
    if level >= 4:
        return "high"
    if level >= 2:
        return "medium"
    return "low"


def build_world_risk_from_alerts(disruption_alerts: list, political_risks: list = None) -> dict:
    """
    Build world_risk_data dynamically from live intelligence sources only.
    No static baselines. Risk = political + disruption + chokepoint + weather + congestion.
    """
    print(f"[DEBUG] build_world_risk_from_alerts: disruption_alerts={len(disruption_alerts or [])}, political_risks={len(political_risks or [])}")
    result = get_base_world_risk_data()
    disruption_by_country: dict = {}
    chokepoint_activity_by_country: dict = {}
    weather_risk_by_country: dict = {}
    congestion_by_country: dict = {}

    for a in disruption_alerts or []:
        country = get_canonical_country((a.get("country") or "").strip())
        if not country:
            continue
        if country not in disruption_by_country:
            disruption_by_country[country] = []
        disruption_by_country[country].append(a)

        for cp_name in _chokepoint_mentioned_in_alert(a):
            for c in CHOKEPOINT_TO_COUNTRIES.get(cp_name, []):
                chokepoint_activity_by_country.setdefault(c, []).append(cp_name)

        if _has_weather_signal(a):
            weather_risk_by_country[country] = True
        if _has_congestion_signal(a):
            congestion_by_country[country] = True

    disruption_avg_by_country = {}
    for c, alerts in disruption_by_country.items():
        scores = [a.get("risk_score") for a in alerts if isinstance(a.get("risk_score"), (int, float))]
        disruption_avg_by_country[c] = sum(scores) / len(scores) if scores else 2.0

    # Dedupe chokepoint lists
    chokepoint_activity_by_country = {
        c: list(dict.fromkeys(cps)) for c, cps in chokepoint_activity_by_country.items()
    }
    if disruption_by_country:
        print(f"[DEBUG] build_world_risk_from_alerts: countries with disruptions={list(disruption_by_country.keys())}")

    # Political risks (enriched by reasoning + source text + chokepoint context)
    political_level_by_country: dict = {}
    political_sources_by_country: dict = {}
    political_entries_by_country: dict = {}
    for p in political_risks or []:
        country = get_canonical_country((p.get("country") or "").strip())
        if not country:
            continue
        level, sources = _political_text_level_and_sources(p)
        political_level_by_country[country] = max(political_level_by_country.get(country, 0), level)
        political_sources_by_country.setdefault(country, []).extend(sources)
        political_entries_by_country.setdefault(country, []).append(p)

    # Compute dynamic risk for each country
    for country in result:
        signal_levels = []
        sources: list = []

        # Strategic maritime chokepoints should not default to low risk.
        chokepoint_baseline_source = CHOKEPOINT_BASELINE_BY_COUNTRY.get(country)
        if chokepoint_baseline_source:
            signal_levels.append(3)
            sources.append(chokepoint_baseline_source)

        # political_risk_score (escalated from reasoning/source text)
        pol_level = political_level_by_country.get(country, 0)
        if pol_level > 0:
            signal_levels.append(pol_level)
            sources.extend(political_sources_by_country.get(country, []))
            sources.append("geopolitical_risk")

        # disruption_severity
        if country in disruption_by_country:
            disp_avg = disruption_avg_by_country.get(country, 2)
            signal_levels.append(risk_score_to_level(disp_avg))
            sources.append("disruption_alerts")

        # chokepoint_conflict_score (strategic chokepoints cannot be low risk)
        cps = chokepoint_activity_by_country.get(country, [])
        if cps:
            cp_level = min(5, 3 + max(0, len(cps) - 1))
            signal_levels.append(cp_level)
            for cp in cps:
                slug = cp.lower().replace(" ", "_").replace("-", "_")
                if "red" in slug and "sea" in slug:
                    sources.append("red_sea_conflict")
                elif "hormuz" in slug:
                    sources.append("hormuz_chokepoint")
                elif "suez" in slug:
                    sources.append("suez_canal")
                elif "malacca" in slug:
                    sources.append("malacca_chokepoint")
                elif "panama" in slug:
                    sources.append("panama_canal")
                elif "bab" in slug or "mandeb" in slug:
                    sources.append("bab_el_mandeb")

        # weather_risk_score
        if weather_risk_by_country.get(country):
            signal_levels.append(3)
            sources.append("weather_risk")

        # congestion_score
        if congestion_by_country.get(country):
            signal_levels.append(3)
            sources.append("port_congestion")

        # Final level = maximum of available political/disruption/chokepoint/weather/congestion signals.
        level = max(signal_levels) if signal_levels else 1
        level = max(1, min(5, int(level)))

        entry = result[country]
        entry["risk_level"] = level
        entry["risk_label"] = risk_level_to_label(level)
        entry["risk_sources"] = list(dict.fromkeys(sources)) if sources else []
        entry["risk_sources_display"] = [
            RISK_SOURCE_DISPLAY.get(s, s.replace("_", " ").title()) for s in entry["risk_sources"]
        ] if entry["risk_sources"] else []

        if country in disruption_by_country:
            alerts = disruption_by_country[country]
            latest = max(alerts, key=lambda x: str(x.get("published_at", "")))
            latest_text = latest.get("summary") or latest.get("title", "Disruption detected")
            entry["disruption_count"] = len(alerts)
            entry["latest_disruption"] = latest_text[:200] if latest_text else None
            entry["details"] = f"{len(alerts)} disruption(s) | {latest_text[:100]}..." if len(latest_text) > 100 else latest_text
            entry["risk_factors"] = list({r for a in alerts for r in (a.get("risk_signals") or [])})[:5]
            entry["type"] = "logistics"

        if pol_level > 0:
            risks = political_entries_by_country.get(country, [])
            political_factors = [r.get("risk_type") for r in risks if r.get("risk_type")]
            entry["risk_factors"] = list(dict.fromkeys((entry.get("risk_factors") or []) + political_factors))[:7]
            if entry.get("disruption_count", 0) == 0:
                entry["details"] = f"Political risk level {pol_level}/5; no logistics disruptions detected"
                entry["type"] = "political" if entry.get("type") != "logistics" else "logistics+political"
            else:
                entry["type"] = "logistics+political"

    return result


def get_base_world_risk_data() -> dict:
    """Returns default risk data for full global countries list. risk_level=1 (low)."""
    result = {}
    seen = set()
    for c in ALL_WORLD_COUNTRIES:
        canonical = get_canonical_country(c)
        if canonical in seen:
            continue
        seen.add(canonical)
        result[canonical] = {
            "risk_level": 1,
            "risk_label": "low",
            "disruption_count": 0,
            "latest_disruption": None,
            "details": "No disruptions detected",
            "risk_factors": [],
            "type": "logistics",
        }
    return result
