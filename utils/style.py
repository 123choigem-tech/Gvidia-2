import streamlit as st

# 앱 공통 브랜드 아이콘·워드마크 (사이드바 CSS와 hero/page_header 에서 공유)
_EYEBROW = "GVIDIA · 고수온 연안재해 모니터링"


def apply():
    st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

html, body, [class*="css"] {
    font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
}

:root {
    --ocean-dark:   #020d1a;
    --ocean-deep:   #041529;
    --ocean-mid:    #062240;
    --ocean-light:  #0a3660;
    --cyan:         #00c2d4;
    --cyan-2:       #00e5ff;
    --teal:         #00a896;
    --warn:         #ff6b35;
    --ink:          #f2fbff;   /* 값·제목: near-white */
    --text:         #e8f4f8;
    --text-muted:   #7aacbf;
    --text-faint:   #4a7a8a;
    --panel:        rgba(4, 21, 41, 0.85);
    --panel-border: rgba(0, 194, 212, 0.15);
    --hairline:     rgba(148, 199, 214, 0.08);
    --glow:         0 0 24px rgba(0, 194, 212, 0.12);
}

/* 배경 — 바다 느낌 */
.stApp {
    background:
        radial-gradient(ellipse at 20% 0%, rgba(0,194,212,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 100%, rgba(0,168,150,0.07) 0%, transparent 50%),
        linear-gradient(180deg, #020d1a 0%, #041529 50%, #020d1a 100%);
    min-height: 100vh;
}
/* 필름 그레인 — 디지털 평면감 제거 (클릭 통과) */
.stApp::after {
    content: "";
    position: fixed; inset: 0;
    z-index: 2; pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    opacity: 0.035;
    mix-blend-mode: overlay;
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020d1a 0%, #041529 100%) !important;
    border-right: 1px solid rgba(0,194,212,0.12) !important;
}
[data-testid="stSidebar"] * { color: #c8e6f0 !important; }
[data-testid="stSidebarNav"]::before {
    content: "🌊 GVIDIA";
    display: block;
    padding: 20px 20px 10px;
    font-size: 20px; font-weight: 800;
    letter-spacing: -0.02em;
    color: #f2fbff;
    border-bottom: 1px solid rgba(0,194,212,0.10);
    margin-bottom: 10px;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    border-radius: 10px;
    transition: background 0.2s, transform 0.2s;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background: rgba(0,194,212,0.08) !important;
    transform: translateX(2px);
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(0,194,212,0.13) !important;
    border-left: 3px solid var(--cyan);
}

/* 메인 컨텐츠 — 배경 투명 + 초광폭 화면에서 가독 폭 제한 */
[data-testid="stAppViewContainer"] { background: transparent; }
[data-testid="stMainBlockContainer"],
section.main .block-container {
    max-width: 1560px;
    margin: 0 auto;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
}

/* 메트릭 카드 */
[data-testid="stMetric"] {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 16px;
    padding: 18px;
    box-shadow: var(--glow);
    backdrop-filter: blur(12px);
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 12px !important;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    color: var(--ink) !important;
    font-weight: 800 !important;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
}

/* 버튼 — 브랜드 시안 계열로 통일 */
.stButton > button,
[data-testid="stDownloadButton"] > button,
.stForm .stButton > button,
.stForm button[kind="primary"],
.stForm button[kind="secondary"] {
    border-radius: 11px;
    font-weight: 700;
    background: linear-gradient(135deg, #00505e, #008ea6);
    color: white !important;
    border: 1px solid rgba(0, 194, 212, 0.30) !important;
    box-shadow: 0 4px 16px rgba(0, 142, 166, 0.22);
    transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease, border-color 0.18s ease;
}
.stButton > button:hover,
[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-1px);
    filter: brightness(1.14);
    box-shadow: 0 8px 24px rgba(0, 194, 212, 0.28);
    border-color: rgba(0, 229, 255, 0.55) !important;
}
.stButton > button:active,
[data-testid="stDownloadButton"] > button:active {
    transform: translateY(0) scale(0.985);
    filter: brightness(0.98);
}
.stButton > button[kind="primary"],
.stForm button[kind="primary"] {
    background: linear-gradient(135deg, #00b7cb, #00e5ff) !important;
    color: #032330 !important;   /* 밝은 시안 위엔 어두운 텍스트로 대비 확보 */
    font-weight: 800;
}
/* 버튼 라벨(<p>)이 전역 p 색상에 덮이지 않도록 버튼 색을 상속 */
.stButton button p,
[data-testid="stDownloadButton"] button p {
    color: inherit !important;
    font-weight: inherit;
}
.stButton > button:focus-visible,
[data-testid="stDownloadButton"] > button:focus-visible,
a:focus-visible {
    outline: 2px solid rgba(0, 229, 255, 0.65) !important;
    outline-offset: 2px;
}

/* multiselect chip — 시안 계열 */
.stMultiSelect [data-baseweb="tag"],
.stMultiSelect [data-baseweb="tag"] > div,
.stMultiSelect [data-baseweb="tag"] button,
.stMultiSelect [data-baseweb="tag"] span {
    background: rgba(0, 194, 212, 0.13) !important;
    color: #d7f6fb !important;
    border-color: rgba(0, 229, 255, 0.30) !important;
}
.stMultiSelect [data-baseweb="tag"]:hover {
    background: rgba(0, 194, 212, 0.22) !important;
}
.stMultiSelect [data-baseweb="tag"] svg { fill: #d7f6fb !important; }
.stMultiSelect [data-baseweb="tag"] button { background: transparent !important; }

/* 데이터프레임 */
[data-testid="stDataFrame"] {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: var(--glow);
}
[data-testid="stDataFrame"] * { font-variant-numeric: tabular-nums; }

/* 텍스트 */
h1 { color: var(--ink) !important; font-weight: 800 !important; letter-spacing: -0.035em; }
h2, h3, h4 { color: var(--text) !important; letter-spacing: -0.02em; }
p, li, span { color: var(--text-muted); }
strong { color: var(--text); }
/* 한국어 단어 단위 줄바꿈 — Streamlit 기본 break-word 를 이기도록 !important */
.hero-sub, .ph-sub, .kpi-sub, .flow-d, .tip-row, .sec-title,
.hero-title, .ph-title, .ocean-card, .stCaption, [data-testid="stCaptionContainer"] {
    word-break: keep-all !important;
    overflow-wrap: break-word;
}

/* 인풋 */
.stTextInput input, .stSelectbox select, .stNumberInput input {
    background: rgba(4,21,41,0.8) !important;
    border: 1px solid rgba(0,194,212,0.2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
.stTextInput input:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 2px rgba(0,194,212,0.15) !important;
}

/* 탭 */
.stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    border-radius: 8px 8px 0 0;
    transition: color 0.18s;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text) !important; }
.stTabs [aria-selected="true"] {
    color: var(--cyan) !important;
    border-bottom: 2px solid var(--cyan) !important;
}

/* 알림 박스 */
.stInfo { background: rgba(0,194,212,0.07) !important; border-color: rgba(0,194,212,0.25) !important; color: var(--text) !important; }
.stSuccess { background: rgba(0,168,150,0.07) !important; border-color: rgba(0,168,150,0.3) !important; }
.stWarning { background: rgba(255,107,53,0.07) !important; border-color: rgba(255,107,53,0.3) !important; }
.stError { background: rgba(220,53,69,0.07) !important; border-color: rgba(220,53,69,0.3) !important; }

/* 스크롤바 */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,194,212,0.2); border-radius: 4px; }

/* 구분선 */
hr { border-color: var(--hairline) !important; }

/* Streamlit 기본 숨김 */
#MainMenu, footer, header { visibility: hidden; }

/* ── 카드 ─────────────────────────────────────────────── */
.ocean-card {
    position: relative;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 18px;
    padding: 20px 24px;
    box-shadow: var(--glow);
    backdrop-filter: blur(12px);
    margin-bottom: 12px;
    word-break: keep-all;
}

/* KPI 카드 — 아이콘 칩 + 라벨 + tabular 값 */
.kpi-head { display: flex; align-items: center; gap: 9px; margin-bottom: 12px; }
.kpi-ico {
    width: 30px; height: 30px; flex: 0 0 30px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px;
    border-radius: 9px;
    background: rgba(0, 194, 212, 0.10);
    border: 1px solid rgba(0, 194, 212, 0.18);
}
.kpi-label {
    font-size: 11px; font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.08em; text-transform: uppercase;
}
.kpi-value {
    font-size: 33px; font-weight: 800;
    color: var(--ink);
    line-height: 1.08; letter-spacing: -0.025em;
    font-variant-numeric: tabular-nums;
}
.kpi-sub { font-size: 12px; color: var(--text-faint); margin-top: 8px; }

/* 링크 카드 — 호버 리프트 + 화살표 어포던스 */
a.card-link { text-decoration: none !important; display: block; }
a.card-link .ocean-card {
    transition: transform 0.22s ease, border-color 0.22s ease,
                box-shadow 0.22s ease, background 0.22s ease;
}
a.card-link .ocean-card::after {
    content: "→";
    position: absolute; right: 20px; bottom: 16px;
    color: var(--cyan-2); font-size: 16px; font-weight: 700;
    opacity: 0; transform: translateX(-6px);
    transition: opacity 0.22s ease, transform 0.22s ease;
}
a.card-link .ocean-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0, 229, 255, 0.40);
    box-shadow: 0 12px 36px rgba(0, 194, 212, 0.16);
    background: rgba(6, 34, 64, 0.9);
}
a.card-link .ocean-card:hover::after { opacity: 1; transform: translateX(0); }

