from __future__ import annotations

from pathlib import Path

try:  # pragma: no cover - shim for environments without pandas preinstalled
    import pandas as pd  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    class _FallbackDataFrame:
        def __init__(self, records: list[dict[str, str]]):
            self._records = records
            self._columns = list(records[0].keys()) if records else []

        def __len__(self) -> int:
            return len(self._records)

        def to_markdown(self, index: bool = False) -> str:
            headers = ([""] if index else []) + self._columns
            divider = ["---" for _ in headers]
            rows = []
            for row_idx, record in enumerate(self._records):
                row_values = [record.get(column, "") for column in self._columns]
                if index:
                    row_values.insert(0, str(row_idx))
                rows.append(row_values)

            def _line(values: list[str]) -> str:
                return "| " + " | ".join(values) + " |"

            lines = [_line(headers), _line(divider)]
            lines.extend(_line([str(value) for value in row]) for row in rows)
            return "\n".join(lines)

    class _FallbackPandasModule:
        @staticmethod
        def DataFrame(records: list[dict[str, str]]) -> _FallbackDataFrame:
            return _FallbackDataFrame(records)

    pd = _FallbackPandasModule()  # type: ignore


OUTPUT_PATH = Path("digital_delta_map_v1.md")
CHART_PATH = Path("artifacts/digital_delta_category_counts.svg")


def ensure_artifacts_dir() -> None:
    CHART_PATH.parent.mkdir(parents=True, exist_ok=True)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False)


def build_industry_df() -> pd.DataFrame:
    records = [
        {
            "Entity": "xAI",
            "Description": "Colossus supercomputer buildout; $12B investment, 500+ jobs.",
            "Location": "South Memphis",
            "Key AI/Energy Tie": "35 gas turbines (initially unpermitted); Tesla batteries; water recycling plant.",
            "Sample Coords (Lat, Lon)": "35.099, -90.025",
        },
        {
            "Entity": "FedEx",
            "Description": "Logistics AI for routing and supply chain; University of Memphis partner.",
            "Location": "Midtown Memphis HQ",
            "Key AI/Energy Tie": "Digital Delta supporter deploying AI optimization across operations.",
            "Sample Coords (Lat, Lon)": "35.149, -90.049",
        },
        {
            "Entity": "AutoZone",
            "Description": "AI inventory prediction supporting 15K+ local jobs.",
            "Location": "East Memphis HQ",
            "Key AI/Energy Tie": "Retail-tech pilots balancing energy use with automation.",
            "Sample Coords (Lat, Lon)": "35.118, -89.970",
        },
        {
            "Entity": "St. Jude",
            "Description": "Biomedical AI diagnostics via PathAI with $100M+ research investment.",
            "Location": "Downtown Memphis",
            "Key AI/Energy Tie": "Health equity lens on compute-intensive research.",
            "Sample Coords (Lat, Lon)": "35.139, -90.019",
        },
        {
            "Entity": "Ford BlueOval",
            "Description": "AI-managed EV battery manufacturing complex ($5.6B).",
            "Location": "West Tennessee",
            "Key AI/Energy Tie": "Energy-efficient operations near Memphis powering EV supply chain.",
            "Sample Coords (Lat, Lon)": "35.250, -89.800",
        },
        {
            "Entity": "Preteckt",
            "Description": "Predictive fleet maintenance startup with sustainability focus.",
            "Location": "Memphis",
            "Key AI/Energy Tie": "AI reduces emissions for heavy-duty vehicles.",
            "Sample Coords (Lat, Lon)": "35.120, -90.000",
        },
        {
            "Entity": "Ursa Computing",
            "Description": "Quantum-AI security firm with regional research roots.",
            "Location": "Memphis",
            "Key AI/Energy Tie": "Collaborates with University of Memphis researchers on secure compute.",
            "Sample Coords (Lat, Lon)": "35.130, -90.010",
        },
        {
            "Entity": "Clear Function",
            "Description": "Enterprise AI for payments/security plus workforce training programs.",
            "Location": "Memphis",
            "Key AI/Energy Tie": "Custom ML deployments with local talent pipelines.",
            "Sample Coords (Lat, Lon)": "35.140, -90.020",
        },
        {
            "Entity": "Nvidia / Dell / Supermicro",
            "Description": "Hardware suppliers enabling the Colossus build; Dell expanding Memphis footprint.",
            "Location": "Memphis operations",
            "Key AI/Energy Tie": "Billions in infrastructure with grid strain and siting debates.",
            "Sample Coords (Lat, Lon)": "35.100, -90.030",
        },
    ]
    return pd.DataFrame(records)


