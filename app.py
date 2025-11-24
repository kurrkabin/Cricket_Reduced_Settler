# Cricket Reduced-Matches Settlement Tool — Streamlit Edition
# ODI/T20, before-start reductions UI
# Exactly 28 markets (after removing "Batter Milestone Runs —"), same order as provided.

import streamlit as st

# ---------- constants ----------
TOP_PCT        = 0.50         # Top markets need ≥50% of original overs
COMPLETE_PCT   = 0.80         # 80% threshold (match proxy; either-innings in text)
GOES_ON_MARKETS = {
    "Highest Opening Partnership",
    "Fall of 1st Wicket",
    "Batter Total Runs",
    "Batter to Score 50+ Runs",
    "Batter to Score 100+ Runs",
    "Batter Total Fours —",
    "Batter Total Sixes —",
}
# --- ADD ONLY: also treat " — Depends" variants as GOES-ON ---
GOES_ON_MARKETS |= {f"{m} — Depends" for m in list(GOES_ON_MARKETS)}

def _pct_rule(ctx, pct) -> str:
    return "STANDS" if ctx["reduced"] >= pct * ctx["orig"] else "VOID/CANCEL"

def _pct_or_goes_on(ctx, pct) -> str:
    # Proxy: if reduction keeps ≥80% we stand; otherwise VOID (UI does not capture UD signals)
    return "STANDS" if ctx["reduced"] >= pct * ctx["orig"] else "VOID/CANCEL"

# ---------- market rules (same order as your last code) ----------
market_meta = [

    # 1
    ("1st Over Total Runs",        lambda c:
        "STANDS" if (c["stage"]=="before" and c["reduced"]>=1) else "VOID/CANCEL"),

    # 2
    ("1st Wicket Method",          lambda c:
        "STANDS" if (c["stage"]=="before" and c["reduced"]>=1)
        else "Depends (need 1st-wicket info)"),

    # 3
    ("1st Wicket Method (2 Way)",  lambda c:
        "STANDS" if (c["stage"]=="before" and c["reduced"]>=1)
        else "Depends (need 1st-wicket info)"),

    # 4
    ("1st Over Runs Odd/Even",     lambda c:
        "STANDS" if (c["stage"]=="before" and c["reduced"]>=1) else "VOID/CANCEL"),

    # 5  (80% match threshold)
    ("A Fifty Score in Match",     lambda c:
        "STANDS" if c["reduced"] >= 0.80 * c["orig"] else "VOID/CANCEL"),

    # 6  (80% match threshold)
    ("A Hundred Score in Match",   lambda c:
        "STANDS" if c["reduced"] >= 0.80 * c["orig"] else "VOID/CANCEL"),

    # 7  (GOES-ON applies)
    ("Batter to Score 50+ Runs",   lambda c: _pct_or_goes_on(c, COMPLETE_PCT)),

    # 8  (GOES-ON applies)
    ("Batter to Score 100+ Runs",  lambda c: _pct_or_goes_on(c, COMPLETE_PCT)),

    # 9  (80% proxy for either-innings requirement)
    ("Most Match Sixes",           lambda c:
        "STANDS" if c["reduced"] >= 0.80 * c["orig"] else "VOID/CANCEL"),

    # 10 (80% proxy for either-innings requirement)
    ("Most Match Fours",           lambda c:
        "STANDS" if c["reduced"] >= 0.80 * c["orig"] else "VOID/CANCEL"),

    # 11
    ("Player of the Match",        lambda c: "STANDS (if declared)"),

    # 12
    ("Top Bowler",                 lambda c: _pct_rule(c, TOP_PCT)),

    # 13
    ("Top Batter",                 lambda c: _pct_rule(c, TOP_PCT)),

    # 14
    ("Most Run Outs",              lambda c: "STANDS" if c["reduced"] > 0 else "VOID/CANCEL"),

    # 15 (GOES-ON applies)
    ("Fall of 1st Wicket — Depends", lambda c: _pct_or_goes_on(c, COMPLETE_PCT)),

    # 16 (GOES-ON applies)
    ("Highest Opening Partnership", lambda c: _pct_or_goes_on(c, COMPLETE_PCT)),

    # 17 (80% match threshold)
    ("Total Match Sixes",          lambda c:
        "STANDS" if c["reduced"] >= 0.80 * c["orig"] else "VOID/CANCEL"),

    # 18 (80% match threshold)
    ("Total Match Fours",          lambda c:
        "STANDS" if c["reduced"] >= 0.80 * c["orig"] else "VOID/CANCEL"),

    # 19 (80% match threshold)
    ("Total Run Outs",             lambda c:
        "STANDS" if c["reduced"] >= 0.80 * c["orig"] else "VOID/CANCEL"),

    # 20
    ("Tied Match",                 lambda c: "STANDS" if c["reduced"] > 0 else "VOID/CANCEL"),

    # 21 (Bowler Match Bet — LOI: 80% proxy; no "Depends")
    ("Bowler Match Bet —",         lambda c:
        "STANDS" if c["reduced"] >= 0.80 * c["orig"] else "VOID/CANCEL"),

    # 22 (Batter Match Bet — LOI: 80% proxy; no "Depends")
    ("Batter Match Bet",           lambda c:
        "STANDS" if c["reduced"] >= 0.80 * c["orig"] else "VOID/CANCEL"),

    # 23 (GOES-ON applies)
    ("Batter Total Runs",          lambda c: _pct_or_goes_on(c, COMPLETE_PCT)),

    # 25 (GOES-ON applies; uses 80% proxy)
    ("Batter Total Fours —",       lambda c: _pct_or_goes_on(c, COMPLETE_PCT)),

    # 26 (GOES-ON applies; uses 80% proxy)
    ("Batter Total Sixes —",       lambda c: _pct_or_goes_on(c, COMPLETE_PCT)),

    # 27 (shortened label per your edit; 80% match threshold)
    ("Bowler Total Wickets —",     lambda c: _pct_rule(c, COMPLETE_PCT)),

    # 28 (segment depends on format: T20≥6 overs, ODI≥15 overs)
    ("Team Highest 1st 6/15 Overs —", lambda c:
        "STANDS" if (c["sched"] >= (6 if c["fmt"]=="T20" else 15)) else "VOID/CANCEL"),

    # 29 (label kept from previous; logic = 80% match threshold)
    ("Highest Individual Score —", lambda c:
        "STANDS" if c["reduced"] >= 0.80 * c["orig"] else "VOID/CANCEL"),
]

