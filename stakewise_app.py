import streamlit as st
import openai
import json
import random
from datetime import datetime, date
import time

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StakeWise",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── Brand palette ── */
:root {
    --sw-navy:   #0F2044;
    --sw-blue:   #1A56DB;
    --sw-teal:   #0EA5E9;
    --sw-green:  #10B981;
    --sw-amber:  #F59E0B;
    --sw-red:    #EF4444;
    --sw-light:  #F0F4FF;
    --sw-border: #E2E8F0;
    --sw-muted:  #64748B;
}

/* ── Header / logo bar ── */
.sw-header {
    display: flex; align-items: center; gap: 10px;
    padding: 0.6rem 1.2rem; margin-bottom: 1.2rem;
    background: var(--sw-navy); border-radius: 14px; color: white;
}
.sw-logo { font-size: 1.5rem; font-weight: 700; letter-spacing: -0.5px; }
.sw-tagline { font-size: 0.78rem; color: #93C5FD; margin-left: auto; }

/* ── Stat cards ── */
.stat-row { display: flex; gap: 12px; margin-bottom: 1rem; flex-wrap: wrap; }
.stat-card {
    flex: 1; min-width: 110px;
    background: white; border: 1px solid var(--sw-border);
    border-radius: 12px; padding: 14px 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.stat-label { font-size: 0.72rem; color: var(--sw-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
.stat-value { font-size: 1.4rem; font-weight: 700; color: var(--sw-navy); margin-top: 2px; }
.stat-sub   { font-size: 0.72rem; color: var(--sw-muted); }

/* ── Section cards ── */
.sw-card {
    background: white; border: 1px solid var(--sw-border);
    border-radius: 14px; padding: 20px 22px; margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.sw-card-title { font-size: 1rem; font-weight: 600; color: var(--sw-navy); margin-bottom: 0.8rem; }

/* ── Persona chips ── */
.persona-chip {
    display: inline-block; padding: 4px 12px;
    border-radius: 20px; font-size: 0.78rem; font-weight: 600;
    background: var(--sw-light); color: var(--sw-blue);
    border: 1px solid #BFDBFE;
}

/* ── Risk meter ── */
.risk-bar-wrap { background: #F1F5F9; border-radius: 8px; height: 10px; overflow: hidden; margin: 6px 0; }
.risk-bar { height: 100%; border-radius: 8px; transition: width 0.5s; }

/* ── Scenario cards ── */
.scenario-card {
    border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
    border-left: 4px solid;
}
.scenario-mild   { background: #F0FDF4; border-color: var(--sw-green); }
.scenario-bad    { background: #FFFBEB; border-color: var(--sw-amber); }
.scenario-severe { background: #FEF2F2; border-color: var(--sw-red); }
.scenario-title  { font-weight: 600; font-size: 0.88rem; margin-bottom: 4px; }
.scenario-body   { font-size: 0.82rem; color: #374151; }
.scenario-dollar { font-size: 1.1rem; font-weight: 700; margin-top: 6px; }

/* ── Quiz option buttons ── */
.stButton > button {
    border-radius: 10px !important; font-size: 0.88rem !important;
    border: 1.5px solid var(--sw-border) !important;
    background: white !important; color: var(--sw-navy) !important;
    text-align: left !important; width: 100% !important;
    padding: 10px 16px !important; transition: all 0.15s !important;
}
.stButton > button:hover {
    border-color: var(--sw-blue) !important;
    background: var(--sw-light) !important;
}

/* ── XP bar ── */
.xp-bar-wrap { background: #E2E8F0; border-radius: 8px; height: 8px; overflow: hidden; }
.xp-bar { background: linear-gradient(90deg, var(--sw-blue), var(--sw-teal)); height: 100%; border-radius: 8px; }

/* ── Chat bubbles ── */
.chat-user { background: var(--sw-blue); color: white; border-radius: 14px 14px 4px 14px; padding: 10px 14px; margin: 6px 0; margin-left: 15%; font-size: 0.88rem; }
.chat-ai   { background: #F8FAFC; border: 1px solid var(--sw-border); border-radius: 14px 14px 14px 4px; padding: 10px 14px; margin: 6px 0; margin-right: 15%; font-size: 0.88rem; }

/* ── Badge grid ── */
.badge-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.badge {
    border-radius: 10px; padding: 8px 12px; font-size: 0.78rem; font-weight: 600;
    display: flex; align-items: center; gap: 6px;
}
.badge-earned  { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
.badge-locked  { background: #F8FAFC; color: #94A3B8; border: 1px solid #E2E8F0; }

/* ── Nav pills ── */
.nav-active { background: var(--sw-navy) !important; color: white !important; }

/* ── Progress step ── */
.step-row { display: flex; gap: 8px; align-items: center; margin-bottom: 1rem; }
.step-dot  { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; flex-shrink: 0; }
.step-done { background: var(--sw-green); color: white; }
.step-active { background: var(--sw-blue); color: white; }
.step-todo { background: #E2E8F0; color: #94A3B8; }

/* ── Welcome card ── */
.welcome-card {
    background: linear-gradient(135deg, var(--sw-navy) 0%, #1e3a8a 100%);
    border-radius: 16px; padding: 32px; color: white; text-align: center; margin-bottom: 1.5rem;
}
.welcome-title { font-size: 2rem; font-weight: 700; margin-bottom: 8px; }
.welcome-sub   { font-size: 1rem; color: #93C5FD; margin-bottom: 20px; }

/* ── Lesson card ── */
.lesson-card {
    background: var(--sw-light); border-radius: 12px; padding: 18px;
    border-left: 4px solid var(--sw-blue); margin-bottom: 1rem;
    font-size: 0.9rem; line-height: 1.7; color: #1E293B;
}

/* ── Toast ── */
.toast-success {
    background: #ECFDF5; border: 1px solid #6EE7B7; border-radius: 10px;
    padding: 12px 16px; color: #065F46; font-weight: 500; font-size: 0.88rem;
}
</style>
""", unsafe_allow_html=True)

# ─── OpenAI client ──────────────────────────────────────────────────────────────
def get_client():
    key = st.session_state.get("api_key", "")
    if key:
        return openai.OpenAI(api_key=key)
    return None

def call_ai(system_prompt, user_prompt, max_tokens=600):
    client = get_client()
    if not client:
        return "⚠️ Please enter your OpenAI API key in the sidebar to enable AI features."
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI error: {str(e)}"

# ─── Session state init ─────────────────────────────────────────────────────────
DEFAULTS = {
    "screen": "welcome",
    "api_key": "",
    "persona": None,
    "persona_name": None,
    "quiz_step": 0,
    "quiz_answers": [],
    "xp": 0,
    "level": 1,
    "streak": 1,
    "badges": [],
    "chat_history": [],
    "portfolio": [],
    "lesson_done": False,
    "knowledge_quiz_done": False,
    "knowledge_quiz_score": 0,
    "daily_lesson": "",
    "knowledge_questions": [],
    "kq_index": 0,
    "kq_score": 0,
    "scenario_text": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Persona data ───────────────────────────────────────────────────────────────
PERSONAS = {
    "A": {
        "name": "The Cautious Keeper",
        "emoji": "🛡️",
        "desc": "You value safety above all. You prefer stability, sleep well knowing your money is protected, and want to understand every risk before committing a single dollar.",
        "focus": "Capital preservation & low-risk investing",
        "color": "#0EA5E9",
        "risk_level": "Low",
    },
    "B": {
        "name": "The Steady Builder",
        "emoji": "🏗️",
        "desc": "You're patient and consistent. You believe in slow-and-steady wealth building, diversification, and tuning out market noise.",
        "focus": "Diversified portfolios & long-term growth",
        "color": "#10B981",
        "risk_level": "Medium-Low",
    },
    "C": {
        "name": "The Growth Seeker",
        "emoji": "🚀",
        "desc": "You're willing to take calculated risks for bigger rewards. You follow market trends and get excited about opportunities — but sometimes act on impulse.",
        "focus": "Growth stocks, ETFs & trend investing",
        "color": "#1A56DB",
        "risk_level": "Medium-High",
    },
    "D": {
        "name": "The Bold Adventurer",
        "emoji": "⚡",
        "desc": "High risk, high reward — that's your motto. You're comfortable with volatility and love discovering emerging opportunities before others do.",
        "focus": "High-growth, alternative & emerging investments",
        "color": "#F59E0B",
        "risk_level": "High",
    },
}

# ─── Onboarding quiz questions ──────────────────────────────────────────────────
QUIZ_QUESTIONS = [
    {
        "q": "Imagine your investment drops 20% overnight. What's your gut reaction?",
        "opts": [
            ("Panic — I'd want to sell immediately and stop the bleeding.", "A"),
            ("Worried, but I'd hold on and wait for recovery.", "B"),
            ("Calm — I see this as a potential buying opportunity.", "C"),
            ("Excited! Time to buy more at a discount.", "D"),
        ],
    },
    {
        "q": "You have $5,000 to invest. Which option appeals most to you?",
        "opts": [
            ("A savings account — guaranteed returns, no surprises.", "A"),
            ("A diversified index fund — steady, boring, reliable.", "B"),
            ("A mix of growth stocks with some index funds.", "C"),
            ("A few high-potential individual stocks or crypto.", "D"),
        ],
    },
    {
        "q": "How long are you comfortable leaving your money invested?",
        "opts": [
            ("Less than 2 years — I might need it soon.", "A"),
            ("3–5 years — medium term.", "B"),
            ("5–10 years — I'm in it for the long game.", "C"),
            ("10+ years — I won't touch it for decades.", "D"),
        ],
    },
    {
        "q": "When you hear 'the stock market is at an all-time high,' you think...",
        "opts": [
            ("It's about to crash — I should stay out.", "A"),
            ("Be cautious, but don't panic-sell what I have.", "B"),
            ("Markets go up long-term — I'm optimistic.", "C"),
            ("Great momentum! What should I buy next?", "D"),
        ],
    },
    {
        "q": "What's your #1 goal with investing?",
        "opts": [
            ("Protect what I have — don't lose money.", "A"),
            ("Slowly grow my savings over time.", "B"),
            ("Beat inflation and build real wealth.", "C"),
            ("Maximize returns — I want to grow fast.", "D"),
        ],
    },
]

LEVEL_NAMES = ["Beginner", "Learner", "Explorer", "Investor", "Pro"]
LEVEL_XP    = [0, 100, 250, 500, 1000]

BADGE_DEFS = [
    ("🎓", "First Step",       "Completed the persona quiz"),
    ("📖", "First Lesson",     "Read your first AI lesson"),
    ("🎯", "Quiz Ace",         "Scored 100% on a knowledge quiz"),
    ("🔥", "On a Roll",        "Kept a 3-day streak"),
    ("💼", "Portfolio Pro",    "Added your first portfolio"),
    ("🧠", "Curious Mind",     "Asked 5 tutor questions"),
    ("⚡", "Risk Radar",       "Ran your first risk scenario"),
    ("🏆", "StakeWise Master", "Reached Investor level"),
]

def award_badge(name):
    if name not in st.session_state.badges:
        st.session_state.badges.append(name)

def add_xp(amount):
    st.session_state.xp += amount
    for i, threshold in enumerate(LEVEL_XP):
        if st.session_state.xp >= threshold:
            st.session_state.level = i + 1

def get_level_name():
    idx = min(st.session_state.level - 1, len(LEVEL_NAMES) - 1)
    return LEVEL_NAMES[idx]

def xp_to_next():
    lvl = st.session_state.level
    if lvl >= len(LEVEL_XP):
        return 100
    return LEVEL_XP[lvl] - st.session_state.xp

def xp_pct():
    lvl = st.session_state.level
    if lvl >= len(LEVEL_XP):
        return 100
    lo = LEVEL_XP[lvl - 1]
    hi = LEVEL_XP[lvl]
    return int((st.session_state.xp - lo) / (hi - lo) * 100)

# ─── HEADER ────────────────────────────────────────────────────────────────────
def render_header():
    persona_label = ""
    if st.session_state.persona:
        p = PERSONAS[st.session_state.persona]
        persona_label = f"&nbsp;&nbsp;|&nbsp;&nbsp;{p['emoji']} {p['name']}"
    st.markdown(f"""
    <div class="sw-header">
        <span style="font-size:1.4rem;">📈</span>
        <span class="sw-logo">StakeWise</span>
        <span style="font-size:0.78rem; color:#93C5FD; margin-left:4px;">Your AI investing coach{persona_label}</span>
        <span class="sw-tagline">🔥 {st.session_state.streak}-day streak &nbsp;|&nbsp; ⭐ {st.session_state.xp} XP &nbsp;|&nbsp; {get_level_name()}</span>
    </div>
    """, unsafe_allow_html=True)

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        key = st.text_input("OpenAI API Key", value=st.session_state.api_key,
                            type="password", placeholder="sk-...")
        st.session_state.api_key = key
        if key:
            st.success("API key set ✓")

        st.markdown("---")
        st.markdown("### 🧭 Navigation")

        pages = [
            ("🏠", "Home",       "home"),
            ("📖", "Daily Lesson","lesson"),
            ("📊", "My Portfolio","portfolio"),
            ("🧨", "Risk Radar", "risk"),
            ("💬", "AI Tutor",   "chat"),
            ("🏅", "Badges",     "badges"),
        ]

        for icon, label, screen in pages:
            if st.session_state.persona:
                if st.button(f"{icon} {label}", key=f"nav_{screen}", use_container_width=True):
                    st.session_state.screen = screen
                    st.rerun()

        st.markdown("---")
        # XP progress
        st.markdown(f"**Level {st.session_state.level} · {get_level_name()}**")
        st.markdown(f"""
        <div class="xp-bar-wrap">
          <div class="xp-bar" style="width:{xp_pct()}%"></div>
        </div>
        <div style="font-size:0.72rem;color:var(--sw-muted);margin-top:3px">{st.session_state.xp} XP · {xp_to_next()} to next level</div>
        """, unsafe_allow_html=True)

# ─── SCREEN: WELCOME ───────────────────────────────────────────────────────────
def screen_welcome():
    st.markdown("""
    <div class="welcome-card">
        <div style="font-size:3rem;margin-bottom:8px">📈</div>
        <div class="welcome-title">Welcome to StakeWise</div>
        <div class="welcome-sub">Your AI-powered investing coach for everyday people</div>
        <div style="font-size:0.88rem;color:#BFDBFE;max-width:480px;margin:0 auto">
            No jargon. No assumptions. Just clear, personalized guidance — whether you have $100 or $100,000.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="sw-card" style="text-align:center">
            <div style="font-size:2rem">🎯</div>
            <div style="font-weight:600;margin:6px 0">Know Your Type</div>
            <div style="font-size:0.82rem;color:#64748B">Take a 5-question quiz and discover your investor personality</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="sw-card" style="text-align:center">
            <div style="font-size:2rem">🧨</div>
            <div style="font-weight:600;margin:6px 0">Understand Your Risk</div>
            <div style="font-size:0.82rem;color:#64748B">See exactly what a market crash means for <em>your</em> portfolio in real dollars</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="sw-card" style="text-align:center">
            <div style="font-size:2rem">💬</div>
            <div style="font-weight:600;margin:6px 0">Ask Anything</div>
            <div style="font-size:0.82rem;color:#64748B">Your AI tutor explains concepts in plain English, matched to your personality</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([2, 1, 2])
    with col_b:
        if st.button("🚀 Get Started", use_container_width=True):
            st.session_state.screen = "quiz"
            st.rerun()

# ─── SCREEN: QUIZ ──────────────────────────────────────────────────────────────
def screen_quiz():
    st.markdown("## 🎯 Discover Your Investor Persona")
    st.markdown("Answer 5 quick questions to get your personalized investing profile.")

    step = st.session_state.quiz_step
    total = len(QUIZ_QUESTIONS)

    # Progress dots
    dots = ""
    for i in range(total):
        if i < step:
            cls = "step-done"
        elif i == step:
            cls = "step-active"
        else:
            cls = "step-todo"
        dots += f'<div class="step-dot {cls}">{i+1}</div>'
    st.markdown(f'<div class="step-row">{dots}<span style="font-size:0.8rem;color:#64748B;margin-left:4px">Question {min(step+1,total)} of {total}</span></div>', unsafe_allow_html=True)

    if step < total:
        q = QUIZ_QUESTIONS[step]
        st.markdown(f"""<div class="sw-card">
            <div style="font-size:1rem;font-weight:600;color:#0F2044;margin-bottom:1rem">{q['q']}</div>
        </div>""", unsafe_allow_html=True)

        for opt_text, opt_val in q["opts"]:
            if st.button(opt_text, key=f"q{step}_{opt_val}"):
                st.session_state.quiz_answers.append(opt_val)
                st.session_state.quiz_step += 1
                st.rerun()
    else:
        # Tally answers
        from collections import Counter
        counts = Counter(st.session_state.quiz_answers)
        persona_key = counts.most_common(1)[0][0]
        st.session_state.persona = persona_key
        p = PERSONAS[persona_key]
        st.session_state.persona_name = p["name"]
        add_xp(50)
        award_badge("First Step")
        st.session_state.screen = "persona_reveal"
        st.rerun()

# ─── SCREEN: PERSONA REVEAL ────────────────────────────────────────────────────
def screen_persona_reveal():
    p = PERSONAS[st.session_state.persona]
    st.markdown(f"""
    <div class="welcome-card">
        <div style="font-size:3.5rem;margin-bottom:8px">{p['emoji']}</div>
        <div style="font-size:0.9rem;color:#93C5FD;font-weight:600;letter-spacing:1px;margin-bottom:4px">YOUR INVESTOR PERSONA</div>
        <div class="welcome-title">{p['name']}</div>
        <div style="font-size:0.95rem;color:#BFDBFE;max-width:500px;margin:0 auto 16px">{p['desc']}</div>
        <div style="display:inline-block;background:rgba(255,255,255,0.15);border-radius:20px;padding:6px 18px;font-size:0.82rem;font-weight:600">
            🎯 Focus: {p['focus']}
        </div>
        <div style="margin-top:8px;display:inline-block;background:rgba(255,255,255,0.1);border-radius:20px;padding:4px 14px;font-size:0.8rem">
            Risk Level: {p['risk_level']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div class="toast-success" style="text-align:center;margin-bottom:1rem">
        🎉 +50 XP earned! Badge unlocked: 🎓 First Step
    </div>""", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([2, 1, 2])
    with col_b:
        if st.button("Let's go! →", use_container_width=True):
            st.session_state.screen = "home"
            st.rerun()

# ─── SCREEN: HOME ──────────────────────────────────────────────────────────────
def screen_home():
    p = PERSONAS[st.session_state.persona]

    # Stats row
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <div class="stat-label">Your Persona</div>
            <div class="stat-value">{p['emoji']}</div>
            <div class="stat-sub">{p['name']}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">XP Earned</div>
            <div class="stat-value">⭐ {st.session_state.xp}</div>
            <div class="stat-sub">{get_level_name()}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Day Streak</div>
            <div class="stat-value">🔥 {st.session_state.streak}</div>
            <div class="stat-sub">Keep it up!</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Badges</div>
            <div class="stat-value">🏅 {len(st.session_state.badges)}</div>
            <div class="stat-sub">of {len(BADGE_DEFS)} total</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Portfolio Items</div>
            <div class="stat-value">💼 {len(st.session_state.portfolio)}</div>
            <div class="stat-sub">holdings tracked</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""<div class="sw-card">
            <div class="sw-card-title">📋 Today's Action Plan</div>
        </div>""", unsafe_allow_html=True)

        tasks = [
            ("📖", "Read your daily AI lesson", "lesson", not st.session_state.lesson_done),
            ("📊", "Review your portfolio risk", "risk", True),
            ("💬", "Ask your AI tutor a question", "chat", True),
        ]
        for icon, label, nav, active in tasks:
            done_icon = "✅" if (nav == "lesson" and st.session_state.lesson_done) else ""
            if st.button(f"{done_icon or icon} {label}", key=f"home_{nav}"):
                st.session_state.screen = nav
                st.rerun()

    with col2:
        st.markdown(f"""<div class="sw-card">
            <div class="sw-card-title">🧠 About Your Persona</div>
            <div style="font-size:0.88rem;color:#374151;line-height:1.6">{p['desc']}</div>
            <div style="margin-top:12px">
                <span class="persona-chip">🎯 {p['focus']}</span>
            </div>
            <div style="margin-top:8px;font-size:0.8rem;color:#64748B">Risk appetite: <strong>{p['risk_level']}</strong></div>
        </div>""", unsafe_allow_html=True)

    # XP progress
    st.markdown(f"""<div class="sw-card">
        <div class="sw-card-title">⭐ Level Progress — {get_level_name()}</div>
        <div class="xp-bar-wrap"><div class="xp-bar" style="width:{xp_pct()}%"></div></div>
        <div style="font-size:0.8rem;color:#64748B;margin-top:6px">{st.session_state.xp} XP · {xp_to_next()} XP to next level</div>
    </div>""", unsafe_allow_html=True)

# ─── SCREEN: DAILY LESSON ──────────────────────────────────────────────────────
def screen_lesson():
    p = PERSONAS[st.session_state.persona]
    st.markdown("## 📖 Daily AI Lesson")
    st.markdown(f"*Tailored for {p['emoji']} {p['name']} · {p['risk_level']} risk profile*")

    topics = ["Diversification", "Understanding ETFs", "The Power of Compound Interest",
              "How to Read a Stock Chart", "What is a P/E Ratio?", "Bond Basics",
              "Dollar-Cost Averaging", "Emergency Fund vs Investing", "Index Funds Explained",
              "Inflation and Your Money"]
    today_topic = topics[datetime.now().day % len(topics)]

    if not st.session_state.daily_lesson:
        with st.spinner("✨ Generating your personalized lesson..."):
            lesson = call_ai(
                f"""You are StakeWise, a friendly financial coach for everyday people.
The user is '{p['name']}' with '{p['risk_level']}' risk tolerance who focuses on '{p['focus']}'.
Write a 60-second bite-sized investing lesson. Structure: 
1. Hook (1 sentence grabber)
2. Core concept (2-3 sentences, no jargon — use simple analogies)
3. Real-life example with dollar amounts
4. One key takeaway for someone with this persona
Keep it warm, encouraging, and jargon-free. Use emojis sparingly.""",
                f"Today's topic: {today_topic}"
            )
            st.session_state.daily_lesson = lesson

    st.markdown(f"""<div class="sw-card">
        <div class="sw-card-title">Today's Topic: {today_topic}</div>
        <div class="lesson-card">{st.session_state.daily_lesson}</div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.lesson_done:
        if st.button("✅ Mark as read  (+30 XP)", use_container_width=True):
            st.session_state.lesson_done = True
            add_xp(30)
            award_badge("First Lesson")
            st.rerun()
    else:
        st.markdown('<div class="toast-success">✅ Lesson complete! +30 XP earned.</div>', unsafe_allow_html=True)

    # Knowledge quiz
    st.markdown("---")
    st.markdown("### 🧩 Test Your Knowledge")

    if not st.session_state.knowledge_questions:
        if st.button("🎯 Start Mini-Quiz (+20 XP per correct answer)", use_container_width=True):
            with st.spinner("Generating quiz..."):
                raw = call_ai(
                    "You are a financial quiz generator. Return ONLY valid JSON — an array of exactly 3 quiz objects.",
                    f"""Create 3 multiple-choice quiz questions about '{today_topic}' for a beginner investor.
Return ONLY this JSON format with no extra text:
[{{"q":"question","opts":["A) ...","B) ...","C) ...","D) ..."],"correct":0}}]
correct is the 0-based index of the right answer.""",
                    max_tokens=500,
                )
            try:
                cleaned = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                qs = json.loads(cleaned)
                st.session_state.knowledge_questions = qs
                st.session_state.kq_index = 0
                st.session_state.kq_score = 0
            except:
                st.error("Quiz generation failed — try again.")
            st.rerun()
    elif not st.session_state.knowledge_quiz_done:
        qs = st.session_state.knowledge_questions
        idx = st.session_state.kq_index
        if idx < len(qs):
            q = qs[idx]
            st.markdown(f"**Q{idx+1}/{len(qs)}: {q['q']}**")
            for i, opt in enumerate(q["opts"]):
                if st.button(opt, key=f"kq_{idx}_{i}"):
                    if i == q["correct"]:
                        st.session_state.kq_score += 1
                        add_xp(20)
                    st.session_state.kq_index += 1
                    st.rerun()
        else:
            score = st.session_state.kq_score
            total = len(qs)
            st.session_state.knowledge_quiz_done = True
            if score == total:
                award_badge("Quiz Ace")
            st.rerun()
    else:
        score = st.session_state.kq_score
        total = len(st.session_state.knowledge_questions)
        pct = int(score / total * 100)
        st.markdown(f"""<div class="toast-success">
            🎯 Quiz complete! You scored {score}/{total} ({pct}%) · +{score*20} XP earned
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 Reset lesson for next session"):
            st.session_state.daily_lesson = ""
            st.session_state.lesson_done = False
            st.session_state.knowledge_questions = []
            st.session_state.knowledge_quiz_done = False
            st.rerun()

# ─── SCREEN: PORTFOLIO ─────────────────────────────────────────────────────────
def screen_portfolio():
    st.markdown("## 💼 My Portfolio")
    st.markdown("Add your holdings and StakeWise will coach you on what they mean — in plain English.")

    # Sample starters
    if not st.session_state.portfolio:
        st.info("💡 No holdings yet. Use the starter templates or add your own below.")
        col1, col2, col3 = st.columns(3)
        starters = [
            ("🛡️ Safe Starter", [
                {"name": "Vanguard Total Bond ETF", "ticker": "BND", "amount": 3000, "type": "Bond ETF"},
                {"name": "S&P 500 Index Fund", "ticker": "VOO", "amount": 2000, "type": "Index ETF"},
            ]),
            ("📈 Balanced Mix", [
                {"name": "S&P 500 Index Fund", "ticker": "VOO", "amount": 3000, "type": "Index ETF"},
                {"name": "Apple Inc.", "ticker": "AAPL", "amount": 1500, "type": "Stock"},
                {"name": "International ETF", "ticker": "VXUS", "amount": 1500, "type": "ETF"},
            ]),
            ("🚀 Growth Focus", [
                {"name": "Nasdaq 100 ETF", "ticker": "QQQ", "amount": 3000, "type": "Index ETF"},
                {"name": "Tesla Inc.", "ticker": "TSLA", "amount": 1000, "type": "Stock"},
                {"name": "NVIDIA Corp.", "ticker": "NVDA", "amount": 1000, "type": "Stock"},
            ]),
        ]
        for col, (label, holdings) in zip([col1, col2, col3], starters):
            with col:
                if st.button(f"Use {label}", key=f"starter_{label}", use_container_width=True):
                    st.session_state.portfolio = holdings
                    add_xp(25)
                    award_badge("Portfolio Pro")
                    st.rerun()

    # Add holding form
    with st.expander("➕ Add a holding manually"):
        c1, c2, c3, c4 = st.columns([3, 1, 2, 1])
        with c1:
            hname = st.text_input("Investment name", placeholder="e.g. Apple Inc.")
        with c2:
            hticker = st.text_input("Ticker", placeholder="AAPL")
        with c3:
            hamount = st.number_input("Amount invested ($)", min_value=1, value=1000)
        with c4:
            htype = st.selectbox("Type", ["Stock", "ETF", "Index ETF", "Bond ETF", "Crypto", "Other"])
        if st.button("Add to Portfolio"):
            if hname:
                st.session_state.portfolio.append({"name": hname, "ticker": hticker.upper(), "amount": hamount, "type": htype})
                add_xp(10)
                if len(st.session_state.portfolio) == 1:
                    award_badge("Portfolio Pro")
                st.rerun()

    if st.session_state.portfolio:
        total_val = sum(h["amount"] for h in st.session_state.portfolio)

        st.markdown(f"""<div class="stat-row">
            <div class="stat-card"><div class="stat-label">Total Invested</div><div class="stat-value">${total_val:,.0f}</div></div>
            <div class="stat-card"><div class="stat-label">Holdings</div><div class="stat-value">{len(st.session_state.portfolio)}</div></div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sw-card"><div class="sw-card-title">📊 Your Holdings</div>', unsafe_allow_html=True)
        for i, h in enumerate(st.session_state.portfolio):
            pct = h["amount"] / total_val * 100
            col1, col2, col3, col4, col5 = st.columns([3, 1, 2, 2, 1])
            with col1: st.markdown(f"**{h['name']}**")
            with col2: st.markdown(f"`{h['ticker']}`")
            with col3: st.markdown(f"${h['amount']:,.0f} ({pct:.0f}%)")
            with col4:
                st.markdown(f"""<div class="risk-bar-wrap"><div class="risk-bar" style="width:{pct}%;background:#1A56DB"></div></div>""", unsafe_allow_html=True)
            with col5:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.portfolio.pop(i)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # AI portfolio commentary
        if st.button("🤖 Get AI Portfolio Analysis (+15 XP)", use_container_width=True):
            p = PERSONAS[st.session_state.persona]
            holdings_str = ", ".join([f"{h['ticker']} (${h['amount']:,.0f}, {h['type']})" for h in st.session_state.portfolio])
            with st.spinner("Analyzing your portfolio..."):
                analysis = call_ai(
                    f"You are StakeWise, a friendly financial coach for everyday people. Be concise, warm, and jargon-free. User persona: {p['name']}, risk: {p['risk_level']}.",
                    f"Analyze this portfolio in 3-4 sentences: {holdings_str}. Total: ${total_val:,.0f}. Comment on diversification, risk fit for their persona, and one specific improvement suggestion. Use plain English — no financial jargon.",
                    max_tokens=250,
                )
            st.markdown(f"""<div class="lesson-card">🤖 <strong>AI Analysis</strong><br><br>{analysis}</div>""", unsafe_allow_html=True)
            add_xp(15)

# ─── SCREEN: RISK RADAR ────────────────────────────────────────────────────────
def screen_risk():
    p = PERSONAS[st.session_state.persona]
    st.markdown("## 🧨 Risk Radar")
    st.markdown("See what market crashes mean for **your money** — in real-life terms, not percentages.")

    # Monthly expense context
    col1, col2 = st.columns(2)
    with col1:
        monthly_expense = st.number_input("Your monthly living expenses ($)", min_value=100, value=2500, step=100,
                                          help="Used to translate losses into relatable terms like 'months of rent'")
    with col2:
        portfolio_val = sum(h["amount"] for h in st.session_state.portfolio) if st.session_state.portfolio else 0
        custom_val = st.number_input("Portfolio value to analyze ($)",
                                     min_value=100, value=max(portfolio_val, 5000), step=500)

    st.markdown("---")
    st.markdown("### 🌪️ Scenario-Driven Rebalancing")
    st.markdown("Choose a historical market scenario to simulate:")

    scenarios = {
        "📉 2022 Rate Hike Selloff (-20%)": ("2022 rate-hike selloff", 0.20),
        "💥 2020 COVID Crash (-34%)":       ("2020 COVID-19 crash", 0.34),
        "🔥 2008 Financial Crisis (-50%)":  ("2008 global financial crisis", 0.50),
        "🌑 2000 Dot-Com Bust (-78%)":      ("2000 dot-com bubble burst", 0.78),
    }

    chosen = st.radio("Select scenario", list(scenarios.keys()), horizontal=True)
    scenario_label, drop_pct = scenarios[chosen]

    loss_dollars = custom_val * drop_pct
    remaining    = custom_val - loss_dollars
    months_rent  = loss_dollars / monthly_expense

    # Display impact cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="scenario-card scenario-severe">
            <div class="scenario-title">💸 Potential Loss</div>
            <div class="scenario-dollar" style="color:#DC2626">-${loss_dollars:,.0f}</div>
            <div class="scenario-body">A {drop_pct*100:.0f}% drop in your portfolio value</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="scenario-card scenario-bad">
            <div class="scenario-title">🏠 In Real Terms</div>
            <div class="scenario-dollar" style="color:#D97706">{months_rent:.1f} months</div>
            <div class="scenario-body">of your living expenses (${monthly_expense:,.0f}/mo)</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="scenario-card scenario-mild">
            <div class="scenario-title">💰 Portfolio Remaining</div>
            <div class="scenario-dollar" style="color:#059669">${remaining:,.0f}</div>
            <div class="scenario-body">{(1-drop_pct)*100:.0f}% of your original value</div>
        </div>""", unsafe_allow_html=True)

    # AI Rebalancing advice
    if st.button("🤖 Get AI Rebalancing Advice (+20 XP)", use_container_width=True):
        portfolio_str = ""
        if st.session_state.portfolio:
            portfolio_str = ", ".join([f"{h['ticker']} (${h['amount']:,.0f})" for h in st.session_state.portfolio])
        else:
            portfolio_str = f"a ${custom_val:,.0f} general portfolio"

        with st.spinner("Analyzing your risk scenario..."):
            advice = call_ai(
                f"""You are StakeWise, a warm, plain-English financial coach. User persona: '{p['name']}', risk level: '{p['risk_level']}'. 
NEVER use jargon without explaining it. Always translate numbers into relatable real-life terms.""",
                f"""The user has {portfolio_str} (total: ${custom_val:,.0f}).
Scenario: {scenario_label} — a {drop_pct*100:.0f}% market drop.
Projected loss: ${loss_dollars:,.0f} ({months_rent:.1f} months of their ${monthly_expense:,.0f}/mo expenses).

Respond in exactly this structure (use these headers):
**What this scenario means for you** (2 sentences — make it personal and relatable)
**Should you panic?** (1-2 sentences — honest, calming advice for their persona)
**Rebalancing suggestion** (2-3 sentences — one specific, actionable change they could make)
**Silver lining** (1 sentence — something genuinely positive)""",
                max_tokens=400,
            )
        st.session_state.scenario_text = advice
        add_xp(20)
        award_badge("Risk Radar")
        st.rerun()

    if st.session_state.scenario_text:
        st.markdown(f"""<div class="lesson-card">{st.session_state.scenario_text}</div>""", unsafe_allow_html=True)

    # Historical context
    st.markdown("---")
    st.markdown("### 📚 Historical Context")
    st.markdown(f"""<div class="sw-card">
        <div class="sw-card-title">What happened after past crashes?</div>
        <div style="font-size:0.88rem;line-height:1.8;color:#374151">
        📉 <strong>2022 Selloff:</strong> Markets recovered within ~12 months for most diversified portfolios.<br>
        💥 <strong>2020 COVID:</strong> S&P 500 recovered in just 6 months — one of the fastest in history.<br>
        🔥 <strong>2008 Crisis:</strong> Full recovery took ~4 years. Long-term investors who held on were rewarded.<br>
        🌑 <strong>2000 Dot-Com:</strong> Tech-heavy portfolios took 10+ years to recover. Diversification was key.
        </div>
    </div>""", unsafe_allow_html=True)

# ─── SCREEN: AI TUTOR CHAT ─────────────────────────────────────────────────────
def screen_chat():
    p = PERSONAS[st.session_state.persona]
    st.markdown("## 💬 AI Tutor")
    st.markdown(f"*Ask me anything about investing — I'll answer as your {p['emoji']} {p['name']} coach*")

    # Starter questions
    if not st.session_state.chat_history:
        st.markdown("**💡 Try asking:**")
        starters = [
            "What's the difference between a stock and an ETF?",
            "Is now a good time to start investing?",
            "How much should I invest each month?",
            "What does 'diversification' actually mean?",
            "Should I pay off debt before investing?",
        ]
        cols = st.columns(2)
        for i, q in enumerate(starters):
            with cols[i % 2]:
                if st.button(q, key=f"starter_q_{i}"):
                    st.session_state.chat_history.append({"role": "user", "content": q})
                    st.rerun()

    # Chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    # Generate AI response for last unanswered user message
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
        with st.spinner("Thinking..."):
            last_q = st.session_state.chat_history[-1]["content"]
            history_for_api = [
                {"role": "system", "content": f"""You are StakeWise, a warm and knowledgeable financial coach.
The user's persona is '{p['name']}' with '{p['risk_level']}' risk tolerance, focused on '{p['focus']}'.
Always answer in plain English. No jargon without explanation. Keep responses concise (3-5 sentences).
Tailor every answer to their persona and risk level. Be encouraging and practical."""}
            ] + st.session_state.chat_history
            client = get_client()
            if client:
                try:
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=history_for_api,
                        max_tokens=350,
                        temperature=0.7,
                    )
                    answer = resp.choices[0].message.content
                except Exception as e:
                    answer = f"⚠️ Error: {str(e)}"
            else:
                answer = "⚠️ Please add your OpenAI API key in the sidebar."
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            add_xp(5)
            if len([m for m in st.session_state.chat_history if m["role"] == "user"]) >= 5:
                award_badge("Curious Mind")
        st.rerun()

    # Input
    user_input = st.chat_input("Ask anything about investing...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()

# ─── SCREEN: BADGES ────────────────────────────────────────────────────────────
def screen_badges():
    st.markdown("## 🏅 Your Badges")
    st.markdown(f"You've earned **{len(st.session_state.badges)}** of {len(BADGE_DEFS)} badges.")

    st.markdown('<div class="sw-card"><div class="badge-grid">', unsafe_allow_html=True)
    for emoji, name, desc in BADGE_DEFS:
        earned = name in st.session_state.badges
        cls = "badge-earned" if earned else "badge-locked"
        lock = "" if earned else "🔒 "
        st.markdown(f"""<div class="badge {cls}">
            <span>{emoji if earned else "🔒"}</span>
            <span><strong>{name}</strong><br><span style="font-size:0.72rem;font-weight:400">{desc}</span></span>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Level progress
    st.markdown('<div class="sw-card"><div class="sw-card-title">⭐ Level Progress</div>', unsafe_allow_html=True)
    for i, (lvl_name, threshold) in enumerate(zip(LEVEL_NAMES, LEVEL_XP)):
        done = st.session_state.xp >= threshold
        active = (i + 1 == st.session_state.level)
        icon = "✅" if done and not active else ("👉" if active else "○")
        st.markdown(f"**{icon} Level {i+1} — {lvl_name}** &nbsp; `{threshold} XP`")
    st.markdown('</div>', unsafe_allow_html=True)

# ─── ROUTER ────────────────────────────────────────────────────────────────────
render_sidebar()
render_header()

screen = st.session_state.screen

if screen == "welcome":
    screen_welcome()
elif screen == "quiz":
    screen_quiz()
elif screen == "persona_reveal":
    screen_persona_reveal()
elif screen == "home":
    screen_home()
elif screen == "lesson":
    screen_lesson()
elif screen == "portfolio":
    screen_portfolio()
elif screen == "risk":
    screen_risk()
elif screen == "chat":
    screen_chat()
elif screen == "badges":
    screen_badges()
