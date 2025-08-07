# app.py  –  Cricket Reduced-Matches Tool (T20 & ODI)  –  Aug 2025
# (rule logic refreshed 07 Aug 2025 per new DK house-rules)
import streamlit as st
import os, re, unicodedata

# ---------- optional house-rules text (for dev reference) ----------
rules_cache = {"text": ""}
rule_path = "/mnt/data/Cricket House Rules Aug 7th.rtf"
if os.path.exists(rule_path):
    with open(rule_path, "r", encoding="utf-8", errors="ignore") as f:
        rules_cache["text"] = f.read()

# ---------- constants ----------
FMT_MIN   = {"ODI": 40, "T20": 20}         # for 50 / 100-score markets
RED_THR   = {"ODI": 5,  "T20": 3}          # void if ≥ this many overs lost (team totals etc.)
TOP_PCT   = 0.50                           # Top Batter/Bowler – at least 50 % overs
COMPLETE_PCT = 0.80                        # 80 % completion rule (Batter 50+, Fall 1st Wkt…)

# ---------- helpers ----------
def _pct_rule(ctx, pct) -> str:
    """Return STANDS if scheduled overs ≥ pct * original scheduled overs."""
    return "STANDS" if ctx["reduced"] >= pct * ctx["orig"] else "VOID/CANCEL"

# ---------- market rules ----------
market_meta = [

    # ---------- over-based “instant” props ----------
    ("1st Over Total Runs",        lambda c:
        "STANDS" if ((c["stage"]=="before" and c["reduced"]>=1) or
                     (c["stage"]!="before" and c["overs_done"]>=1))
        else "VOID/CANCEL"),

    ("1st Wicket Method",          lambda c:
        "STANDS" if (c["stage"]=="before" and c["reduced"]>=1)
        else "Depends (need 1st-wicket info)"),

    ("1st Wicket Method (2 Way)",  lambda c:
        "STANDS" if (c["stage"]=="before" and c["reduced"]>=1)
        else "Depends (need 1st-wicket info)"),

    ("1st Over Runs Odd/Even",     lambda c:
        "STANDS" if ((c["stage"]=="before" and c["reduced"]>=1) or
                     (c["stage"]!="before" and c["overs_done"]>=1))
        else "VOID/CANCEL"),

    # ---------- 50 / 100 score in match ----------
    ("A Fifty Score in Match",     lambda c:
        "STANDS" if c["sched"] >= c["min_rule"] else "VOID/CANCEL"),
    ("A Hundred Score in Match",   lambda c:
        "STANDS" if c["sched"] >= c["min_rule"] else "VOID/CANCEL"),

    # ---------- named-batter milestones ----------
    ("Batter to Score 50+ Runs",   lambda c: _pct_rule(c, COMPLETE_PCT)),
    ("Batter to Score 100+ Runs",  lambda c: _pct_rule(c, COMPLETE_PCT)),

    # ---------- Most fours/sixes must have full overs ----------
    ("Most Match Sixes",           lambda c:
        "STANDS" if c["sched"] >= c["orig"] else "VOID/CANCEL"),
    ("Most Match Fours",           lambda c:
        "STANDS" if c["sched"] >= c["orig"] else "VOID/CANCEL"),

    ("Player of the Match",        lambda c: "STANDS (if declared)"),

    # ---------- Top Batter / Bowler (≥ 50 % overs rule) ----------
    ("Top Bowler",                 lambda c: _pct_rule(c, TOP_PCT)),
    ("Top Batter",                 lambda c: _pct_rule(c, TOP_PCT)),

    ("Most Run Outs",              lambda c: "STANDS"),   # only void on total abandonment

    # ---------- wicket & partnership props (80 % rule) ----------
    ("Fall of 1st Wicket",         lambda c: _pct_rule(c, COMPLETE_PCT)),
    ("Highest Opening Partnership",lambda c: _pct_rule(c, COMPLETE_PCT)),

    # ---------- totals void if overs lost ≥ threshold ----------
    ("Total Match Sixes",          lambda c:
        "STANDS" if (c["orig"] - c["reduced"]) < c["red_thr"] else "VOID/CANCEL"),
    ("Total Match Fours",          lambda c:
        "STANDS" if (c["orig"] - c["reduced"]) < c["red_thr"] else "VOID/CANCEL"),
    ("Total Run Outs",             lambda c:
        "STANDS" if (c["orig"] - c["reduced"]) < c["red_thr"] else "VOID/CANCEL"),

    ("Tied Match",                 lambda c: "STANDS" if c["reduced"] > 0 else "VOID/CANCEL"),

    ("Bowler Match Bet",           lambda c: "Depends (need bowler status)"),
    ("Batter Match Bet",           lambda c: "Depends (need batter status)"),

    # ---------- batter totals (80 % rule) ----------
    ("Batter Total Runs",          lambda c: _pct_rule(c, COMPLETE_PCT)),

    # ---------- powerplay / segment ----------
    ("Team Highest 1st 6 Overs",   lambda c:
        "STANDS" if c["sched"] >= 6 else "VOID/CANCEL"),

    # ---------- highest individual (still 40 / 20 rule) ----------
    ("Highest Individual Score",   lambda c:
        "STANDS" if c["sched"] >= c["min_rule"] else "VOID/CANCEL"),
]

# ---------- Streamlit UI ----------
st.title("Cricket Reduced-Matches Settlement Tool")

fmt = st.selectbox(
    "Format",
    ["T20", "ODI"],
    index=0,
)

stage = st.selectbox(
    "When reduced",
    ["before", "during1", "during2"],
    format_func=lambda v: {
        "before": "Before start",
        "during1": "During 1st innings",
        "during2": "During 2nd innings",
    }[v],
)

red_to = st.number_input("Reduced to (overs scheduled)", min_value=0, step=1, value=0)

overs_done = 0.0
if stage != "before":
    overs_done = st.number_input(
        "Overs done at reduction", min_value=0.0, step=0.1, value=0.0
    )

if st.button("Evaluate Markets"):
    orig = 20 if fmt == "T20" else 50
    red  = red_to if red_to > 0 else orig

    ctx = dict(
        stage=stage,
        overs_done=overs_done,
        reduced=red,
        orig=orig,
        sched=red,                    # current scheduled overs after reduction
        min_rule=FMT_MIN[fmt],
        red_thr=RED_THR[fmt],
        top_min=None,                 # kept for backward-compat (unused now)
    )

    st.markdown(f"**Status** — {fmt}: **{orig} → {red}** overs, stage = **{stage}**")

    for i, (name, fn) in enumerate(market_meta, 1):
        status = fn(ctx)
        colour = "🟥" if "VOID" in status else "🟩" if "STANDS" in status else "🟧"
        st.markdown(f"{i:02}. **{name}** — {status} {colour}")