# ========================= Streamlit UI =========================

st.set_page_config(page_title="Cricket Reduced-Matches Settlement Tool", page_icon=":cricket_bat_and_ball:", layout="centered")

st.title("Cricket Reduced-Matches Settlement Tool")
st.caption("ODI/T20 • Reduction before start • Policy-aligned thresholds")

# Controls (kept readable and minimal, same semantics as your Colab UI)
col1, col2, col3 = st.columns([1,1,1])
with col1:
    fmt = st.selectbox("Format", ["T20", "ODI"], index=1)
with col2:
    stage = st.selectbox("When reduced", options=["Before start"], index=0)
with col3:
    red_to = st.number_input("Reduced to (overs)", min_value=0, step=1, value=40 if fmt=="ODI" else 20)

run = st.button("Evaluate Markets", type="primary")

# Compute & render
if run:
    orig = 20 if fmt == "T20" else 50
    red  = int(red_to) if red_to and red_to > 0 else orig

    ctx = dict(
        fmt=fmt,
        stage="before",   # fixed as per your spec
        reduced=red,
        orig=orig,
        sched=red,
    )

    st.markdown(
        f"### Status\n**{fmt}**: {orig} → {red} overs, reduction: {stage}"
    )
   # Replace your loop with this block (same semantics, uses Unicode emojis)
EMOJI = {"green": "🟩", "red": "🟥", "yellow": "🟨"}

lines = []
for i, (name, fn) in enumerate(market_meta, 1):
    status = fn(ctx)

    # GOES-ON masking (treat ' — Depends' variants as GOES-ON)
    if name in GOES_ON_MARKETS:
        status = "Depends — GOES-ON applies" if status == "VOID/CANCEL" else status

    # Determine color emoji from status text
    if "VOID" in status or "CANCEL" in status:
        colour = EMOJI["red"]
    elif "STANDS" in status:
        colour = EMOJI["green"]
    else:
        # anything else (Depends / Depends — GOES-ON applies / Depends (need...))
        colour = EMOJI["yellow"]

    lines.append(f"{i:02}. {name} — {status} {colour}")

st.markdown("\n\n".join(lines))

    

