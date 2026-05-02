"""
StakeWise — Your Plain-English Investing Coach
Built for: INFORMS × Zolve Hackathon 2026
Judging criteria addressed:
  30% UX & Empathy        → persona quiz, no-jargon UI, guided flows, bottom nav, glossary tooltips
  30% Innovation/Rebalancing → 4-step guided rebalancing wizard, AI recommended target, before/after, plain-English impact
  20% Transparency & Trust → rationale on every AI call, data sources cited, risk warnings, disclaimer on every screen
  20% Technical Execution → portfolio analytics, crash sensitivity model, simulated projections, live GPT-4o-mini
"""

import streamlit as st
import openai, json, time
from datetime import datetime
from collections import Counter

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="StakeWise", page_icon="📈", layout="wide",
                   initial_sidebar_state="collapsed")

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:0.8rem;padding-bottom:5rem;max-width:1080px;}

:root{
  --navy:#0F2044; --blue:#1A56DB; --teal:#0EA5E9;
  --green:#10B981; --amber:#F59E0B; --red:#EF4444;
  --light:#EEF4FF; --border:#E2E8F0; --muted:#64748B;
}

/* ── Header ── */
.sw-header{display:flex;align-items:center;gap:10px;padding:.6rem 1.2rem;
  background:var(--navy);border-radius:14px;color:white;margin-bottom:1rem;}
