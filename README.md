# 🔍 AEO Diagnostic Tool

**Answer Engine Optimization** — Find out if your product shows up when customers ask GPT, Claude, and Gemini. Get a full report card + competitor breakdown.

## What it does

Paste any customer search query (e.g., *"best magnesium supplement for seniors"*) and your product name — the tool queries **GPT-4o-mini**, **Claude 3 Haiku**, and **Gemini 1.5 Flash** simultaneously and gives you:

- 📊 **Mention Rate** per AI model (how often your product is recommended)
- 🎓 **Grade A–F** for each model + overall score
- 📈 **Avg Rank Position** (#1–5)
- 🏆 **Competitor Landscape** chart — who AI mentions most for your query
- 💡 **Actionable Recommendations** to improve your AEO score

## APIs Used

| API | Purpose |
|-----|---------|
| OpenAI (GPT-4o-mini) | Simulates customer AI assistant queries |
| Anthropic (Claude 3 Haiku) | Second AI perspective |
| Google Gemini (Gemini 1.5 Flash) | Third AI perspective |

## Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/aeo-diagnostic
cd aeo-diagnostic
pip install -r requirements.txt
streamlit run app.py
```

Enter your API keys in the sidebar. They are never stored.

## Deploy on Streamlit Cloud

1. Push this repo to GitHub (public)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → select `app.py`
4. Click **Deploy**

## Built By

Prakash S — Pixii.ai Founding Engineer Project | May 2026
