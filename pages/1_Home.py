import pandas as pd
import streamlit as st

import config
from agents.alert_agent import get_active_alerts
from utils.alert_widget import inject_alerts
from utils.sst_stats import CONSEC_MIN, hot_stats, iter_region_csvs
from utils.style import card, hero, section


inject_alerts(get_active_alerts(demo=True))


@st.cache_data(ttl=300)
def load_stats():
    stats = {}
    news_path = config.PROCESSED_DIR / "disaster_db" / "disaster_events.csv"
    if news_path.exists():
        news_df = pd.read_csv(news_path, encoding="utf-8")
        stats["news_count"] = len(news_df)
        dates = pd.to_datetime(news_df["date"], errors="coerce").dropna()
        stats["news_period"] = (
            f"{dates.min().strftime('%Y.%m')} ~ {dates.max().strftime('%Y.%m')}"
            if not dates.empty
            else "2025.06 ~ 08"
        )
        stats["last_updated"] = dates.max().strftime("%Y-%m-%d") if not dates.empty else None
    else:
        stats["news_count"] = None
        stats["news_period"] = "2025.06 ~ 08"
        stats["last_updated"] = None

    sst_total, sst_regions, hot_regions = 0, 0, []
    for region, df in iter_region_csvs(config.DATA_DIR):
        sst_total += int(df["sst"].notna().sum())
        sst_regions += 1
        if hot_stats(df)["max_consec"] >= CONSEC_MIN:
            hot_regions.append(region)

    stats["sst_count"] = sst_total if sst_total > 0 else None
    stats["sst_regions"] = sst_regions
    stats["hot_regions"] = hot_regions
    return stats


s = load_stats()
news_count = f"{s['news_count']:,}건" if s["news_count"] else "없음"
sst_count = f"{s['sst_count']:,}건" if s["sst_count"] else "없음"
hot_count = f"{len(s['hot_regions'])}개" if s["hot_regions"] else "없음"
last_updated = s["last_updated"] or "미확인"


hero(
    "고수온 연안재해 AI·AX 대시보드",
    "관심지역 수집, 고수온 분석, 보고서 생성을 한 화면에서 연결하는 운영 대시보드입니다.",
)

section("현재 상태", "📊")
left, right = st.columns([1.15, 0.85])
with left:
    c1, c2 = st.columns(2)
    with c1:
        card("수집된 뉴스", news_count, s["news_period"], "📰")
    with c2:
        card("수집된 수온", sst_count, f"KHOA OPeNDAP · {s['sst_regions']}개 지역", "🌡️")
    c3, c4 = st.columns(2)
    with c3:
        card("고수온 위험 지역", hot_count, ", ".join(s["hot_regions"]) if s["hot_regions"] else "연속 3일 이상 지역", "⚠️")
    with c4:
        card("최신 갱신", last_updated, "분석 데이터 기준", "🕒")
with right:
    st.markdown(
        """
<div class="ocean-card" style="height:100%;">
  <div class="kpi-label" style="margin-bottom:8px;">운영 개요</div>
  <div style="font-size:19px;font-weight:800;color:#f2fbff;letter-spacing:-0.02em;margin-bottom:14px;">한눈에 보는 진행 흐름</div>
  <div style="display:grid;gap:12px;">
    <div class="flow-step">
      <div class="flow-no">1</div>
      <div>
        <div class="flow-t">뉴스 수집</div>
        <div class="flow-d">재난 관련 뉴스를 모아 관심 지역을 자동 추출합니다.</div>
      </div>
    </div>
    <div class="flow-step">
      <div class="flow-no">2</div>
      <div>
        <div class="flow-t">수온 분석</div>
        <div class="flow-d">관심 지역 SST를 모아 일별 추세와 고수온 상태를 확인합니다.</div>
      </div>
    </div>
    <div class="flow-step">
      <div class="flow-no">3</div>
      <div>
        <div class="flow-t">보고서 생성</div>
        <div class="flow-d">분석 결과를 Word와 PDF 보고서로 정리합니다.</div>
      </div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

section("바로가기", "🧭")


def _link_card(href: str, icon: str, title: str, desc: str):
    st.markdown(
        f"""
<a class="card-link" href="{href}" target="_self">
  <div class="ocean-card" style="min-height:170px;">
    <div class="kpi-head">
      <span class="kpi-ico">{icon}</span>
      <span style="font-size:14px;font-weight:700;color:#e8f4f8;">{title}</span>
    </div>
    <div style="font-size:12.5px;color:#7aacbf;line-height:1.65;">{desc}</div>
  </div>
</a>
""",
        unsafe_allow_html=True,
    )


g1, g2, g3 = st.columns(3)
with g1:
    _link_card("Disaster_Areas", "📰", "재난 지역 분석",
               "지역별 기사 분포와 관심 지역을 지도와 표로 확인합니다.")
with g2:
    _link_card("SST_Timeseries", "🌡️", "수온 시계열",
               "지역 SST를 인터랙티브 그래프로 보고 기간별 추세를 비교합니다.")
with g3:
    _link_card("Report", "📄", "보고서",
               "보고서 페이지에서 분석 문서를 생성하고 내려받을 수 있습니다.")

section("운영 팁", "✨")
st.markdown(
    """
<div class="ocean-card" style="padding:20px 26px;">
  <div style="display:grid;gap:9px;">
    <div class="tip-row"><span>파이프라인은 <span class="tip-key">Pipeline</span> 페이지에서 실행하는 것이 가장 안정적입니다.</span></div>
    <div class="tip-row"><span>시계열은 <span class="tip-key">SST Timeseries</span> 페이지에서 직접 확대하고 기간을 바꿀 수 있습니다.</span></div>
    <div class="tip-row"><span>경보는 오른쪽 상단 알림으로, LLM 어시스턴트는 오른쪽 가장자리 화살표로 열 수 있습니다.</span></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
