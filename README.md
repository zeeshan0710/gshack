# 📈 StakeWise — Your AI Investing Coach

> **INFORMS × Zolve Hackathon 2026** | Built with Streamlit + OpenAI GPT-4o-mini

StakeWise is an AI-powered investing coach for everyday people — combining persona-driven financial education, gamified learning, and real-life risk scenario analysis.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 Investor Persona Quiz | 5 questions → 4 personality archetypes |
| 📖 Daily AI Lessons | GPT-4o-mini generates persona-matched 60-second lessons |
| 🧩 Knowledge Quizzes | Test understanding, earn XP |
| 💼 Portfolio Tracker | Add holdings, get AI commentary |
| 🧨 Risk Radar | Scenario-driven rebalancing — real-$ crash simulations |
| 💬 AI Tutor Chat | Ask anything, get plain-English answers |
| 🏅 Badges & XP | Gamified progression system |

---

## 🚀 Deploy to Streamlit Cloud (60 seconds)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial StakeWise commit"
   git remote add origin https://github.com/YOUR_USERNAME/stakewise.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click **New app** → connect your GitHub repo
   - Set **Main file path**: `stakewise_app.py`
   - Under **Advanced settings → Secrets**, add:
     ```toml
     OPENAI_API_KEY = "sk-your-key-here"
     ```
   - Click **Deploy** → live URL in ~60 seconds ✅

3. **Or run locally**
   ```bash
   pip install -r requirements.txt
   streamlit run stakewise_app.py
   ```
   Then enter your OpenAI API key in the sidebar.

---

## 🏗️ Tech Stack

- **Frontend**: Streamlit (pure Python, no HTML/CSS fights)
- **AI Engine**: OpenAI GPT-4o-mini (lessons, quizzes, risk advice, tutor)
- **Deployment**: Streamlit Cloud (free, connect GitHub → live URL)

---

## 👤 Investor Personas

| Persona | Risk | Focus |
|---|---|---|
| 🛡️ Cautious Keeper | Low | Capital preservation |
| 🏗️ Steady Builder | Medium-Low | Diversified long-term growth |
| 🚀 Growth Seeker | Medium-High | Growth stocks & ETFs |
| ⚡ Bold Adventurer | High | High-growth & emerging investments |

---

## 📋 Hackathon Deliverables

- ✅ **Working prototype** — this app
- ⬜ **Pitch deck** — 10 slides (coming next)
- ✅ **Scenario-Driven Rebalancing** — Risk Radar screen (live demo feature)