/* 섹션 헤더 */
.sec-head { display: flex; align-items: center; gap: 10px; margin: 30px 0 14px 0; }
.sec-bar {
    width: 3px; height: 20px; border-radius: 2px;
    background: linear-gradient(180deg, var(--cyan), var(--teal));
}
.sec-title { font-size: 17px; font-weight: 800; color: var(--text); letter-spacing: -0.01em; }

/* 페이지 헤더 (서브페이지 공통) */
.page-head { margin: 4px 0 22px 0; }
.ph-eyebrow {
    font-size: 11px; font-weight: 700; color: var(--cyan);
    letter-spacing: 0.14em; text-transform: uppercase;
    margin-bottom: 7px;
}
.ph-title {
    font-size: 27px; font-weight: 800; color: var(--ink);
    letter-spacing: -0.03em; line-height: 1.2; margin: 0;
}
.ph-sub { font-size: 13.5px; color: var(--text-muted); margin: 7px 0 0 0; max-width: 640px; }

/* 히어로 */
.hero-wrap {
    position: relative;
    background: linear-gradient(135deg, rgba(0,194,212,0.08) 0%, rgba(0,168,150,0.05) 100%);
    border: 1px solid rgba(0,194,212,0.15);
    border-radius: 20px;
    padding: 40px 44px 44px;
    margin-bottom: 28px;
    overflow: hidden;
}
.hero-dots {
    position: absolute; top: 0; right: 0; width: 46%; height: 100%;
    background-image: radial-gradient(circle, rgba(0,229,255,0.16) 1px, transparent 1px);
    background-size: 22px 22px;
    -webkit-mask-image: radial-gradient(ellipse at 100% 0%, black 0%, transparent 68%);
    mask-image: radial-gradient(ellipse at 100% 0%, black 0%, transparent 68%);
    pointer-events: none;
}
.hero-wave { position: absolute; left: 0; right: 0; bottom: -2px; pointer-events: none; }
.hero-eyebrow {
    position: relative;
    font-size: 11.5px; font-weight: 700; color: var(--cyan);
    letter-spacing: 0.14em; text-transform: uppercase;
    margin-bottom: 10px;
}
.hero-title {
    position: relative;
    font-size: clamp(28px, 3.2vw, 40px);
    font-weight: 800; color: var(--ink);
    letter-spacing: -0.04em; line-height: 1.16;
    margin: 0 0 12px 0;
}
.hero-sub {
    position: relative;
    font-size: 15px; color: var(--text-muted);
    margin: 0; max-width: 680px; line-height: 1.7;
    text-wrap: pretty;
}

