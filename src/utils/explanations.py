"""
Explanation utilities: detect significant rises/dips in indicator time series
and attach plausible macro event context.

This is heuristic and NOT authoritative. Users should validate with domain sources.
"""
from typing import List, Dict
import pandas as pd

# Global macro events (year -> description)
GLOBAL_EVENTS = {
    2001: "Dot-com aftermath and 9/11 shocks affecting global growth and risk appetite",
    2003: "SARS outbreak impacting Asian travel and health indicators",
    2008: "Global financial crisis peak; credit contraction and demand slump",
    2009: "Post-crisis recession; lingering unemployment and GDP contraction",
    2011: "European sovereign debt concerns; uneven recovery",
    2014: "Oil price collapse impacting energy exporters and inflation",
    2015: "Chinese market volatility; adjustments in global trade flows",
    2016: "Brexit referendum uncertainty (mainly UK/EU); global policy shifts",
    2020: "COVID-19 pandemic shock: mobility restrictions, demand collapse, health system strain",
    2021: "Initial recovery phase; supply chain bottlenecks and rebound effects",
    2022: "Energy/commodity price surge and inflation spike (Ukraine conflict)",
    2023: "Post-pandemic normalization; disinflation trends and recovery consolidation"
}

# Indicator specific contextual augmentations keyed by indicator category fragments
INDICATOR_CONTEXT_RULES = [
    ("gdp", {2008: "Sharp downturn in output due to financial crisis", 2020: "Historic contraction from pandemic restrictions", 2022: "Commodity price dynamics and uneven recovery"}),
    ("inflation", {2020: "Low inflation amid demand shock", 2022: "Global inflation spike driven by energy & supply chains"}),
    ("unemployment", {2009: "Labor market deterioration post-crisis", 2020: "Sudden spike from lockdowns"}),
    ("co2", {2020: "Temporary emissions drop from reduced mobility & industry"}),
    ("energy", {2014: "Oil price collapse altering energy investment", 2022: "Energy price shock and policy shifts"}),
    ("internet", {2020: "Acceleration in digital adoption under lockdowns"}),
    ("health", {2020: "Healthcare strain and vaccination disruptions"}),
]

def _percent_changes(df: pd.DataFrame) -> pd.DataFrame:
    df_sorted = df.sort_values(['country', 'year']).copy()
    df_sorted['pct_change'] = df_sorted.groupby('country')['value'].pct_change() * 100
    return df_sorted

def _is_percentage_indicator(indicator_key: str) -> bool:
    return any(x in indicator_key for x in ["pct", "rate", "growth"])

def detect_extremes(
    df: pd.DataFrame,
    indicator_key: str,
    top_n: int = 3,
    min_abs_change_pct: float = 5.0,
) -> Dict[str, Dict[str, List[Dict]]]:
    """Detect top rises and dips per country.

    Returns structure: {country: {"rises": [...], "dips": [...]}}
    Each entry: {year, change_pct, value}
    """
    pc_df = _percent_changes(df)
    results = {}
    for country in pc_df['country'].unique():
        cdata = pc_df[pc_df['country'] == country]
        # Exclude first NaN change
        cvalid = cdata.dropna(subset=['pct_change'])
        # Apply significance threshold
        cvalid = cvalid[ cvalid['pct_change'].abs() >= float(min_abs_change_pct) ]
        if cvalid.empty:
            continue
        rises = cvalid.nlargest(top_n, 'pct_change')
        dips = cvalid.nsmallest(top_n, 'pct_change')
        results[country] = {
            'rises': [
                {
                    'year': int(r['year']),
                    'change_pct': float(r['pct_change']),
                    'value': float(r['value'])
                } for _, r in rises.iterrows()
            ],
            'dips': [
                {
                    'year': int(r['year']),
                    'change_pct': float(r['pct_change']),
                    'value': float(r['value'])
                } for _, r in dips.iterrows()
            ]
        }
    return results

def _augment_reason(indicator_key: str, year: int) -> List[str]:
    reasons = []
    if year in GLOBAL_EVENTS:
        reasons.append(GLOBAL_EVENTS[year])
    for fragment, mapping in INDICATOR_CONTEXT_RULES:
        if fragment in indicator_key and year in mapping:
            reasons.append(mapping[year])
    return reasons

def generate_explanations(
    df: pd.DataFrame,
    indicator_key: str,
    top_n: int = 3,
    min_abs_change_pct: float = 5.0,
) -> List[str]:
    """Generate formatted explanation strings for dips and rises.

    Output: list of markdown bullet strings.
    """
    if df.empty:
        return ["No data available to analyze dips/rises."]
    extremes = detect_extremes(df, indicator_key, top_n=top_n, min_abs_change_pct=min_abs_change_pct)
    lines: List[str] = []
    for country, vals in extremes.items():
        # Dips
        for dip in vals['dips']:
            reasons = _augment_reason(indicator_key, dip['year'])
            reason_str = "; ".join(reasons) if reasons else "Local factors or data volatility"
            lines.append(
                f"🔻 {country} {dip['year']}: {dip['change_pct']:.2f}% decline (value {dip['value']:.2f}) — {reason_str}"
            )
        # Rises
        for rise in vals['rises']:
            reasons = _augment_reason(indicator_key, rise['year'])
            reason_str = "; ".join(reasons) if reasons else "Potential recovery, structural growth, or base effects"
            lines.append(
                f"🔺 {country} {rise['year']}: {rise['change_pct']:.2f}% rise (value {rise['value']:.2f}) — {reason_str}"
            )
    if not lines:
        return []
    # Deduplicate identical lines (possible if small dataset)
    seen = set()
    deduped = []
    for l in lines:
        if l not in seen:
            deduped.append(l)
            seen.add(l)
    # Add disclaimer at end
    deduped.append("_Explanations are heuristic; verify with authoritative sources._")
    return deduped
