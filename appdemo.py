

import streamlit as st
from google import genai as google_genai
import re
import time
import random
from collections import defaultdict
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
 
st.set_page_config(page_title="AEO Diagnostic Tool", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>[data-testid="stMetricValue"]{font-size:1.6rem;font-weight:700;}.block-container{padding-top:1.5rem;}.stButton>button{border-radius:8px;font-weight:600;}</style>""", unsafe_allow_html=True)
 
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/search.png", width=60)
    st.title("AEO Diagnostic")
    st.caption("Answer Engine Optimization")
    st.divider()
    st.subheader("🔑 API Key")
    st.caption("Never stored. Cleared on refresh.")
    gemini_key = st.text_input("Gemini API Key", type="password", placeholder="AIza... (leave blank for demo)")
    demo_mode = st.checkbox("🎬 Run in Demo Mode", value=False, help="Shows realistic sample results without an API key")
    st.divider()
    st.subheader("⚙️ Settings")
    num_runs = st.slider("Queries per AI model", min_value=1, max_value=5, value=3)
    st.divider()
    st.caption("Built for Pixii.ai Founding Engineer challenge")
 
st.title("🔍 AEO Diagnostic Tool")
st.markdown("**Answer Engine Optimization** — Find out if your product shows up when customers ask Gemini 2.0 Flash, Gemini 1.5 Flash, and Gemini 1.5 Pro. Get a full report card + competitor breakdown.")
st.divider()
 
st.subheader("1️⃣  What are you selling?")
col1, col2 = st.columns(2)
with col1:
    query = st.text_input("Customer search query", placeholder="e.g., best magnesium supplement for seniors")
with col2:
    your_product = st.text_input("Your product / brand name", placeholder="e.g., Nature Made Magnesium")
 
run_btn = st.button("🚀  Run AEO Diagnostic", type="primary", use_container_width=True)
 
PROMPT = """You are a knowledgeable shopping assistant.
A customer asks: "{query}"
List your top 5 specific product or brand recommendations.
Format EXACTLY as a numbered list:
1. Brand Name Product — reason
2. ...
Use real, specific product and brand names. Be concise."""
 
DEMO_COMPETITORS = [
    "Optimum Nutrition Gold Standard Whey",
    "MyProtein Impact Whey",
    "GNC Pro Performance Whey",
    "Dymatize ISO100",
    "MuscleTech NitroTech",
    "BSN Syntha-6",
    "Isopure Zero Carb",
    "Garden of Life Sport",
]
 
def get_demo_responses(query, your_product, n):
    """Generate realistic demo responses"""
    responses = []
    for run in range(n):
        items = []
        mention_this_run = random.random() > 0.35
        comps = random.sample(DEMO_COMPETITORS, 4)
        all_products = ([your_product] + comps) if mention_this_run else (comps + [random.choice(DEMO_COMPETITORS)])
        random.shuffle(all_products)
        all_products = all_products[:5]
        reasons = ["highly rated by beginners","excellent amino acid profile","great value for money","most popular choice","clean ingredients","fast absorption","trusted brand","best in class"]
        for idx, p in enumerate(all_products, 1):
            items.append(f"{idx}. {p} — {random.choice(reasons)}")
        responses.append("\n".join(items))
    return responses
 
def call_gemini(prompt, key, model, n):
    client = google_genai.Client(api_key=key)
    out = []
    for _ in range(n):
        r = client.models.generate_content(model=model, contents=prompt)
        out.append(r.text)
        time.sleep(1.5)
    return out
 
def parse_list(text):
    items = []
    for line in text.splitlines():
        m = re.match(r"^\s*(\d+)[.)]\s+(.+)", line)
        if m:
            rank = int(m.group(1))
            content = re.sub(r"\*\*(.+?)\*\*", r"\1", m.group(2).strip())
            product = re.split(r"[:\-–—]", content)[0].strip()
            items.append((rank, product))
    return items
 
def analyze(responses, target):
    mentions, ranks, competitors = 0, [], defaultdict(int)
    for resp in responses:
        hit = False
        for rank, product in parse_list(resp):
            if target.lower() in product.lower():
                if not hit:
                    mentions += 1; ranks.append(rank); hit = True
            else:
                competitors[product] += 1
    rate = (mentions / len(responses) * 100) if responses else 0
    avg  = sum(ranks)/len(ranks) if ranks else None
    return rate, avg, ranks, dict(sorted(competitors.items(), key=lambda x: -x[1]))
 
def grade(rate):
    if rate >= 80: return "A","🟢","#00c851"
    if rate >= 60: return "B","🔵","#33b5e5"
    if rate >= 40: return "C","🟡","#ffbb33"
    if rate >= 20: return "D","🟠","#ff8800"
    return "F","🔴","#ff4444"
 
def show_results(analysis, scores, your_product, query, num_runs):
    st.subheader("3️⃣  AEO Report Card")
    st.caption(f'Query: **"{query}"**  |  Your Product: **{your_product}**')
    cols = st.columns(3)
    for idx, (name, data) in enumerate(analysis.items()):
        with cols[idx]:
            st.markdown(f"#### 🤖 {name}")
            if data:
                g, emoji, color = grade(data["rate"])
                st.metric("Mention Rate",    f"{data['rate']:.0f}%")
                st.metric("Grade",           f"{emoji} {g}")
                st.metric("Avg Rank",        f"#{data['avg_rank']:.1f} of 5" if data["avg_rank"] else "Not ranked")
                st.metric("Times Mentioned", f"{len(data['rank_list'])}/{num_runs}")
            else:
                st.error("Query failed — check API key")
 
    if scores:
        overall = sum(scores.values()) / len(scores)
        og, oe, oc = grade(overall)
        st.divider()
        c1, c2 = st.columns([1,2])
        with c1:
            st.metric("🎯 Overall AEO Score", f"{overall:.0f}%", f"Grade {og}")
            st.markdown(f"**{your_product}** is mentioned in **{overall:.0f}%** of all AI responses.")
        with c2:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=overall,
                title={"text":"Overall AEO Score","font":{"size":16}},
                number={"suffix":"%"},
                gauge={"axis":{"range":[0,100]},"bar":{"color":oc},
                       "steps":[{"range":[0,20],"color":"#ffe5e5"},{"range":[20,40],"color":"#fff0e0"},
                                 {"range":[40,60],"color":"#fffbe0"},{"range":[60,80],"color":"#e0f0ff"},
                                 {"range":[80,100],"color":"#e0ffe8"}],
                       "threshold":{"line":{"color":"black","width":3},"thickness":0.8,"value":overall}}))
            fig_gauge.update_layout(height=220, margin=dict(t=30,b=0,l=20,r=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
 
        st.divider()
        st.subheader("4️⃣  Score Breakdown by AI Model")
        df_scores = pd.DataFrame({"AI Model":list(scores.keys()),"Mention Rate (%)":[round(v,1) for v in scores.values()]})
        fig_bar = px.bar(df_scores, x="AI Model", y="Mention Rate (%)", color="Mention Rate (%)",
                         color_continuous_scale="Blues", text="Mention Rate (%)", range_y=[0,100],
                         title=f'"{your_product}" mention rate per AI model')
        fig_bar.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
        fig_bar.update_layout(showlegend=False, height=320)
        st.plotly_chart(fig_bar, use_container_width=True)
 
        st.divider()
        st.subheader("5️⃣  Competitor Landscape")
        all_comps  = defaultdict(int)
        your_total = 0
        for name, data in analysis.items():
            if data:
                for comp, cnt in data["comps"].items(): all_comps[comp] += cnt
                your_total += len(data["rank_list"])
        if all_comps:
            top10 = dict(sorted(all_comps.items(), key=lambda x: -x[1])[:10])
            df_comps = pd.DataFrame({
                "Brand / Product":[f"⭐ {your_product} (YOU)"]+list(top10.keys()),
                "Total Mentions":[your_total]+list(top10.values()),
                "Is You":[True]+[False]*len(top10)})
            fig_comp = px.bar(df_comps.sort_values("Total Mentions"), x="Total Mentions", y="Brand / Product",
                              orientation="h", color="Is You",
                              color_discrete_map={True:"#4CAF50",False:"#90caf9"},
                              title="Who AI mentions most for this query (all models combined)")
            fig_comp.update_layout(showlegend=False, height=420)
            st.plotly_chart(fig_comp, use_container_width=True)
            with st.expander("📋 Full competitor data table"):
                st.dataframe(df_comps.sort_values("Total Mentions",ascending=False).reset_index(drop=True), use_container_width=True)
 
        st.divider()
        st.subheader("6️⃣  Raw AI Responses")
        for name, data in analysis.items():
            if data:
                with st.expander(f"🤖 {name} — all {num_runs} responses"):
                    for i, resp in enumerate(data["responses"],1):
                        st.markdown(f"**Run {i}:**"); st.write(resp)
                        if i < len(data["responses"]): st.divider()
 
        st.divider()
        st.subheader("7️⃣  Recommendations")
        if overall < 20:
            st.error(f"**Grade F — '{your_product}' is invisible to AI models.**")
            rec = "- Publish authoritative content: blogs, product pages, comparison articles\n- Get listed on Amazon, G2, Trustpilot, Wirecutter\n- Issue press releases for AI training data\n- Get keyword-rich customer reviews"
        elif overall < 40:
            st.warning(f"**Grade D — '{your_product}' is rarely visible.**")
            rec = "- Create content targeting your exact query keyword\n- Build backlinks from niche authority sites\n- Create a Wikipedia-style page about your product\n- Submit to product directories"
        elif overall < 60:
            st.info(f"**Grade C — '{your_product}' appears occasionally.**")
            rec = "- Push for top-3 ranking\n- Get featured in 'best of' listicles\n- Increase brand mentions on Reddit and review platforms"
        elif overall < 80:
            st.info(f"**Grade B — '{your_product}' is regularly mentioned!**")
            rec = "- Identify which model mentions you least — focus there\n- Create content positioning you as #1\n- Monitor monthly as AI training data updates"
        else:
            st.success(f"**Grade A — '{your_product}' dominates AI search! 🎉**")
            rec = "- Run this diagnostic monthly to catch any drops\n- Expand to more query variations\n- Stay active on review platforms"
        st.markdown(rec)
    else:
        st.error("All models failed. Please check your Gemini API key and try again.")
 
    st.divider()
    st.caption("🔍 AEO Diagnostic Tool — Built by Prakash S | Pixii.ai Founding Engineer Project")
 
if run_btn:
    errors = []
    if not query.strip():        errors.append("Enter a search query.")
    if not your_product.strip(): errors.append("Enter your product/brand name.")
    if not demo_mode and not gemini_key: errors.append("Add your Gemini API key or enable Demo Mode.")
    if errors:
        for e in errors: st.error(e)
        st.stop()
 
    prompt   = PROMPT.format(query=query)
    analysis = {}
    scores   = {}
 
    st.subheader("2️⃣  Querying AI Models…")
    progress = st.progress(0, text="Starting…")
    status   = st.empty()
 
    ai_jobs = [
        ("Gemini 2.5 Flash",      "gemini-2.5-flash",      "🟢"),
        ("Gemini 2.5 Flash Lite", "gemini-2.5-flash-lite",  "🔵"),
        ("Gemini 2.5 Pro",      "gemini-2.5-pro",       "🟠"),
    ]
 
    for i, (name, model, emoji) in enumerate(ai_jobs):
        status.info(f"{emoji} Querying **{name}**… ({i+1}/3)")
        try:
            if demo_mode:
                time.sleep(0.8)
                responses = get_demo_responses(query, your_product, num_runs)
            else:
                responses = call_gemini(prompt, gemini_key, model, num_runs)
            rate, avg_rank, rank_list, comps = analyze(responses, your_product)
            analysis[name] = {"rate":rate,"avg_rank":avg_rank,"rank_list":rank_list,"comps":comps,"responses":responses}
            scores[name]   = rate
            st.success(f"✅ {name} — {num_runs} queries done")
        except Exception as ex:
            st.error(f"❌ {name} failed: {ex}")
            analysis[name] = None
        progress.progress((i+1)/3, text=f"{i+1}/3 models done")
 
    status.empty(); progress.empty()
    st.divider()
    show_results(analysis, scores, your_product, query, num_runs)