/* 진행 흐름 스텝 (Home 운영 개요) */
.flow-step {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 13px 15px; border-radius: 13px;
    background: rgba(0,194,212,0.05);
    border: 1px solid rgba(0,194,212,0.10);
}
.flow-no {
    width: 24px; height: 24px; flex: 0 0 24px; margin-top: 1px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 8px;
    background: rgba(0,229,255,0.12);
    color: var(--cyan-2); font-size: 12px; font-weight: 800;
    font-variant-numeric: tabular-nums;
}
.flow-t { font-weight: 700; color: var(--text); font-size: 13.5px; margin-bottom: 3px; }
.flow-d { font-size: 12px; color: var(--text-muted); line-height: 1.55; }

/* 팁 행 + 페이지명 키 칩 */
.tip-row {
    display: flex; gap: 10px; align-items: baseline;
    color: #c8e6f0; font-size: 13.5px; font-weight: 500; line-height: 1.7;
}
.tip-row::before { content: "›"; color: var(--cyan-2); font-weight: 800; }
.tip-key {
    display: inline-block; padding: 1px 8px; border-radius: 6px;
    background: rgba(0,229,255,0.10); border: 1px solid rgba(0,229,255,0.22);
    color: #9fe8f2; font-size: 12px; font-weight: 700;
}

