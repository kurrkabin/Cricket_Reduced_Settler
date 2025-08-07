# app.py  –  Cricket Reduced-Matches Tool (T20 & ODI)  –  Aug 2025
import streamlit as st
import os, re, unicodedata

# ---------- optional house-rules text (for dev reference) ----------
rules_cache = {"text": ""}
rule_path = "/mnt/data/Cricket House Rules.rtf"
if os.path.exists(rule_path):
    with open(rule_path, "r", encoding="utf-8", errors="ignore") as f:
        rules_cache["text"] = f.read()

# ---------- constants ----------
FMT_MIN  = {"ODI": 40, "T20": 20}         # for 50 / 100-run props
RED_THR  = {"ODI": 5,  "T20": 3}          # overs lost that void limited-overs props
TOP_MIN  = {"ODI": 20, "T20": 6}          # min overs for Top Batter/Bowler

# ---------- market rules ----------
market_meta = [
    ("1st Over Total Runs",        lambda c: "STANDS" if (
        (c["stage"]=="before" and c["reduced"]>=1) or
        (c["stage"]!="before" and c["overs_done"]>=1)) else "VOID/CANCEL"),

    ("1st Wicket Method",          lambda c: "STANDS" if (
        c["stage"]=="before" and c["reduced"]>=1) else
        "Depends (need 1st-wicket info)"),

    ("1st Wicket Method (2 Way)",  lambda c: "STANDS" if (
        c["stage"]=="before" and c["reduced"]>=1) else
        "Depends (need 1st-wicket info)"),

    ("1st Over Runs Odd/Even",     lambda c: "STANDS" if (
        (c["stage"]=="before" and c["reduced"]>=1) or
        (c["stage"]!="before" and c["overs_done"]>=1)) else "VOID/CANCEL"),

    ("A Fifty Score in Match",     lambda c: "STANDS" if c["sched"]>=c["min_rule"] else "VOID/CANCEL"),
    ("A Hundred Score in Match",   lambda c: "STANDS" if c["sched"]>=c["min_rule"] else "VOID/CANCEL"),

    ("Batter to Score 50+ Runs",   lambda c: "STANDS" if (c["orig"]-c["reduced"])<c["red_thr"] else "VOID/CANCEL"),

    # ODI must be full 50 overs
    ("Most Match Sixes",           lambda c: "STANDS" if c["sched"]>=c["orig"] else "VOID/CANCEL"),
    ("Most Match Fours",           lambda c: "STANDS" if c["sched"]>=c["orig"] else "VOID/CANCEL"),

    ("Player of the Match",        lambda c: "STANDS (if declared)"),

    ("Top Bowler",                 lambda c: "STANDS" if c["sched"]>=c["top_min"] else "VOID/CANCEL"),
    ("Top Batter",                 lambda c: "STANDS" if c["sched"]>=c["top_min"] else "VOID/CANCEL"),

    ("Most Run Outs",              lambda c: "STANDS"),              # void only on total abandonment

    ("Fall of 1st Wicket",         lambda c: "STANDS"),

    ("Total Match Sixes",          lambda c: "STANDS" if (c["orig"]-c["reduced"])<c["red_thr"] else "VOID/CANCEL"),
    ("Total Match Fours",          lambda c: "STANDS" if (c["orig"]-c["reduced"])<c["red_thr"] else "VOID/CANCEL"),
    ("Total Run Outs",             lambda c: "STANDS" if (c["orig"]-c["reduced"])<c["red_thr"] else "VOID/CANCEL"),

    ("Tied Match",                 lambda c: "STANDS" if c["reduced"]>0 else "VOID/CANCEL"),

    ("Bowler Match Bet",           lambda c: "Depends (need bowler status)"),
    ("Batter Match Bet",           lambda c: "Depends (need batter status)"),

    ("Batter Total Runs",          lambda c: "STANDS" if c["reduced"]>=0.8*c["orig"] else "VOID/CANCEL"),

    ("Team Highest 1st 6 Overs",   lambda c: "STANDS" if c["sched"]>=6 else "VOID/CANCEL"),

    ("Highest Opening Partnership",lambda c: "STANDS" if (c["orig"]-c["reduced"])<c["red_thr"] else "VOID/CANCEL"),

    ("Highest Individual Score",   lambda c: "STANDS" if c["sched"]>=c["min_rule"] else "VOID/CANCEL"),
]

# ---------- Streamlit UI ----------
st.title("Cricket Reduced-Matches Settlement Tool")

fmt   = st.selectbox("Format", ["T20", "ODI"])
stage = st.selectbox("When reduced", ["before", "during1", "during2"],
                     format_func=lambda v: {"before":"Before start",
                                            "during1":"During 1st innings",
                                            "during2":"During 2nd innings"}[v])

red_to = st.number_input("Reduced to (overs scheduled)", min_value=0, step=1, value=0)
if stage=="before":
    overs_done = 0.0
else:
    overs_done = st.number_input("Overs done at reduction", min_value=0.0, step=0.1, value=0.0)

if st.button("Evaluate Markets"):
    orig  = 20 if fmt=="T20" else 50
    red   = red_to if red_to>0 else orig
    sched = red

    ctx = dict(stage=stage, overs_done=overs_done, reduced=red, orig=orig,
               sched=sched, min_rule=FMT_MIN[fmt], red_thr=RED_THR[fmt],
               top_min=TOP_MIN[fmt])

    st.markdown(f"**Status** — {fmt}: **{orig} → {red}** overs, stage = **{stage}**")

    results = []
    for i, (name, fn) in enumerate(market_meta, 1):
        status = fn(ctx)
        colour = "🟥" if "VOID" in status else "🟩" if "STANDS" in status else "🟧"
        results.append(f"{i:02}. {name}: {status} {colour}")

    st.markdown("\n\n".join(results))