def build_academia_df() -> pd.DataFrame:
    records = [
        {
            "Entity": "University of Memphis",
            "Description": "FedEx Institute of Technology anchors AI R&D; $1M new AI commitment.",
            "Location": "Central Memphis",
            "Key AI/Energy Tie": "xAI/TVA partners; ethics curriculum expansion.",
            "Sample Coords (Lat, Lon)": "35.119, -89.941",
        },
        {
            "Entity": "UTHSC",
            "Description": "UT Verse platform scaling AI for healthcare delivery.",
            "Location": "Downtown Memphis",
            "Key AI/Energy Tie": "Copilot-style tools with equity focus.",
            "Sample Coords (Lat, Lon)": "35.133, -90.021",
        },
        {
            "Entity": "Christian Brothers University",
            "Description": "AI engineering and startup collaboration hub.",
            "Location": "Midtown Memphis",
            "Key AI/Energy Tie": "Innovation lab with local founders.",
            "Sample Coords (Lat, Lon)": "35.158, -90.031",
        },
        {
            "Entity": "LeMoyne-Owen College",
            "Description": "HBCU advancing AI ethics and advocacy programming.",
            "Location": "South Memphis",
            "Key AI/Energy Tie": "NAACP-aligned workshops for community access.",
            "Sample Coords (Lat, Lon)": "35.096, -90.024",
        },
        {
            "Entity": "Rhodes College",
            "Description": "Data science minor integrated with urban equity research.",
            "Location": "Midtown Memphis",
            "Key AI/Energy Tie": "Partners with nonprofits on responsible tech.",
            "Sample Coords (Lat, Lon)": "35.163, -90.039",
        },
    ]
    return pd.DataFrame(records)


def build_government_df() -> pd.DataFrame:
    records = [
        {
            "Entity": "City of Memphis",
            "Description": "Permitting and Digital Delta policy coordination.",
            "Location": "Downtown",
            "Key AI/Energy Tie": "Equity audits alongside zoning reforms.",
            "Sample Coords (Lat, Lon)": "35.149, -90.049",
        },
        {
            "Entity": "Shelby County",
            "Description": "Data center zoning and impact funding strategies.",
            "Location": "Memphis",
            "Key AI/Energy Tie": "Economic development incentives for AI buildouts.",
            "Sample Coords (Lat, Lon)": "35.129, -90.049",
        },
        {
            "Entity": "MLGW",
            "Description": "Utility managing 20% demand spike with AI grid tools.",
            "Location": "Midtown",
            "Key AI/Energy Tie": "Powering Colossus while upgrading infrastructure.",
            "Sample Coords (Lat, Lon)": "35.135, -90.040",
        },
        {
            "Entity": "TVA",
            "Description": "Regional power provider coordinating xAI substation.",
            "Location": "Knoxville (Memphis ops)",
            "Key AI/Energy Tie": "Balancing gas assets with renewables push.",
            "Sample Coords (Lat, Lon)": "35.150, -90.050",
        },
        {
            "Entity": "Greater Memphis Chamber",
            "Description": "Digital Delta branding and supplier matchmaking.",
            "Location": "Downtown",
            "Key AI/Energy Tie": "xAI advocacy; 2025 Chamber of the Year honors.",
            "Sample Coords (Lat, Lon)": "35.138, -90.050",
        },
        {
            "Entity": "Entergy Arkansas",
            "Description": "Utility supporting Google data center expansion across the river.",
            "Location": "West Memphis",
            "Key AI/Energy Tie": "600MW solar build aligned with AI load.",
            "Sample Coords (Lat, Lon)": "35.147, -90.185",
        },
    ]
    return pd.DataFrame(records)


def build_community_df() -> pd.DataFrame:
    records = [
        {
            "Entity": "Memphis Community Against Pollution",
            "Description": "Environmental justice coalition tracking industrial pollution.",
            "Location": "Southwest Memphis",
            "Key AI/Energy Tie": "xAI turbine lawsuits with air monitoring demands.",
            "Sample Coords (Lat, Lon)": "35.080, -90.050",
        },
        {
            "Entity": "NAACP Memphis",
            "Description": "Civil rights organization advancing responsible tech guidelines.",
            "Location": "Downtown",
            "Key AI/Energy Tie": "Hosting 2025 data center equity summit.",
            "Sample Coords (Lat, Lon)": "35.130, -90.030",
        },
        {
            "Entity": "Memphis Technology Foundation",
            "Description": "Community tech group offering inclusive training.",
            "Location": "Citywide",
            "Key AI/Energy Tie": "Ethical AI upskilling and job access workshops.",
            "Sample Coords (Lat, Lon)": "35.140, -90.040",
        },
        {
            "Entity": "Southern Environmental Law Center",
            "Description": "Regional legal advocacy challenging fossil-tied data centers.",
            "Location": "Memphis",
            "Key AI/Energy Tie": "Litigation focused on xAI emissions.",
            "Sample Coords (Lat, Lon)": "35.120, -90.020",
        },
        {
            "Entity": "Moms Clean Air Force",
            "Description": "Grassroots group mobilizing against pollution in Boxtown.",
            "Location": "Boxtown / South Memphis",
            "Key AI/Energy Tie": "Publishes health impact reports on xAI buildout.",
            "Sample Coords (Lat, Lon)": "35.095, -90.030",
        },
    ]
    return pd.DataFrame(records)