/* 랭킹 행 (관심지역 TOP N) */
.rank-row {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 4px;
    border-bottom: 1px solid var(--hairline);
}
.rank-row:last-child { border-bottom: none; }
.rank-no {
    width: 26px; height: 26px; flex: 0 0 26px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 8px; font-size: 12px; font-weight: 800;
    background: rgba(0,194,212,0.10); color: #9fe8f2;
    font-variant-numeric: tabular-nums;
}
.rank-row.top .rank-no { background: rgba(0,229,255,0.20); color: #eafcff; }
.rank-name { min-width: 64px; font-weight: 700; color: var(--text); font-size: 13.5px; }
.rank-bar {
    flex: 1; height: 6px; border-radius: 99px;
    background: rgba(148,199,214,0.08); overflow: hidden;
}
.rank-bar > div {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, #007c8f, #00c2d4);
}
.rank-count {
    min-width: 44px; text-align: right;
    font-size: 12.5px; color: var(--text-muted);
    font-variant-numeric: tabular-nums;
}
</style>
""", unsafe_allow_html=True)


def card(title: str, value: str, sub: str = "", icon: str = ""):
    ico = f'<span class="kpi-ico">{icon}</span>' if icon else ""
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
<div class="ocean-card kpi">
    <div class="kpi-head">{ico}<span class="kpi-label">{title}</span></div>
    <div class="kpi-value">{value}</div>
    {sub_html}
</div>
""", unsafe_allow_html=True)


def section(title: str, icon: str = ""):
    label = f"{icon} {title}" if icon else title
    st.markdown(f"""
<div class="sec-head">
    <div class="sec-bar"></div>
    <span class="sec-title">{label}</span>
</div>
""", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """서브페이지 공통 헤더 — eyebrow + 타이틀 + 설명."""
    label = f"{icon} {title}" if icon else title
    sub_html = f'<p class="ph-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
<div class="page-head">
    <div class="ph-eyebrow">{_EYEBROW}</div>
    <h1 class="ph-title">{label}</h1>
    {sub_html}
</div>
""", unsafe_allow_html=True)


def hero(title: str, subtitle: str, eyebrow: str = _EYEBROW):
    st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-dots"></div>
    <svg class="hero-wave" viewBox="0 0 1200 70" preserveAspectRatio="none" height="70">
        <path d="M0,42 C220,14 420,66 640,44 C860,22 1040,58 1200,36 L1200,70 L0,70 Z"
              fill="rgba(0,194,212,0.06)"></path>
        <path d="M0,56 C260,34 480,72 720,54 C940,38 1080,64 1200,50 L1200,70 L0,70 Z"
              fill="rgba(0,168,150,0.07)"></path>
    </svg>
    <div class="hero-eyebrow">{eyebrow}</div>
    <h1 class="hero-title">{title}</h1>
    <p class="hero-sub">{subtitle}</p>
</div>
""", unsafe_allow_html=True)