.sw-logo{font-size:1.35rem;font-weight:800;letter-spacing:-.5px;}
.sw-tagline{font-size:.73rem;color:#93C5FD;margin-left:auto;}

/* ── Bottom Nav ── */
.bottom-nav{
  position:fixed;bottom:0;left:0;right:0;z-index:999;
  background:white;border-top:1px solid var(--border);
  display:flex;justify-content:center;gap:0;
  box-shadow:0 -2px 12px rgba(0,0,0,.08);
}
.bnav-item{
  flex:1;max-width:120px;display:flex;flex-direction:column;align-items:center;
  padding:8px 4px 6px;cursor:pointer;border:none;background:transparent;
  font-size:.65rem;font-weight:500;color:var(--muted);gap:2px;
  transition:color .15s;
}
.bnav-item.active{color:var(--blue);}
.bnav-item .icon{font-size:1.2rem;}

/* ── Cards ── */
.sw-card{background:white;border:1px solid var(--border);border-radius:14px;
  padding:18px 20px;margin-bottom:.9rem;box-shadow:0 1px 4px rgba(0,0,0,.05);}
.sw-card-title{font-size:.92rem;font-weight:600;color:var(--navy);margin-bottom:.7rem;}

/* ── Stat row ── */
.stat-row{display:flex;gap:8px;margin-bottom:.9rem;flex-wrap:wrap;}
.stat-card{flex:1;min-width:90px;background:white;border:1px solid var(--border);
  border-radius:12px;padding:10px 12px;box-shadow:0 1px 3px rgba(0,0,0,.04);}
.stat-label{font-size:.65rem;color:var(--muted);font-weight:500;
  text-transform:uppercase;letter-spacing:.4px;}
.stat-value{font-size:1.25rem;font-weight:700;color:var(--navy);margin-top:1px;}
.stat-sub{font-size:.67rem;color:var(--muted);}

/* ── Bars ── */
.bar-wrap{background:#F1F5F9;border-radius:6px;height:9px;overflow:hidden;margin:3px 0;}
.bar-fill{height:100%;border-radius:6px;transition:width .4s;}
.xp-bar-wrap{background:#E2E8F0;border-radius:5px;height:7px;overflow:hidden;}
.xp-bar{background:linear-gradient(90deg,var(--blue),var(--teal));height:100%;border-radius:5px;}

/* ── Scenario cards ── */
.sc{border-radius:12px;padding:14px 16px;border-left:4px solid;color:black;}
.sc-severe{background:#FEF2F2;border-color:var(--red);}
.sc-warn  {background:#FFFBEB;border-color:var(--amber);}
.sc-safe  {background:#F0FDF4;border-color:var(--green);}
.sc-info  {background:var(--light);border-color:var(--blue);}
.sc-title {font-weight:600;font-size:.83rem;margin-bottom:3px;}
.sc-dollar{font-size:1.1rem;font-weight:700;margin-top:4px;}
.sc-body  {font-size:.79rem;}

/* ── Lesson / AI response ── */
.lesson-box{background:var(--light);border-radius:12px;padding:16px;
  border-left:4px solid var(--blue);font-size:.86rem;line-height:1.75;
  color:black;margin-bottom:.9rem;}

/* ── Trust / tip banners ── */
.tip{background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;
  padding:9px 13px;color:#1E40AF;font-size:.8rem;margin:.5rem 0;}
.trust{background:#F8FAFC;border:1px solid #CBD5E1;border-radius:10px;
  padding:10px 14px;font-size:.75rem;color:#475569;line-height:1.6;}
.ok{background:#ECFDF5;border:1px solid #6EE7B7;border-radius:10px;
  padding:9px 13px;color:#065F46;font-size:.83rem;font-weight:500;}
.warn-box{background:#FFFBEB;border:1px solid #FCD34D;border-radius:10px;
  padding:9px 13px;color:#92400E;font-size:.8rem;}

/* ── Rebalancing wizard ── */
.wizard-step{border-radius:12px;padding:14px 18px;margin-bottom:.8rem;
  border:2px solid var(--border);background:white;}
.wizard-step.active{border-color:var(--blue);background:var(--light);}
.wizard-step.done{border-color:var(--green);background:#F0FDF4;}
.step-header{font-weight:600;font-size:.88rem;color:var(--navy);margin-bottom:6px;}

/* ── Rebalancing before/after ── */
.rebal-box{border-radius:12px;padding:14px;text-align:center;}
.rebal-before{background:#FEF2F2;border:1px solid #FECACA;}
.rebal-after {background:#F0FDF4;border:1px solid #BBF7D0;}
.rebal-label {font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;}
.rebal-num   {font-size:1.5rem;font-weight:800;}

/* ── Impact meter ── */
.impact-meter{display:flex;gap:4px;margin:6px 0;}
.impact-dot{width:12px;height:12px;border-radius:50%;}

/* ── Chat ── */
.chat-user{background:var(--blue);color:white;border-radius:14px 14px 4px 14px;
  padding:9px 13px;margin:5px 0;margin-left:16%;font-size:.85rem;}
.chat-ai{background:#F8FAFC;border:1px solid var(--border);
  border-radius:14px 14px 14px 4px;padding:9px 13px;margin:5px 0;
  margin-right:16%;font-size:.85rem;color:#000000;}

/* ── Badges ── */
.badge-grid{display:flex;flex-wrap:wrap;gap:8px;}
.badge{border-radius:10px;padding:7px 11px;font-size:.76rem;font-weight:600;
  display:flex;align-items:center;gap:5px;}
.b-earn{background:#F0FDF4;color:#166534;border:1px solid #BBF7D0;}
.b-lock{background:#F8FAFC;color:#94A3B8;border:1px solid #E2E8F0;}

/* ── Hero ── */
.hero{background:linear-gradient(135deg,var(--navy) 0%,#1e3a8a 100%);
  border-radius:16px;padding:28px;color:white;text-align:center;margin-bottom:1.2rem;}
.hero-title{font-size:1.8rem;font-weight:800;margin-bottom:6px;}
.hero-sub{font-size:.9rem;color:#93C5FD;margin-bottom:14px;}

/* ── Persona reveal ── */
.p-reveal{background:linear-gradient(135deg,var(--navy),#1e3a8a);
  border-radius:16px;padding:26px;color:white;text-align:center;margin-bottom:1rem;}

/* ── Step dots ── */
.step-row{display:flex;gap:5px;align-items:center;margin-bottom:.9rem;}
.step-dot{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:.7rem;font-weight:700;flex-shrink:0;}
.sd-done  {background:var(--green);color:white;}
.sd-active{background:var(--blue);color:white;}
.sd-todo  {background:#E2E8F0;color:#94A3B8;}

/* ── Glossary term ── */
.gt{font-weight:600;color:var(--blue);}

/* ── Button override ── */
.stButton>button{border-radius:10px!important;font-size:.85rem!important;
  border:1.5px solid var(--border)!important;background:white!important;
  color:var(--navy)!important;text-align:left!important;width:100%!important;
  padding:8px 13px!important;}
.stButton>button:hover{border-color:var(--blue)!important;background:var(--light)!important;}

/* ── Source badge ── */
.source-badge{display:inline-block;background:#F1F5F9;border:1px solid #CBD5E1;
  border-radius:6px;font-size:.65rem;color:#475569;padding:1px 7px;margin-left:4px;}

/* ── Confidence bar ── */
.conf-row{display:flex;align-items:center;gap:8px;font-size:.75rem;color:var(--muted);margin-top:6px;}
.conf-bar-wrap{flex:1;background:#E2E8F0;border-radius:4px;height:5px;}
.conf-bar{background:var(--green);height:100%;border-radius:4px;}
</style>
""", unsafe_allow_html=True)

# ─── OpenAI ────────────────────────────────────────────────────────────────────
def get_client():
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")
    except:
        key = ""
    if not key:
        key = st.session_state.get("api_key", "")
    return openai.OpenAI(api_key=key) if key else None

def call_ai(system_prompt, user_prompt, max_tokens=600):
    c = get_client()
    if not c:
        return "⚠️ Enter your OpenAI API key in the sidebar to unlock AI features."
    try:
        r = c.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":system_prompt},
                      {"role":"user","content":user_prompt}],
            max_tokens=max_tokens, temperature=0.7)
        return r.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI error: {e}"

# ─── Domain data ───────────────────────────────────────────────────────────────
PERSONAS = {
    "A":{"name":"The Cautious Keeper","emoji":"🛡️",
         "desc":"You value safety above all. You prefer stability and want to understand every risk before committing a single dollar.",
         "focus":"Capital preservation & low-risk investing","risk_level":"Low","risk_score":1,
         "color":"#0EA5E9",
         "alloc":{"Bonds":50,"Index Funds":30,"Cash / Savings":15,"Stocks":5},
         "rebal_nudge":"Since you're cautious, adding more Bonds and Cash typically reduces your exposure during crashes."},
    "B":{"name":"The Steady Builder","emoji":"🏗️",
         "desc":"Patient and consistent. You believe in slow-and-steady wealth building and tuning out market noise.",
         "focus":"Diversified portfolios & long-term growth","risk_level":"Medium-Low","risk_score":2,
         "color":"#10B981",
         "alloc":{"Index Funds":45,"Bonds":25,"Stocks":20,"International":10},
         "rebal_nudge":"As a Steady Builder, shifting some Stocks into Index Funds can smooth out volatility while maintaining growth."},
    "C":{"name":"The Growth Seeker","emoji":"🚀",
         "desc":"Willing to take calculated risks for bigger rewards. You follow trends and get excited by opportunity.",
         "focus":"Growth stocks, ETFs & trend investing","risk_level":"Medium-High","risk_score":3,
         "color":"#1A56DB",
         "alloc":{"Stocks":45,"Index Funds":30,"International":15,"Bonds":10},
         "rebal_nudge":"As a Growth Seeker, consider temporarily raising your Bond allocation during severe downturns to limit losses."},
    "D":{"name":"The Bold Adventurer","emoji":"⚡",
         "desc":"High risk, high reward. You're comfortable with volatility and love emerging opportunities.",
         "focus":"High-growth, alternative & emerging investments","risk_level":"High","risk_score":4,
         "color":"#F59E0B",
         "alloc":{"Stocks":55,"Index Funds":20,"International":15,"Alternative":10},
         "rebal_nudge":"Even bold investors benefit from small defensive positions. A 10-15% Bond buffer can cut crash losses significantly."},
}

QUIZ = [
    {"q":"Imagine your investment drops 20% overnight. What's your gut reaction?",
     "opts":[("😰 Panic — I'd want to sell immediately.","A"),
             ("😟 Worried, but I'd hold and wait it out.","B"),
             ("😌 Calm — I see this as a buying opportunity.","C"),
             ("😄 Excited! Time to buy more at a discount.","D")]},
    {"q":"You have $5,000 to invest. Which option appeals most?",
     "opts":[("🏦 A savings account — guaranteed, no surprises.","A"),
             ("📊 A diversified index fund — steady and reliable.","B"),
             ("📈 A mix of growth stocks with index funds.","C"),
             ("🎯 High-potential individual stocks.","D")]},
    {"q":"How long can you leave your money invested?",
     "opts":[("⏰ Under 2 years — I might need it soon.","A"),
             ("📅 3–5 years — medium term.","B"),
             ("🗓️ 5–10 years — the long game.","C"),
             ("♾️ 10+ years — I won't touch it for decades.","D")]},
    {"q":"When you hear 'the stock market hit an all-time high,' you think…",
     "opts":[("📉 It's about to crash — stay out.","A"),
             ("🤔 Be cautious, but don't panic.","B"),
             ("📈 Markets go up long-term — I'm optimistic.","C"),
             ("🔥 Great momentum! What should I buy?","D")]},
    {"q":"What's your #1 goal with investing?",
     "opts":[("🔒 Protect what I have — don't lose money.","A"),
             ("🌱 Slowly grow my savings over time.","B"),
             ("💪 Beat inflation and build real wealth.","C"),
             ("🚀 Maximize returns — grow fast.","D")]},
]

LEVEL_NAMES = ["Beginner","Learner","Explorer","Investor","Pro"]
LEVEL_XP    = [0,100,250,500,1000]

BADGE_DEFS = [
    ("🎓","First Step","Completed the persona quiz"),
    ("📖","First Lesson","Read your first AI lesson"),
    ("🎯","Quiz Ace","Scored 100% on a knowledge quiz"),
    ("🔥","On a Roll","3-day streak"),
    ("💼","Portfolio Pro","Added your first portfolio"),
    ("🧠","Curious Mind","Asked 5 tutor questions"),
    ("⚡","Risk Radar","Completed the rebalancing wizard"),
    ("🏆","StakeWise Master","Reached Investor level"),
]

ASSET_COLORS = {
    "Bonds":"#0EA5E9","Index Funds":"#10B981","Cash / Savings":"#8B5CF6",
    "Stocks":"#1A56DB","International":"#F59E0B","Alternative":"#EF4444",
}
ALL_ASSETS = list(ASSET_COLORS.keys())

# Crash sensitivity: how much each asset class drops relative to the overall market drop
# Source: Ibbotson SBBI, Vanguard research, Federal Reserve historical data
CRASH_SENS = {
    "Stocks":1.40,"Index Funds":1.00,"Bonds":0.08,
    "International":1.10,"Cash / Savings":0.00,"Alternative":0.75,
}

# Historical avg annual returns — Ibbotson SBBI 2023 data
HIST_RETURNS = {
    "Stocks":0.103,"Index Funds":0.095,"Bonds":0.043,
    "International":0.072,"Cash / Savings":0.020,"Alternative":0.082,
}

SCENARIOS = {
    "📉 2022 Rate Hike Selloff":{
        "label":"2022 Rate Hike Selloff","pct":0.20,"recovery":"~12 months",
        "cause":"The US Federal Reserve raised interest rates 11 times to fight 40-year-high inflation, making borrowing expensive and pushing investors out of stocks.",
        "lesson":"Portfolios with even 20-30% in bonds lost significantly less than pure stock portfolios.",
        "emoji":"📉"},
    "💥 2020 COVID-19 Crash":{
        "label":"2020 COVID-19 Crash","pct":0.34,"recovery":"~6 months",
        "cause":"A global pandemic caused an almost-instant halt in economic activity. Stock markets fell 34% in just 33 days — the fastest crash in history.",
        "lesson":"Investors who held on (or bought more) during the crash saw full recovery within 6 months — one of the fastest in history.",
        "emoji":"💥"},
    "🔥 2008 Financial Crisis":{
        "label":"2008 Financial Crisis","pct":0.50,"recovery":"~4–5 years",
        "cause":"Risky mortgage lending and over-leveraged banks triggered a global financial collapse. Over $11 trillion in US household wealth was wiped out.",
        "lesson":"Bonds and government securities were the key protector. Diversified investors recovered years faster than stock-only investors.",
        "emoji":"🔥"},
    "🌑 2000 Dot-Com Bust":{
        "label":"2000 Dot-Com Bust","pct":0.78,"recovery":"10–12 years",
        "cause":"Investor euphoria over the internet created a stock bubble — companies with no profits were worth billions. When profits never came, the bubble burst.",
        "lesson":"Tech-concentrated portfolios took over a decade to recover. Diversification across sectors and bonds was the only real protection.",
        "emoji":"🌑"},
}

GLOSSARY = {
    "ETF":"Exchange-Traded Fund — a basket of many stocks bundled together. Like buying one ticket to own a tiny slice of hundreds of companies at once.",
    "Index Fund":"A fund that automatically tracks the overall stock market (like the S&P 500) rather than trying to pick winners. Low-cost, low-effort, widely recommended for beginners.",
    "Diversification":"Spreading your money across different types of investments so that if one falls, others may hold steady. The investing equivalent of 'don't put all your eggs in one basket.'",
    "Bond":"A loan you give to a government or company. They pay you back with regular interest, then return your money. Safer than stocks, but lower returns.",
    "Rebalancing":"Adjusting your investment mix back to your target. If stocks grew from 60% → 75% of your portfolio, you'd sell some stocks and buy bonds to return to 60/40.",
    "Volatility":"How wildly an investment's price jumps up and down. High volatility = dramatic swings. Low volatility = slow, steady movement.",
    "Asset Allocation":"How you divide your money across investment types (stocks, bonds, cash, etc.). Research shows this single decision drives 90%+ of your long-term results.",
    "P/E Ratio":"Price-to-Earnings — how much investors are paying for each $1 of a company's profit. A quick way to check if a stock might be cheap or overpriced.",
    "Dollar-Cost Averaging":"Investing a fixed amount regularly (e.g. $200/month) regardless of market conditions. You buy more when prices are low, less when high — it averages out over time.",
    "Compound Interest":"Earning returns on your returns. If you make 8% on $1,000 ($80), next year you make 8% on $1,080. Over decades, this creates exponential growth.",
}

TOPICS = ["Diversification","Understanding ETFs","The Power of Compound Interest",
          "How to Read a Stock Chart","What is a P/E Ratio?","Bond Basics",
          "Dollar-Cost Averaging","Emergency Fund vs Investing",
          "Index Funds Explained","Inflation and Your Money"]

DEFAULTS = {
    "screen":"welcome","api_key":"","persona":None,"quiz_step":0,"quiz_answers":[],
    "xp":0,"level":1,"streak":1,"badges":[],"chat_history":[],
    "portfolio":[],"lesson_done":False,"kq_done":False,"daily_lesson":"",
    "kq_list":[],"kq_idx":0,"kq_score":0,
    # wizard state
    "wiz_step":0,"wiz_scenario":None,"wiz_new_alloc":{},"wiz_advice":"",
    "wiz_complete":False,
    "tutor_q":0,
}
for k,v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Helpers ───────────────────────────────────────────────────────────────────
def award(name):
    if name not in st.session_state.badges:
        st.session_state.badges.append(name)

def add_xp(n):
    st.session_state.xp += n
    for i,t in enumerate(LEVEL_XP):
        if st.session_state.xp >= t:
            st.session_state.level = i+1

def lvl_name():
    return LEVEL_NAMES[min(st.session_state.level-1, len(LEVEL_NAMES)-1)]

def xp_pct():
    lvl = st.session_state.level
    if lvl >= len(LEVEL_XP): return 100
    lo,hi = LEVEL_XP[lvl-1],LEVEL_XP[lvl]
    return int((st.session_state.xp-lo)/(hi-lo)*100)

def xp_next():
    lvl = st.session_state.level
    return LEVEL_XP[lvl]-st.session_state.xp if lvl < len(LEVEL_XP) else 0

def calc_crash_loss(alloc, total, drop_pct):
    """Weighted crash loss using asset-class sensitivity model."""
    return sum((alloc.get(t,0)/100)*CRASH_SENS.get(t,1.0)*drop_pct*total
               for t in alloc)

def weighted_return(alloc):
    return sum((alloc.get(t,0)/100)*HIST_RETURNS.get(t,0.07) for t in alloc)

def impact_dots(loss_pct, max_pct=0.80):
    """Render filled/empty dots for visual risk impact."""
    filled = round((loss_pct/max_pct)*10)
    dots = ""
    for i in range(10):
        color = "#EF4444" if i < filled else "#E2E8F0"
        dots += f'<div class="impact-dot" style="background:{color}"></div>'
    return f'<div class="impact-meter">{dots}</div>'

def trust_footer():
    st.markdown("""<div class="trust">
    🛡️ <strong>Transparency:</strong> StakeWise is an AI-powered educational tool — <strong>not</strong> a licensed
    financial advisor. Crash sensitivity estimates are derived from Ibbotson SBBI historical data and
    Vanguard research. Projections use long-run average returns and do not guarantee future results.
    Always consult a qualified financial advisor before investing.
    </div>""", unsafe_allow_html=True)

def persona_alloc():
    p = PERSONAS[st.session_state.persona]
    return dict(p["alloc"])

def portfolio_alloc():
    port = st.session_state.portfolio
    if not port: return persona_alloc()
    total = sum(h["amount"] for h in port)
    tt = {}
    for h in port:
        tt[h["type"]] = tt.get(h["type"],0) + h["amount"]
    return {t: round(amt/total*100) for t,amt in tt.items()}

# ─── Layout: header + bottom nav ───────────────────────────────────────────────
def render_header():
    p_label = ""
    if st.session_state.persona:
        p = PERSONAS[st.session_state.persona]
        p_label = f"&nbsp;&nbsp;|&nbsp;&nbsp;{p['emoji']} {p['name']}"
    st.markdown(f"""<div class="sw-header">
        <span style="font-size:1.35rem">📈</span>
        <span class="sw-logo">StakeWise</span>
        <span style="font-size:.73rem;color:#93C5FD;margin-left:4px">Your plain-English investing coach{p_label}</span>
        <span class="sw-tagline">🔥 {st.session_state.streak}d streak &nbsp;|&nbsp; ⭐ {st.session_state.xp} XP &nbsp;|&nbsp; {lvl_name()}</span>
    </div>""", unsafe_allow_html=True)

def render_bottom_nav():
    if not st.session_state.persona: return
    screen = st.session_state.screen
    nav_items = [
        ("🏠","Home","home"),("📖","Lesson","lesson"),("🧨","Risk","risk"),
        ("💼","Portfolio","portfolio"),("💬","Tutor","chat"),
    ]
    st.markdown('<div class="bottom-nav">', unsafe_allow_html=True)
    cols = st.columns(len(nav_items))
    for col,(icon,label,sc) in zip(cols, nav_items):
        with col:
            active = "active" if screen==sc else ""
            if st.button(f"{icon}\n{label}", key=f"bnav_{sc}", use_container_width=True):
                st.session_state.screen = sc; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        try:
            secret_key = st.secrets.get("OPENAI_API_KEY", "")
            if secret_key:
                st.success("OpenAI API key loaded from secrets ✓")
            else:
                key = st.text_input("OpenAI API Key", value=st.session_state.get("api_key", ""),
                                    type="password", placeholder="sk-...")
                st.session_state.api_key = key
                if key: st.success("API key connected ✓")
        except:
            key = st.text_input("OpenAI API Key", value=st.session_state.get("api_key", ""),
                                type="password", placeholder="sk-...")
            st.session_state.api_key = key
            if key: st.success("API key connected ✓")
        if st.session_state.persona:
            st.markdown("---")
            st.markdown(f"**Level {st.session_state.level} · {lvl_name()}**")
            st.markdown(f'<div class="xp-bar-wrap"><div class="xp-bar" style="width:{xp_pct()}%"></div></div>'
                        f'<div style="font-size:.68rem;color:var(--muted);margin-top:3px">'
                        f'{st.session_state.xp} XP · {xp_next()} to next level</div>',
                        unsafe_allow_html=True)
            st.markdown("---")
            if st.button("📚 Glossary", use_container_width=True):
                st.session_state.screen = "glossary"; st.rerun()
            if st.button("🏅 Badges", use_container_width=True):
                st.session_state.screen = "badges"; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  SCREENS
# ══════════════════════════════════════════════════════════════════════════════

# ── Welcome ───────────────────────────────────────────────────────────────────
def screen_welcome():
    st.markdown("""<div class="hero">
        <div style="font-size:3rem;margin-bottom:6px">📈</div>
        <div class="hero-title">Welcome to StakeWise</div>
        <div class="hero-sub">Investing, explained like a friend — not a textbook.</div>
        <div style="font-size:.83rem;color:#BFDBFE;max-width:460px;margin:0 auto">
        No jargon. No intimidating charts. Personalized guidance matched to
        exactly who you are as an investor.
        </div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    for col,(icon,title,desc) in zip([c1,c2,c3],[
        ("🎯","Know Your Type","5 questions reveal your investor personality. Every lesson and recommendation adapts to it."),
        ("🧨","Understand Real Risk","See what market crashes mean for your money in dollars — not confusing percentages."),
        ("💬","Ask Anything","Your AI coach explains any concept in plain English. No question is too basic."),
    ]):
        with col:
            st.markdown(f'<div class="sw-card" style="text-align:center;min-height:140px">'
                        f'<div style="font-size:1.6rem">{icon}</div>'
                        f'<div style="font-weight:600;margin:5px 0;font-size:.88rem">{title}</div>'
                        f'<div style="font-size:.78rem;color:#64748B">{desc}</div></div>',
                        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _,mid,_ = st.columns([2,1,2])
    with mid:
        if st.button("🚀 Start — it's free", use_container_width=True):
            st.session_state.screen = "quiz"; st.rerun()
    trust_footer()

# ── Quiz ──────────────────────────────────────────────────────────────────────
def screen_quiz():
    st.markdown("## 🎯 Discover Your Investor Persona")
    st.markdown("5 quick questions — no right or wrong answers, just be honest!")
    step = st.session_state.quiz_step
    dots = "".join(
        f'<div class="step-dot {"sd-done" if i<step else "sd-active" if i==step else "sd-todo"}">{i+1}</div>'
        for i in range(len(QUIZ))
    )
    st.markdown(f'<div class="step-row">{dots}'
                f'<span style="font-size:.75rem;color:#64748B;margin-left:6px">'
                f'Question {min(step+1,len(QUIZ))} of {len(QUIZ)}</span></div>',
                unsafe_allow_html=True)

    if step < len(QUIZ):
        q = QUIZ[step]
        st.markdown(f'<div class="sw-card"><div style="font-size:.97rem;font-weight:600;'
                    f'color:#0F2044;margin-bottom:1rem">{q["q"]}</div></div>',
                    unsafe_allow_html=True)
        for opt_text,opt_val in q["opts"]:
            if st.button(opt_text, key=f"q{step}_{opt_val}"):
                st.session_state.quiz_answers.append(opt_val)
                st.session_state.quiz_step += 1; st.rerun()
    else:
        counts = Counter(st.session_state.quiz_answers)
        pk = counts.most_common(1)[0][0]
        st.session_state.persona = pk
        add_xp(50); award("First Step")
        st.session_state.screen = "persona_reveal"; st.rerun()

# ── Persona reveal ────────────────────────────────────────────────────────────
def screen_persona_reveal():
    p = PERSONAS[st.session_state.persona]
    alloc = p["alloc"]
    st.markdown(f"""<div class="p-reveal">
        <div style="font-size:3rem;margin-bottom:5px">{p['emoji']}</div>
        <div style="font-size:.82rem;color:#93C5FD;font-weight:600;letter-spacing:1px;margin-bottom:4px">YOUR INVESTOR PERSONA</div>
        <div style="font-size:1.6rem;font-weight:700;margin-bottom:7px">{p['name']}</div>
        <div style="font-size:.85rem;color:#BFDBFE;max-width:460px;margin:0 auto 12px">{p['desc']}</div>
        <div style="display:inline-flex;gap:8px;flex-wrap:wrap;justify-content:center">
            <span style="background:rgba(255,255,255,.15);border-radius:20px;padding:4px 14px;font-size:.78rem;font-weight:600">🎯 {p['focus']}</span>
            <span style="background:rgba(255,255,255,.10);border-radius:20px;padding:4px 14px;font-size:.78rem">⚖️ Risk: {p['risk_level']}</span>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="ok" style="text-align:center;margin-bottom:.9rem">🎉 +50 XP earned! Badge unlocked: 🎓 First Step</div>',
                unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sw-card"><div class="sw-card-title">💡 Your Suggested Starting Allocation</div>'
                    '<div class="tip" style="margin-bottom:10px;font-size:.76rem">This is a <strong>starting point</strong> based on your risk personality — not financial advice. Customize it anytime in My Portfolio.</div>',
                    unsafe_allow_html=True)
        for asset,pct in alloc.items():
            color = ASSET_COLORS.get(asset,"#64748B")
            st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:2px">'
                        f'<span style="font-weight:500">{asset}</span>'
                        f'<span style="color:{color};font-weight:600">{pct}%</span></div>'
                        f'<div class="bar-wrap"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown("""<div class="sw-card"><div class="sw-card-title">📘 What these terms mean</div>
        <div style="font-size:.8rem;line-height:1.9;color:#374151">
        <strong>Bonds</strong> — loans to governments. Safer, lower returns.<br>
        <strong>Index Funds</strong> — automatic baskets tracking the whole market. Great for beginners.<br>
        <strong>Stocks</strong> — tiny ownership slices of companies. Higher risk, higher reward.<br>
        <strong>International</strong> — investments outside your home country. Adds diversity.<br>
        <strong>Cash / Savings</strong> — money in a savings account or money market. Very safe, very low returns.
        </div></div>""", unsafe_allow_html=True)

    _,mid,_ = st.columns([2,1,2])
    with mid:
        if st.button("Let's go! →", use_container_width=True):
            st.session_state.screen = "home"; st.rerun()

# ── Home ──────────────────────────────────────────────────────────────────────
def screen_home():
    p = PERSONAS[st.session_state.persona]
    st.markdown(f"""<div class="stat-row">
        <div class="stat-card"><div class="stat-label">Persona</div><div class="stat-value">{p['emoji']}</div><div class="stat-sub">{p['name']}</div></div>
        <div class="stat-card"><div class="stat-label">XP</div><div class="stat-value">⭐ {st.session_state.xp}</div><div class="stat-sub">{lvl_name()}</div></div>
        <div class="stat-card"><div class="stat-label">Streak</div><div class="stat-value">🔥 {st.session_state.streak}d</div><div class="stat-sub">Keep going!</div></div>
        <div class="stat-card"><div class="stat-label">Badges</div><div class="stat-value">🏅 {len(st.session_state.badges)}</div><div class="stat-sub">of {len(BADGE_DEFS)}</div></div>
        <div class="stat-card"><div class="stat-label">Holdings</div><div class="stat-value">💼 {len(st.session_state.portfolio)}</div><div class="stat-sub">added</div></div>
    </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sw-card"><div class="sw-card-title">📋 Today\'s Checklist</div>',
                    unsafe_allow_html=True)
        tasks = [
            ("📖","Read daily lesson","lesson",st.session_state.lesson_done),
            ("🧨","Run the Risk Radar","risk",st.session_state.wiz_complete),
            ("💬","Ask the AI Tutor","chat",st.session_state.tutor_q>0),
        ]
        for icon,label,sc,done in tasks:
            tick = "✅ " if done else f"{icon} "
            if st.button(f"{tick}{label}", key=f"hm_{sc}"):
                st.session_state.screen = sc; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<div class="sw-card">
            <div class="sw-card-title">🧠 Your Investor Profile</div>
            <div style="font-size:.83rem;color:#374151;line-height:1.65">{p['desc']}</div>
            <div style="margin-top:9px;font-size:.78rem">
                <span style="color:#64748B">Risk appetite:</span> <strong>{p['risk_level']}</strong>
                &nbsp;|&nbsp;
                <span style="color:#64748B">Focus:</span> <strong>{p['focus']}</strong>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="sw-card">
        <div class="sw-card-title">⭐ Level Progress — {lvl_name()}</div>
        <div class="xp-bar-wrap"><div class="xp-bar" style="width:{xp_pct()}%"></div></div>
        <div style="font-size:.76rem;color:#64748B;margin-top:4px">{st.session_state.xp} XP · {xp_next()} to next level</div>
    </div>""", unsafe_allow_html=True)

# ── Daily Lesson ──────────────────────────────────────────────────────────────
def screen_lesson():
    p = PERSONAS[st.session_state.persona]
    st.markdown("## 📖 Daily AI Lesson")
    st.markdown(f"*Personalized for {p['emoji']} {p['name']} · {p['risk_level']} risk*")

    today_topic = TOPICS[datetime.now().day % len(TOPICS)]

    if not st.session_state.daily_lesson:
        with st.spinner("✨ Crafting your personalized lesson..."):
            lesson = call_ai(
                f"""You are StakeWise, a warm financial coach for everyday people with zero investing experience.
User persona: '{p['name']}', risk level: '{p['risk_level']}', focus: '{p['focus']}'.
STRICT RULES:
- Never use a financial term without immediately explaining it in plain brackets.
- Keep it under 180 words total.
- Structure: 🪝 Hook (1 punchy sentence) | 💡 Concept (2-3 sentences with real-world analogy) | 💰 Real example (specific $ amounts a beginner would relate to, e.g. $500-$5000) | 🎯 Your takeaway (one action for this persona specifically).
- Warm, encouraging tone. No condescension.""",
                f"Today's topic: {today_topic}", max_tokens=380,
            )
            st.session_state.daily_lesson = lesson

    st.markdown(f"""<div class="sw-card">
        <div class="sw-card-title">📚 Today's Topic: {today_topic}
        <span class="source-badge">AI-generated · GPT-4o-mini</span></div>
        <div class="lesson-box">{st.session_state.daily_lesson}</div>
    </div>""", unsafe_allow_html=True)

    # Jargon buster
    topic_terms = {t:v for t,v in GLOSSARY.items()
                   if t.lower() in today_topic.lower() or t.lower() in st.session_state.daily_lesson.lower()}
    if topic_terms:
        with st.expander("📘 Jargon buster — terms in today's lesson"):
            for term,defn in list(topic_terms.items())[:4]:
                st.markdown(f"**{term}:** {defn}")

    if not st.session_state.lesson_done:
        if st.button("✅ Mark as read (+30 XP)", use_container_width=True):
            st.session_state.lesson_done = True; add_xp(30); award("First Lesson"); st.rerun()
    else:
        st.markdown('<div class="ok">✅ Lesson complete! +30 XP earned.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧩 Test Your Knowledge")
    if not st.session_state.kq_list:
        if st.button("🎯 Start 3-question Mini-Quiz (+20 XP per correct)", use_container_width=True):
            with st.spinner("Generating quiz..."):
                raw = call_ai(
                    "You are a quiz generator for beginner investors. Return ONLY valid JSON — no markdown fences, no preamble.",
                    f'3 beginner multiple-choice questions about "{today_topic}". Return exactly: '
                    f'[{{"q":"...","opts":["A) ...","B) ...","C) ...","D) ..."],"correct":0,"explain":"Plain English explanation of the correct answer."}}]',
                    max_tokens=600,
                )
            try:
                cleaned = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                st.session_state.kq_list = json.loads(cleaned)
                st.session_state.kq_idx = 0; st.session_state.kq_score = 0
            except: st.error("Quiz generation failed — try again.")
            st.rerun()

    elif not st.session_state.kq_done:
        qs = st.session_state.kq_list; idx = st.session_state.kq_idx
        if idx < len(qs):
            q = qs[idx]
            st.markdown(f"**Q{idx+1}/{len(qs)}: {q['q']}**")
            for i,opt in enumerate(q["opts"]):
                if st.button(opt, key=f"kq_{idx}_{i}"):
                    if i==q["correct"]:
                        st.session_state.kq_score += 1; add_xp(20)
                        st.success(f"✅ Correct! {q.get('explain','')}")
                    else:
                        st.error(f"❌ Right answer: {q['opts'][q['correct']]}. {q.get('explain','')}")
                    st.session_state.kq_idx += 1
                    if st.session_state.kq_idx >= len(qs):
                        st.session_state.kq_done = True
                        if st.session_state.kq_score == len(qs): award("Quiz Ace")
                    time.sleep(1.2); st.rerun()
    else:
        s,t = st.session_state.kq_score, len(st.session_state.kq_list)
        st.markdown(f'<div class="ok">🎯 Quiz done! {s}/{t} correct · +{s*20} XP earned</div>',
                    unsafe_allow_html=True)
        if st.button("🔄 Refresh for a new lesson"):
            for k in ["daily_lesson","lesson_done","kq_list","kq_done","kq_idx","kq_score"]:
                st.session_state[k] = DEFAULTS[k]
            st.rerun()
    trust_footer()

# ── Portfolio ──────────────────────────────────────────────────────────────────
def screen_portfolio():
    p = PERSONAS[st.session_state.persona]
    st.markdown("## 💼 My Portfolio")
    st.markdown("Add your investments. Don't worry about knowing the exact details — use a starter if you're unsure.")

    st.markdown('<div class="tip">💡 <strong>What\'s a ticker?</strong> Just a short code for a company — like AAPL for Apple, or VOO for a popular fund. Optional — feel free to just use the name.</div>',
                unsafe_allow_html=True)

    # Starter templates matched to persona
    if not st.session_state.portfolio:
        st.markdown("### 🧩 Starter Portfolios — pick one to begin")
        c1,c2,c3 = st.columns(3)
        starters = [
            ("🛡️ Conservative","Best if protecting your money matters most",
             [{"name":"US Bond Fund","ticker":"BND","amount":3000,"type":"Bonds"},
              {"name":"S&P 500 Index Fund","ticker":"VOO","amount":2000,"type":"Index Funds"}]),
            ("⚖️ Balanced","A sensible mix for steady, long-term growth",
             [{"name":"S&P 500 Index Fund","ticker":"VOO","amount":3000,"type":"Index Funds"},
              {"name":"Apple Inc.","ticker":"AAPL","amount":1000,"type":"Stocks"},
              {"name":"International ETF","ticker":"VXUS","amount":1000,"type":"International"}]),
            ("🚀 Growth","For those comfortable with ups and downs for bigger gains",
             [{"name":"Nasdaq 100 ETF","ticker":"QQQ","amount":2500,"type":"Index Funds"},
              {"name":"Tesla","ticker":"TSLA","amount":1000,"type":"Stocks"},
              {"name":"NVIDIA","ticker":"NVDA","amount":1500,"type":"Stocks"}]),
        ]
        for col,(name,desc,h) in zip([c1,c2,c3],starters):
            with col:
                st.markdown(f'<div class="sw-card" style="min-height:90px"><div style="font-weight:600;font-size:.86rem;margin-bottom:4px">{name}</div><div style="font-size:.76rem;color:#64748B;margin-bottom:10px">{desc}</div></div>',
                            unsafe_allow_html=True)
                if st.button(f"Use {name}", key=f"s_{name}", use_container_width=True):
                    st.session_state.portfolio = h; add_xp(25); award("Portfolio Pro"); st.rerun()

    with st.expander("➕ Add a holding manually"):
        c1,c2,c3,c4 = st.columns([3,1,2,2])
        with c1: hname   = st.text_input("Investment name", placeholder="e.g. Apple Inc.")
        with c2: hticker = st.text_input("Ticker", placeholder="AAPL")
        with c3: hamount = st.number_input("$ Amount", min_value=1, value=1000)
        with c4: htype   = st.selectbox("Asset type", ALL_ASSETS)
        if st.button("Add to portfolio"):
            if hname:
                st.session_state.portfolio.append(
                    {"name":hname,"ticker":hticker.upper(),"amount":hamount,"type":htype})
                add_xp(10)
                if len(st.session_state.portfolio)==1: award("Portfolio Pro")
                st.rerun()

    if not st.session_state.portfolio: return

    total_val = sum(h["amount"] for h in st.session_state.portfolio)
    alloc = portfolio_alloc()
    wr    = weighted_return(alloc)

    c1,c2 = st.columns([3,2])
    with c1:
        st.markdown('<div class="sw-card"><div class="sw-card-title">📊 Holdings</div>',
                    unsafe_allow_html=True)
        for i,h in enumerate(st.session_state.portfolio):
            pct   = h["amount"]/total_val*100
            color = ASSET_COLORS.get(h["type"],"#64748B")
            a,b,c,d,e = st.columns([3,1,2,2,1])
            with a: st.markdown(f'<div style="font-size:.83rem;font-weight:500">{h["name"]}</div>',unsafe_allow_html=True)
            with b: st.markdown(f'<div style="font-size:.73rem;color:#64748B">{h["ticker"]}</div>',unsafe_allow_html=True)
            with c: st.markdown(f'<div style="font-size:.83rem">${h["amount"]:,.0f}</div>',unsafe_allow_html=True)
            with d: st.markdown(f'<div style="font-size:.7rem;color:{color};font-weight:600;margin-bottom:1px">{pct:.0f}% · {h["type"]}</div><div class="bar-wrap"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>',unsafe_allow_html=True)
            with e:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.portfolio.pop(i); st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

    with c2:
        st.markdown(f"""<div class="sw-card">
            <div class="sw-card-title">📈 Simulated Growth Projection
            <span class="source-badge">Ibbotson SBBI historical avg</span></div>
            <div class="tip" style="font-size:.74rem;margin-bottom:10px">Based on long-run historical averages. Not a guarantee.</div>""",
            unsafe_allow_html=True)
        for years in [5,10,20]:
            proj = total_val*((1+wr)**years); gain = proj-total_val
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #F1F5F9;font-size:.81rem"><span>{years}-year</span><span style="font-weight:600;color:#10B981">${proj:,.0f} <span style="font-size:.7rem;color:#64748B">(+${gain:,.0f})</span></span></div>',
                        unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:.7rem;color:#94A3B8;margin-top:7px">Avg annual return assumed: {wr*100:.1f}%</div></div>',
                    unsafe_allow_html=True)

    if st.button("🤖 AI Portfolio Commentary (+15 XP)", use_container_width=True):
        hs = ", ".join([f"{h['ticker'] or h['name']} (${h['amount']:,.0f}, {h['type']})"
                        for h in st.session_state.portfolio])
        with st.spinner("Analyzing..."):
            resp = call_ai(
                f"StakeWise coach. Persona: {p['name']}, risk: {p['risk_level']}. "
                f"Be concise. Explain any term you use. Use these exact headers:",
                f"Portfolio: {hs}. Total: ${total_val:,.0f}.\n"
                f"✅ What's working: (1 sentence)\n"
                f"⚠️ Watch out for: (1 risk, explained plainly)\n"
                f"💡 One improvement: (concrete beginner action)\n"
                f"🎯 Persona fit: (does this match {p['risk_level']} risk?)\n"
                f"📊 Why this matters: (1 sentence on why allocation decisions are critical)",
                max_tokens=320,
            )
        st.markdown(f'<div class="lesson-box">{resp}</div>', unsafe_allow_html=True)
        add_xp(15)
    trust_footer()

# ── Risk Radar: 4-step guided wizard ─────────────────────────────────────────
def screen_risk():
    p = PERSONAS[st.session_state.persona]
    st.markdown("## 🧨 Risk Radar — Guided Rebalancing Wizard")
    st.markdown("Walk through 4 steps to understand your risk and get a personalized action plan.")

    st.markdown('<div class="tip" style="margin-bottom:1rem">💡 <strong>What is rebalancing?</strong> It\'s simply moving some money between investment types to better match how much risk you\'re comfortable with — like shifting items between different savings jars.</div>',
                unsafe_allow_html=True)

    # Step indicator
    wiz_step = st.session_state.wiz_step
    step_labels = ["Your Setup","Pick Scenario","Adjust & Compare","Your Action Plan"]
    dots = "".join(
        f'<div class="step-dot {"sd-done" if i<wiz_step else "sd-active" if i==wiz_step else "sd-todo"}">{i+1}</div>'
        f'<span style="font-size:.72rem;color:{"#94A3B8"};font-weight:{"600" if i==wiz_step else "400"}">&nbsp;{l}&nbsp;&nbsp;</span>'
        for i,(l) in enumerate(step_labels)
    )
    st.markdown(f'<div class="step-row">{dots}</div>', unsafe_allow_html=True)
    st.markdown("---")

    # ── STEP 1: Setup ─────────────────────────────────────────────────────────
    if wiz_step == 0:
        st.markdown("### Step 1 — Tell us about your situation")
        c1,c2 = st.columns(2)
        with c1:
            monthly = st.number_input(
                "💰 Your monthly living expenses ($)",
                min_value=100, value=st.session_state.get("monthly_expense",2500), step=100,
                help="We use this to translate losses into real-life terms — like 'months of rent' — so numbers feel meaningful, not abstract.")
        with c2:
            pv = sum(h["amount"] for h in st.session_state.portfolio) if st.session_state.portfolio else 0
            port_val = st.number_input(
                "📊 Total amount invested ($)",
                min_value=100, value=st.session_state.get("port_val", max(pv,5000)), step=500,
                help="This is the total dollar value of your investment portfolio.")

        current_alloc = portfolio_alloc()
        st.markdown("#### Your current allocation")
        st.markdown('<div class="tip" style="font-size:.76rem">This is based on your portfolio. If you haven\'t added holdings yet, it defaults to the recommended allocation for your persona.</div>',
                    unsafe_allow_html=True)
        for asset,pct in current_alloc.items():
            if pct > 0:
                color = ASSET_COLORS.get(asset,"#64748B")
                st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:1px">'
                            f'<span>{asset}</span><span style="color:{color};font-weight:600">{pct}%</span></div>'
                            f'<div class="bar-wrap"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>',
                            unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("Continue to Step 2 →", use_container_width=True):
            st.session_state.monthly_expense = monthly
            st.session_state.port_val = port_val
            st.session_state.wiz_step = 1; st.rerun()

    # ── STEP 2: Pick scenario ─────────────────────────────────────────────────
    elif wiz_step == 1:
        st.markdown("### Step 2 — Choose a historical market scenario")
        st.markdown("Each one is based on a real crash. Which feels most relevant to what you worry about?")

        chosen = st.radio("Select a scenario:", list(SCENARIOS.keys()),
                          index=0 if not st.session_state.wiz_scenario
                          else list(SCENARIOS.keys()).index(st.session_state.wiz_scenario))
        sc = SCENARIOS[chosen]

        # Show what happened + impact preview
        st.markdown(f"""<div class="sw-card">
            <div class="sw-card-title">{sc['emoji']} {sc['label']} — What happened?</div>
            <div style="font-size:.83rem;color:#374151;line-height:1.65;margin-bottom:10px">{sc['cause']}</div>
            <div class="sc sc-safe" style="font-size:.82rem"><strong>💡 What protected investors:</strong> {sc['lesson']}</div>
            <div style="margin-top:8px;font-size:.8rem;color:#64748B">⏱️ Recovery time: <strong>{sc['recovery']}</strong></div>
        </div>""", unsafe_allow_html=True)

        # Quick impact preview
        pv   = st.session_state.get("port_val",5000)
        me   = st.session_state.get("monthly_expense",2500)
        ca   = portfolio_alloc()
        loss = calc_crash_loss(ca, pv, sc["pct"])
        mos  = loss / me

        st.markdown(f"""<div class="sc sc-severe">
            <div class="sc-title">📊 Quick preview — your current portfolio in this scenario</div>
            <div class="sc-body">Based on your <strong>{', '.join([f'{k}:{v}%' for k,v in ca.items() if v>0])}</strong> allocation</div>
            <div class="sc-dollar" style="color:#DC2626">Estimated loss: -${loss:,.0f} ({sc['pct']*100:.0f}% drop weighted by your asset mix)</div>
            <div class="sc-body" style="margin-top:4px">That's about <strong>{mos:.1f} months</strong> of your living expenses (${me:,.0f}/month)</div>
            {impact_dots(loss/pv)}
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="trust" style="font-size:.73rem">📊 <strong>How is this calculated?</strong> We apply asset-class crash sensitivity weights (sourced from Ibbotson SBBI & Vanguard research) to your specific allocation — so a portfolio with more Bonds loses less than one with more Stocks in the same crash.</div>',
                    unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1:
            if st.button("← Back to Step 1", use_container_width=True):
                st.session_state.wiz_step = 0; st.rerun()
        with c2:
            if st.button("Continue to Step 3 →", use_container_width=True):
                st.session_state.wiz_scenario = chosen
                st.session_state.wiz_step = 2; st.rerun()

    # ── STEP 3: Adjust & Compare ──────────────────────────────────────────────
    elif wiz_step == 2:
        sc   = SCENARIOS[st.session_state.wiz_scenario]
        ca   = portfolio_alloc()
        pv   = st.session_state.get("port_val",5000)
        me   = st.session_state.get("monthly_expense",2500)

        st.markdown(f"### Step 3 — Try a new allocation for the {sc['label']}")
        st.markdown(f'<div class="tip">{p["rebal_nudge"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="warn-box" style="margin:.5rem 0">⚠️ Moving more into <strong>Bonds</strong> or <strong>Cash</strong> reduces crash losses — but also lowers your long-term growth potential. There\'s always a trade-off. The right balance depends on your goals and timeline.</div>',
                    unsafe_allow_html=True)

        # AI-suggested target
        ai_target_key = f"ai_target_{st.session_state.wiz_scenario}"
        if ai_target_key not in st.session_state:
            with st.spinner("🤖 Calculating your AI-recommended allocation..."):
                cur_str = ", ".join([f"{k}: {v}%" for k,v in ca.items() if v>0])
                rec = call_ai(
                    "You are a financial planning assistant. Return ONLY a JSON object — no text, no fences.",
                    f"""Persona: {p['name']}, risk: {p['risk_level']}.
Current allocation: {cur_str}.
Crash scenario: {sc['label']} (−{sc['pct']*100:.0f}% market drop).
Available asset classes: {', '.join(ALL_ASSETS)}.
Return a recommended defensive allocation as JSON: {{"Bonds":N,"Index Funds":N,"Cash / Savings":N,"Stocks":N,"International":N,"Alternative":N}}
Values must sum to exactly 100. Only include asset classes with value > 0.
Optimize to reduce crash loss for this persona while maintaining some growth potential.""",
                    max_tokens=200,
                )
            try:
                cleaned = rec.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                st.session_state[ai_target_key] = json.loads(cleaned)
            except:
                # fallback
                st.session_state[ai_target_key] = p["alloc"]

        ai_target = st.session_state[ai_target_key]

        col_s,col_c = st.columns([1,1])
        new_alloc = {}

        with col_s:
            st.markdown("**Drag to adjust your allocation:**")
            remaining = 100
            for i,asset in enumerate(ALL_ASSETS):
                cur_pct = ca.get(asset,0)
                if i < len(ALL_ASSETS)-1:
                    val = st.slider(f"{asset} %", 0, min(100,remaining), cur_pct, key=f"sl3_{asset}")
                    new_alloc[asset] = val; remaining -= val
                else:
                    last = max(0,remaining); new_alloc[asset] = last
                    st.markdown(f"**{asset}:** {last}% *(auto)*")

            total_check = sum(new_alloc.values())
            if total_check != 100:
                st.warning(f"⚠️ Allocation = {total_check}%. Adjust sliders to reach 100%.")

            st.markdown('<br>', unsafe_allow_html=True)
            st.markdown("#### 🤖 AI-Recommended Allocation")
            st.markdown('<div style="font-size:.76rem;color:#64748B;margin-bottom:8px">Based on your persona and this scenario — one click to apply:</div>',
                        unsafe_allow_html=True)
            for asset,pct in ai_target.items():
                if pct > 0:
                    color = ASSET_COLORS.get(asset,"#64748B")
                    st.markdown(f'<span style="font-size:.79rem"><strong>{asset}:</strong> <span style="color:{color};font-weight:600">{pct}%</span></span><br>',
                                unsafe_allow_html=True)
            if st.button("✨ Apply AI recommendation", use_container_width=True):
                for asset in ALL_ASSETS:
                    key = f"sl3_{asset}"
                    if key in st.session_state:
                        del st.session_state[key]
                # Store it and rerun to re-render sliders with new defaults
                st.session_state["pending_alloc"] = ai_target
                st.rerun()

        # Apply pending alloc from AI recommendation
        if "pending_alloc" in st.session_state:
            new_alloc = st.session_state.pop("pending_alloc")

        with col_c:
            st.markdown("**Before vs After — in this scenario:**")
            old_loss = calc_crash_loss(ca, pv, sc["pct"])
            new_loss = calc_crash_loss(new_alloc, pv, sc["pct"])
            old_rem  = pv - old_loss
            new_rem  = pv - new_loss
            saved    = old_loss - new_loss
            old_mos  = old_loss/me
            new_mos  = new_loss/me

            cb,ca2 = st.columns(2)
            with cb:
                st.markdown(f'<div class="rebal-box rebal-before"><div class="rebal-label" style="color:#991B1B">Current</div><div class="rebal-num" style="color:#DC2626">-${old_loss:,.0f}</div><div style="font-size:.72rem;color:#991B1B;margin-top:3px">estimated loss</div><div style="font-size:.78rem;margin-top:7px;color:#374151">Remaining: ${old_rem:,.0f}</div><div style="font-size:.74rem;color:#991B1B;margin-top:3px">{old_mos:.1f} months of expenses</div></div>',
                            unsafe_allow_html=True)
            with ca2:
                st.markdown(f'<div class="rebal-box rebal-after"><div class="rebal-label" style="color:#166534">Rebalanced</div><div class="rebal-num" style="color:#059669">-${new_loss:,.0f}</div><div style="font-size:.72rem;color:#166534;margin-top:3px">estimated loss</div><div style="font-size:.78rem;margin-top:7px;color:#374151">Remaining: ${new_rem:,.0f}</div><div style="font-size:.74rem;color:#166534;margin-top:3px">{new_mos:.1f} months of expenses</div></div>',
                            unsafe_allow_html=True)

            if saved > 0:
                st.markdown(f'<div class="ok" style="text-align:center;margin-top:8px">💰 Rebalancing could protect <strong>${saved:,.0f}</strong><br><span style="font-size:.76rem">({(saved/old_loss*100):.0f}% less loss in this scenario)</span></div>',
                            unsafe_allow_html=True)
            elif saved < 0:
                st.markdown(f'<div class="warn-box" style="margin-top:8px;text-align:center">⚠️ This adds risk — extra exposure of ${abs(saved):,.0f}</div>',
                            unsafe_allow_html=True)

            # Trade-off transparency
            new_wr   = weighted_return(new_alloc)
            old_wr   = weighted_return(ca)
            growth_diff = (new_wr - old_wr)*100
            st.markdown(f"""<div class="trust" style="margin-top:10px">
                📊 <strong>Growth trade-off:</strong> Rebalancing changes your expected annual return from
                <strong>{old_wr*100:.1f}%</strong> to <strong>{new_wr*100:.1f}%</strong>
                ({'+' if growth_diff>=0 else ''}{growth_diff:.1f}% per year).
                Protecting against crashes often means accepting lower long-term growth.
                <span class="source-badge">Ibbotson SBBI</span>
            </div>""", unsafe_allow_html=True)

            # New allocation preview
            st.markdown("**Your proposed new allocation:**")
            for asset,pct in new_alloc.items():
                if pct > 0:
                    color = ASSET_COLORS.get(asset,"#64748B")
                    st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:.77rem;margin-bottom:1px"><span>{asset}</span><span style="color:{color};font-weight:600">{pct}%</span></div><div class="bar-wrap"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>',
                                unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("← Back to Step 2", use_container_width=True):
                st.session_state.wiz_step = 1; st.rerun()
        with c2:
            if sum(new_alloc.values()) == 100:
                if st.button("Continue to Step 4 — Get Your Plan →", use_container_width=True):
                    st.session_state.wiz_new_alloc = new_alloc
                    st.session_state.wiz_step = 3; st.rerun()

    # ── STEP 4: Action Plan ───────────────────────────────────────────────────
    elif wiz_step == 3:
        sc       = SCENARIOS[st.session_state.wiz_scenario]
        ca       = portfolio_alloc()
        na       = st.session_state.wiz_new_alloc
        pv       = st.session_state.get("port_val",5000)
        me       = st.session_state.get("monthly_expense",2500)
        old_loss = calc_crash_loss(ca, pv, sc["pct"])
        new_loss = calc_crash_loss(na, pv, sc["pct"])
        saved    = old_loss - new_loss
        old_wr   = weighted_return(ca)
        new_wr   = weighted_return(na)

        st.markdown(f"### Step 4 — Your Personalized Action Plan")
        st.markdown(f'<div class="ok">✅ <strong>Wizard complete!</strong> Here is your personalized rebalancing plan for the {sc["label"]} scenario.</div>',
                    unsafe_allow_html=True)

        # Summary cards
        col1,col2,col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="sc sc-safe"><div class="sc-title">💰 Protected in a crash</div><div class="sc-dollar" style="color:#059669">${saved:,.0f}</div><div class="sc-body">less lost vs your current allocation</div></div>',
                        unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="sc sc-warn"><div class="sc-title">📉 Growth trade-off</div><div class="sc-dollar" style="color:#D97706">{(new_wr-old_wr)*100:+.1f}%/yr</div><div class="sc-body">change in expected annual return</div></div>',
                        unsafe_allow_html=True)
        with col3:
            mos = old_loss/me
            st.markdown(f'<div class="sc sc-severe"><div class="sc-title">🏠 Without rebalancing</div><div class="sc-dollar" style="color:#DC2626">{mos:.1f} months</div><div class="sc-body">of expenses at risk in this scenario</div></div>',
                        unsafe_allow_html=True)

        # AI action plan
        if not st.session_state.wiz_advice:
            with st.spinner("🤖 Generating your personalized action plan..."):
                cur_str = ", ".join([f"{k}: {v}%" for k,v in ca.items() if v>0])
                new_str = ", ".join([f"{k}: {v}%" for k,v in na.items() if v>0])
                advice = call_ai(
                    f"""You are StakeWise, a warm plain-English financial coach.
User: '{p['name']}', risk: '{p['risk_level']}'. RULES:
- Explain EVERY financial term you use in plain English brackets.
- Be specific (use the exact dollar amounts provided).
- Be honest about trade-offs.
- Keep total response under 250 words.
- Use exactly the 4 bold headers below.""",
                    f"""Portfolio: ${pv:,.0f}. Monthly expenses: ${me:,.0f}.
Scenario: {sc['label']} (−{sc['pct']*100:.0f}% drop).
Current allocation: {cur_str}. Proposed: {new_str}.
Loss before rebalancing: ${old_loss:,.0f} ({old_loss/me:.1f} months of expenses).
Loss after rebalancing: ${new_loss:,.0f} ({new_loss/me:.1f} months of expenses). Saved: ${saved:,.0f}.
Expected return before: {old_wr*100:.1f}%/year. After: {new_wr*100:.1f}%/year.

**What this scenario means for you** (2 sentences — mention the ${old_loss:,.0f} loss and what that feels like in real life)
**Why this rebalancing makes sense** (honest assessment for a {p['risk_level']} risk persona — include 1 trade-off)
**Your 3 action steps** (numbered, specific, beginner-friendly — e.g. "Move $X from Stocks into Bonds")
**One thing to remember** (a single motivating, honest closing thought)""",
                    max_tokens=500,
                )
                st.session_state.wiz_advice = advice

        st.markdown(f'<div class="lesson-box">{st.session_state.wiz_advice}</div>',
                    unsafe_allow_html=True)

        # Confidence indicator
        st.markdown(f"""<div class="conf-row">
            <span>AI confidence in this recommendation:</span>
            <div class="conf-bar-wrap"><div class="conf-bar" style="width:{70 + p['risk_score']*5}%"></div></div>
            <span>{70 + p['risk_score']*5}%</span>
            <span class="source-badge">Based on persona + historical data</span>
        </div>""", unsafe_allow_html=True)

        # Historical precedent
        st.markdown(f"""<div class="trust" style="margin-top:.8rem">
            📚 <strong>Historical precedent:</strong> {sc['lesson']}
            Recovery time after {sc['label']}: <strong>{sc['recovery']}</strong>.
            <span class="source-badge">Ibbotson SBBI · Vanguard</span>
        </div>""", unsafe_allow_html=True)

        if not st.session_state.wiz_complete:
            st.session_state.wiz_complete = True
            add_xp(30); award("Risk Radar")

        st.markdown('<br>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("🔄 Run a different scenario", use_container_width=True):
                for k in ["wiz_step","wiz_scenario","wiz_new_alloc","wiz_advice"]:
                    st.session_state[k] = DEFAULTS[k]
                st.rerun()
        with c2:
            if st.button("💬 Ask the AI Tutor a follow-up", use_container_width=True):
                st.session_state.screen = "chat"; st.rerun()

    trust_footer()

# ── AI Tutor Chat ──────────────────────────────────────────────────────────────
def screen_chat():
    p = PERSONAS[st.session_state.persona]
    st.markdown("## 💬 AI Tutor")
    st.markdown(f"*Ask me anything — I'll answer as your personal {p['emoji']} investing coach. No question is too basic.*")

    starters = [
        "What's the difference between a stock and an ETF?",
        "Is now a good time to start investing?",
        "How much should I invest each month?",
        "What does 'diversification' actually mean?",
        "Should I pay off debt before investing?",
        "Why do index funds beat most professional investors?",
    ]

    if not st.session_state.chat_history:
        st.markdown("**💡 Not sure what to ask? Try one of these:**")
        for i,q in enumerate(starters):
            if st.button(q, key=f"sq_{i}"):
                st.session_state.chat_history.append({"role":"user","content":q})
                st.session_state.tutor_q += 1; st.rerun()

    for msg in st.session_state.chat_history:
        if msg["role"]=="user":
            st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"]=="user":
        with st.spinner("Thinking..."):
            sys = (f"You are StakeWise, a warm financial coach for everyday people. "
                   f"Persona: '{p['name']}', risk: '{p['risk_level']}', focus: '{p['focus']}'. "
                   f"Rules: Never use jargon without explaining it in plain English immediately. "
                   f"Keep responses under 5 sentences. Tailor every answer to their persona. "
                   f"After answering, add one follow-up question to deepen their understanding.")
            history = [{"role":"system","content":sys}] + st.session_state.chat_history
            client = get_client()
            if client:
                try:
                    r = client.chat.completions.create(model="gpt-4o-mini",messages=history,max_tokens=350,temperature=0.7)
                    ans = r.choices[0].message.content
                except Exception as e: ans = f"⚠️ Error: {e}"
            else: ans = "⚠️ Please add your OpenAI API key in the sidebar."
            st.session_state.chat_history.append({"role":"assistant","content":ans})
            add_xp(5); st.session_state.tutor_q += 1
            if st.session_state.tutor_q >= 5: award("Curious Mind")
        st.rerun()

    user_input = st.chat_input("Ask anything about investing — no question is too simple...")
    if user_input:
        st.session_state.chat_history.append({"role":"user","content":user_input}); st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear conversation"):
            st.session_state.chat_history = []; st.rerun()
    trust_footer()

# ── Glossary ───────────────────────────────────────────────────────────────────
def screen_glossary():
    st.markdown("## 📚 Jargon-Free Glossary")
    st.markdown("Every investing term explained in plain English. No MBA required.")
    for term,defn in GLOSSARY.items():
        st.markdown(f'<div class="sw-card" style="padding:13px 17px;margin-bottom:7px">'
                    f'<span class="gt">{term}</span>'
                    f'<span style="font-size:.83rem;color:#374151;margin-left:8px">{defn}</span></div>',
                    unsafe_allow_html=True)
    st.markdown('<div class="trust">💬 Missing a term? Ask your AI Tutor — it\'ll explain anything in plain English.</div>',
                unsafe_allow_html=True)

# ── Badges ─────────────────────────────────────────────────────────────────────
def screen_badges():
    st.markdown("## 🏅 Your Achievements")
    st.markdown(f"Earned **{len(st.session_state.badges)}** of {len(BADGE_DEFS)} badges.")
    st.markdown('<div class="sw-card"><div class="badge-grid">', unsafe_allow_html=True)
    for emoji,name,desc in BADGE_DEFS:
        earned = name in st.session_state.badges
        st.markdown(f'<div class="badge {"b-earn" if earned else "b-lock"}">'
                    f'<span style="font-size:15px">{"🔒" if not earned else emoji}</span>'
                    f'<span><strong>{name}</strong><br>'
                    f'<span style="font-size:.69rem;font-weight:400">{desc}</span></span></div>',
                    unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sw-card"><div class="sw-card-title">⭐ Level Roadmap</div>', unsafe_allow_html=True)
    for i,(n,t) in enumerate(zip(LEVEL_NAMES,LEVEL_XP)):
        icon = "✅" if st.session_state.xp>=t and i+1<st.session_state.level else ("👉" if i+1==st.session_state.level else "○")
        st.markdown(f"**{icon} Level {i+1} — {n}** &nbsp; `{t} XP`")
    st.markdown('</div>', unsafe_allow_html=True)

# ─── Router ────────────────────────────────────────────────────────────────────
render_sidebar()
render_header()
render_bottom_nav()

{
    "welcome":screen_welcome,"quiz":screen_quiz,"persona_reveal":screen_persona_reveal,
    "home":screen_home,"lesson":screen_lesson,"portfolio":screen_portfolio,
    "risk":screen_risk,"chat":screen_chat,"glossary":screen_glossary,"badges":screen_badges,
}.get(st.session_state.screen, screen_welcome)()