def build_startups_df() -> pd.DataFrame:
    records = [
        {
            "Entity": "Diatech Diabetes",
            "Description": "Digital therapeutics startup delivering AI-driven diabetes management.",
            "Location": "Memphis",
            "Key AI/Energy Tie": "Health equity tools for community clinics.",
            "Sample Coords (Lat, Lon)": "35.110, -90.010",
        },
        {
            "Entity": "WHAI Robotics",
            "Description": "Robotics company focused on accessibility solutions.",
            "Location": "Memphis",
            "Key AI/Energy Tie": "University of Memphis collaboration on inclusive automation.",
            "Sample Coords (Lat, Lon)": "35.120, -90.000",
        },
        {
            "Entity": "MiCare Path",
            "Description": "Patient navigation platform using AI and nonprofit partnerships.",
            "Location": "Memphis",
            "Key AI/Energy Tie": "Supports care coordination for local hospitals.",
            "Sample Coords (Lat, Lon)": "35.130, -90.020",
        },
        {
            "Entity": "Bite Ninja",
            "Description": "AI-powered hospitality training solution.",
            "Location": "Memphis",
            "Key AI/Energy Tie": "Incorporates open-source tooling for restaurants.",
            "Sample Coords (Lat, Lon)": "35.140, -90.030",
        },
        {
            "Entity": "KALiiN",
            "Description": "Creative tech platform offering AI tools for filmmakers.",
            "Location": "Memphis",
            "Key AI/Energy Tie": "Promotes ethical content production.",
            "Sample Coords (Lat, Lon)": "35.150, -90.040",
        },
        {
            "Entity": "Otto JS",
            "Description": "Developer tooling startup emerging from local accelerator.",
            "Location": "Memphis",
            "Key AI/Energy Tie": "Open-source-focused AI development kits.",
            "Sample Coords (Lat, Lon)": "35.160, -90.050",
        },
    ]
    return pd.DataFrame(records)


def write_markdown(sections: dict[str, pd.DataFrame]) -> None:
    header = """# Digital Delta Map — MVP v1.0

A static snapshot of Memphis' emerging "Digital Delta" ecosystem, blending AI infrastructure momentum with community oversight. Tables are export-ready for Google Sheets or Notion, and coordinates prime the project for future mapping experiments.

**Total Entities Tracked:** {total}

## 1. Industry & Corporations
"""
    body_parts = [header.format(total=sum(len(df) for df in sections.values()))]

    industry_intro = (
        "Major investors driving AI infrastructure. Estimated $20B+ regional investment since 2024, "
        "with xAI leading expansion and equity debates in Boxtown."
    )
    body_parts.append(industry_intro + "\n\n" + dataframe_to_markdown(sections["industry"]))

    academia_intro = (
        "Workforce pipelines and research hubs. The University of Memphis leads the Digital Delta "
        "coalition, with AI enrollments up roughly 40% year over year."
    )
    body_parts.append("\n\n## 2. Academia & Research\n" + academia_intro + "\n\n" + dataframe_to_markdown(sections["academia"]))

    government_intro = (
        "Policy and infrastructure enablers. MLGW and TVA project a 20% demand spike with $80M in "
        "wastewater upgrades tied to the xAI buildout."
    )
    body_parts.append("\n\n## 3. Government & Infrastructure\n" + government_intro + "\n\n" + dataframe_to_markdown(sections["government"]))

    community_intro = (
        "Community voices for environmental justice and responsible AI. South Memphis groups lead "
        "opposition to unchecked industrial expansion amid Tennessee's highest asthma rates."
    )
    body_parts.append("\n\n## 4. Community & Advocacy\n" + community_intro + "\n\n" + dataframe_to_markdown(sections["community"]))

    startups_intro = (
        "Indie innovators building inclusive technology. More than 38 startups engage with the xAI "
        "supplier portal, with the sample below highlighting local impact plays."
    )
    body_parts.append("\n\n## 5. Startups & Creators\n" + startups_intro + "\n\n" + dataframe_to_markdown(sections["startups"]))

    chart_section = (
        "\n\n## Quick Visualization: Ecosystem Balance\n"
        "![Digital Delta Category Counts]({chart_path})\n\n"
        "A simple bar chart to showcase balanced coverage across the ecosystem. Export the tables "
        "to Sheets for deeper visualizations or geospatial plotting."
    ).format(chart_path=CHART_PATH.as_posix())
    body_parts.append(chart_section)

    launch_plan = (
        "\n\n## MVP Launch Plan\n"
        "1. **Share It:** Publish on Substack with the note ""First look at the Digital Delta Map—your feedback shapes v2!""\n"
        "2. **Gather Input:** Link to a Google Sheet and Form to crowdsource additions (e.g., new startups).\n"
        "3. **Tech Upgrades:** Scope a v1.1 Leaflet.js map using the coordinates above and highlight recent wins like Google’s solar expansion in West Memphis.\n"
        "4. **Ethics Check:** Keep impact flags current to maintain a balanced, transparent lens.\n"
    )
    body_parts.append(launch_plan)

    OUTPUT_PATH.write_text("".join(body_parts), encoding="utf-8")


