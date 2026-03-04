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


def port_to_country(port_or_city: str):
    """Map port/city name to country. Returns None if unknown."""
    key = (port_or_city or "").strip().lower()
    return PORT_TO_COUNTRY.get(key)


def risk_score_to_level(score: float) -> int:
    """Map risk_score (1-5) to risk_level (1-4) for heatmap."""
    if score >= 4:
        return 4
    if score >= 3:
        return 3
    if score >= 2:
        return 2
    return 1


def risk_level_to_label(level: int) -> str:
    if level >= 4:
        return "critical"
    if level == 3:
        return "high"
    if level == 2:
        return "medium"
    return "low"


def build_world_risk_from_alerts(disruption_alerts: list, political_risks: list = None) -> dict:
    """
    Build full world_risk_data: base countries (risk_level=1) + disruptions + political risks.
    final_risk_score = max(disruption_risk_score, political_risk_score).
    """
    result = get_base_world_risk_data()
    disruption_score_by_country = {}

    # Group alerts by country
    by_country = {}
    for a in disruption_alerts or []:
        country = (a.get("country") or "").strip()
        if not country:
            continue
        country = get_canonical_country(country)
        if country not in by_country:
            by_country[country] = []
        by_country[country].append(a)

    for country, alerts in by_country.items():
        scores = [a.get("risk_score", 2) for a in alerts if isinstance(a.get("risk_score"), (int, float))]
        avg_score = sum(scores) / len(scores) if scores else 2
        disruption_score_by_country[country] = avg_score
        level = risk_score_to_level(avg_score)
        latest = max(alerts, key=lambda x: x.get("published_at", ""))
        latest_text = latest.get("summary") or latest.get("title", "Disruption detected")
        result[country] = {
            "risk_level": level,
            "risk_label": risk_level_to_label(level),
            "disruption_count": len(alerts),
            "latest_disruption": latest_text[:200] if latest_text else None,
            "details": f"{len(alerts)} disruption(s) | {latest_text[:100]}..." if len(latest_text) > 100 else latest_text,
            "risk_factors": list({r for a in alerts for r in (a.get("risk_signals") or [])})[:5],
            "type": "logistics",
        }

    # Group political risks by country and merge with disruption risk.
    political_by_country = {}
    for p in political_risks or []:
        country = (p.get("country") or "").strip()
        if not country:
            continue
        country = get_canonical_country(country)
        score = p.get("likelihood_score")
        if not isinstance(score, (int, float)):
            continue
        if country not in political_by_country:
            political_by_country[country] = []
        political_by_country[country].append(p)

    for country, risks in political_by_country.items():
        political_scores = [r.get("likelihood_score", 1) for r in risks if isinstance(r.get("likelihood_score"), (int, float))]
        if not political_scores:
            continue
        political_score = max(political_scores)
        disruption_score = disruption_score_by_country.get(country, 1)
        final_score = max(disruption_score, political_score)
        final_level = risk_score_to_level(final_score)

        if country not in result:
            result[country] = {
                "risk_level": 1,
                "risk_label": "low",
                "disruption_count": 0,
                "latest_disruption": None,
                "details": "No disruptions detected",
                "risk_factors": [],
                "type": "logistics",
            }

        entry = result[country]
        entry["risk_level"] = final_level
        entry["risk_label"] = risk_level_to_label(final_level)
        political_factors = [r.get("risk_type") for r in risks if r.get("risk_type")]
        entry["risk_factors"] = list(dict.fromkeys((entry.get("risk_factors") or []) + political_factors))[:7]
        if entry.get("disruption_count", 0) == 0:
            entry["details"] = f"Political risk score {political_score}/5; no logistics disruptions detected"
            entry["type"] = "political"
        else:
            entry["details"] = f"{entry.get('details', '')} | Political risk score {political_score}/5"
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
