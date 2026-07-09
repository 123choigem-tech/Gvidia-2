# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.style import page_header
from utils.viz import style_fig, ACCENT, ACCENT_SOFT

page_header("SST 시계열", "KHOA SST 일별 평균을 웹에서 직접 확인하는 인터랙티브 시계열 뷰입니다.", "📈")

_ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = _ROOT / "data" / "results" / "sst_analysis" / "timeseries"


@st.cache_data(ttl=300)
def load_latest_csv():
    csvs = sorted(CSV_DIR.glob("SST_daily_mean_*.csv"))
    if not csvs:
        return None, None
    path = csvs[-1]
    df = pd.read_csv(path, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    return df, path


df, csv_path = load_latest_csv()

if df is None:
    st.warning(
        "시계열 CSV가 아직 없습니다.\n\n"
        "먼저 아래 명령으로 데이터를 만들어 주세요.\n"
        "```bash\npython src/sst_timeseries.py\n```"
    )
    st.stop()

st.caption(
    f"데이터: `{csv_path.name}` · 총 {len(df)}일 "
    f"({df['date'].min():%Y-%m-%d} ~ {df['date'].max():%Y-%m-%d})"
)

dmin, dmax = df["date"].min().date(), df["date"].max().date()
c1, c2 = st.columns([3, 1])
with c1:
    sel = st.date_input(
        "기간 선택",
        value=(dmin, dmax),
        min_value=dmin,
        max_value=dmax,
    )
with c2:
    show_max = st.checkbox("최고 SST 표시", value=True)

if isinstance(sel, (list, tuple)) and len(sel) == 2:
    start, end = sel
else:
    start, end = dmin, dmax

with st.expander("축 설정"):
    oc1, oc2 = st.columns(2)
    ymin = oc1.number_input("Y축 최소", value=15.0, step=1.0)
    ymax = oc2.number_input("Y축 최대", value=36.0, step=1.0)

mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)
d = df.loc[mask].sort_values("date")
if d.empty:
    st.error("선택한 기간에 데이터가 없습니다.")
    st.stop()

m1, m2, m3, m4 = st.columns(4)
m1.metric("선택 일수", f"{len(d)}일")
m2.metric("평균 SST", f"{d['mean_sst'].mean():.2f} °C")
hi = d.loc[d["mean_sst"].idxmax()]
lo = d.loc[d["mean_sst"].idxmin()]
m3.metric("최고 평균 SST", f"{hi['mean_sst']:.2f} °C", help=f"{hi['date']:%Y-%m-%d}")
m4.metric("최저 평균 SST", f"{lo['mean_sst']:.2f} °C", help=f"{lo['date']:%Y-%m-%d}")

fig = go.Figure()
if show_max and "max_sst" in d.columns:
    # 같은 변수(SST)의 보조 통계 — 동일 색상 계열의 옅은 톤으로 후퇴
    fig.add_trace(
        go.Bar(
            x=d["date"],
            y=d["max_sst"],
            name="일별 최고 SST",
            marker_color=ACCENT_SOFT,
            hovertemplate="최고 %{y:.2f}°C<extra></extra>",
        )
    )
fig.add_trace(
    go.Scatter(
        x=d["date"],
        y=d["mean_sst"],
        mode="lines+markers",
        name="일별 평균 SST",
        line=dict(color=ACCENT, width=2.4),
        marker=dict(size=6, color=ACCENT, line=dict(width=1, color="#041529")),
        hovertemplate="평균 %{y:.2f}°C<extra></extra>",
    )
)

fig.update_layout(
    title=dict(
        text=f"KHOA 영역 평균 일별 SST ({start:%Y-%m-%d} ~ {end:%Y-%m-%d})",
        font=dict(size=14),
    ),
    xaxis_title=None,
    yaxis_title="해수면온도 (°C)",
    yaxis=dict(range=[ymin, ymax]),
    hovermode="x unified",
)
style_fig(fig, height=520)
fig.update_layout(margin=dict(l=20, r=20, t=56, b=20), bargap=0.35)
fig.update_xaxes(tickformat="%m-%d")

st.plotly_chart(fig, use_container_width=True)

with st.expander("선택 기간 데이터"):
    st.dataframe(d.reset_index(drop=True), use_container_width=True)
    st.download_button(
        "선택 기간 CSV 다운로드",
        data=d.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"SST_daily_mean_{start:%Y%m%d}_{end:%Y%m%d}.csv",
        mime="text/csv",
    )