def create_bar_chart(counts: dict[str, int]) -> None:
    ensure_artifacts_dir()
    categories = list(counts.keys())
    values = list(counts.values())
    max_value = max(values)

    width, height = 640, 400
    margin_left, margin_bottom, margin_top = 80, 60, 40
    chart_height = height - margin_bottom - margin_top
    bar_width = 60
    bar_gap = 30
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    svg_parts = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        f"<svg width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\" xmlns=\"http://www.w3.org/2000/svg\">",
        "<style>text{font-family:'Inter',sans-serif;font-size:14px;fill:#222}</style>",
        f"<text x=\"{width/2}\" y=\"{margin_top - 10}\" text-anchor=\"middle\" font-size=\"18\" font-weight=\"600\">Digital Delta Ecosystem Balance</text>",
    ]

    # Draw axes
    origin_x = margin_left
    origin_y = height - margin_bottom
    svg_parts.append(f"<line x1=\"{origin_x}\" y1=\"{margin_top}\" x2=\"{origin_x}\" y2=\"{origin_y}\" stroke=\"#555\" stroke-width=\"1\" />")
    svg_parts.append(f"<line x1=\"{origin_x}\" y1=\"{origin_y}\" x2=\"{width - margin_left / 2}\" y2=\"{origin_y}\" stroke=\"#555\" stroke-width=\"1\" />")
    svg_parts.append(f"<text x=\"{origin_x - 45}\" y=\"{margin_top + chart_height/2}\" transform=\"rotate(-90 {origin_x - 45},{margin_top + chart_height/2})\">Entity Count</text>")
    svg_parts.append(f"<text x=\"{width/2}\" y=\"{height - 15}\" text-anchor=\"middle\">Categories</text>")

    # Y-axis ticks
    for tick in range(0, max_value + 1):
        y = origin_y - (tick / max_value) * chart_height if max_value else origin_y
        svg_parts.append(f"<line x1=\"{origin_x - 5}\" y1=\"{y}\" x2=\"{origin_x}\" y2=\"{y}\" stroke=\"#777\" stroke-width=\"1\" />")
        svg_parts.append(f"<text x=\"{origin_x - 10}\" y=\"{y + 5}\" text-anchor=\"end\">{tick}</text>")

    # Bars
    for idx, (category, value) in enumerate(counts.items()):
        bar_height = (value / max_value) * chart_height if max_value else 0
        x = origin_x + bar_gap + idx * (bar_width + bar_gap)
        y = origin_y - bar_height
        color = colors[idx % len(colors)]
        svg_parts.append(
            f"<rect x=\"{x}\" y=\"{y}\" width=\"{bar_width}\" height=\"{bar_height}\" fill=\"{color}\" stroke=\"#222\" stroke-width=\"1\" />"
        )
        svg_parts.append(f"<text x=\"{x + bar_width / 2}\" y=\"{y - 8}\" text-anchor=\"middle\" font-size=\"12\">{value}</text>")
        svg_parts.append(
            f"<text x=\"{x + bar_width / 2}\" y=\"{origin_y + 20}\" text-anchor=\"middle\" font-size=\"12\">{category}</text>"
        )

    svg_parts.append("</svg>")

    CHART_PATH.write_text("\n".join(svg_parts), encoding="utf-8")


def main() -> None:
    sections = {
        "industry": build_industry_df(),
        "academia": build_academia_df(),
        "government": build_government_df(),
        "community": build_community_df(),
        "startups": build_startups_df(),
    }

    write_markdown(sections)

    counts = {"Industry": 9, "Academia": 5, "Government": 6, "Community": 5, "Startups": 6}
    create_bar_chart(counts)


if __name__ == "__main__":
    main()
