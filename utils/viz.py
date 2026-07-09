from __future__ import annotations  # py3.9 호환

import folium
import pandas as pd

# ── 차트 공통 팔레트 ────────────────────────────────────────────
# 카테고리(지역 식별) 팔레트 — 다크 서피스(#041529) 기준 CVD 검증 통과
# (인접 최소 ΔE 23.7, 전 슬롯 명도밴드·채도·대비 3:1 통과)
CATEGORICAL = [
    "#00a2bd",  # cyan (브랜드)
    "#199e70",  # aqua-green
    "#c98500",  # amber
    "#9085e9",  # violet
    "#e66767",  # red
    "#d55181",  # magenta
    "#d95926",  # orange
]
ACCENT = "#00a2bd"       # 단일 시리즈(명목형 바 등) 기본 색
ACCENT_SOFT = "rgba(0, 194, 212, 0.20)"  # 같은 변수의 보조 통계(범위·최대 등) — 주 시리즈 뒤로 후퇴
WARN = "#ff6b35"         # 임계값 등 경고 표시선

_GRID = "rgba(148, 199, 214, 0.10)"
_AXIS = "rgba(148, 199, 214, 0.25)"
_INK = "#a9cbd8"


def style_fig(fig, height: int | None = None, show_legend: bool | None = None):
    """Plotly Figure 에 다크 오션 공통 테마를 적용해 반환."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=CATEGORICAL,
        font=dict(family="Pretendard, Noto Sans KR, sans-serif", size=12.5, color=_INK),
        margin=dict(l=10, r=10, t=16, b=10),
        hoverlabel=dict(
            bgcolor="#062240",
            bordercolor="rgba(0,194,212,0.45)",
            font=dict(family="Pretendard, Noto Sans KR, sans-serif", size=12.5, color="#e8f4f8"),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(size=12, color=_INK),
        ),
    )
    fig.update_xaxes(showgrid=True, gridcolor=_GRID, linecolor=_AXIS, zeroline=False, tickfont=dict(size=11.5))
    fig.update_yaxes(showgrid=True, gridcolor=_GRID, linecolor=_AXIS, zeroline=False, tickfont=dict(size=11.5))
    if height is not None:
        fig.update_layout(height=height)
    if show_legend is not None:
        fig.update_layout(showlegend=show_legend)
    return fig


def make_frequency_map(freq_df: pd.DataFrame) -> folium.Map:
    tiles = "CartoDB dark_matter"  # 다크 테마와 톤 일치
    if freq_df.empty:
        return folium.Map(location=[35.5, 128.0], zoom_start=7, tiles=tiles)

    df = freq_df.dropna(subset=["lat", "lon"]).copy()
    if df.empty:
        return folium.Map(location=[35.5, 128.0], zoom_start=7, tiles=tiles)

    m = folium.Map(
        location=[df["lat"].mean(), df["lon"].mean()],
        zoom_start=7,
        tiles=tiles,
    )
    max_count = float(df["count"].max()) if not df.empty else 1.0
    for _, row in df.iterrows():
        ratio = float(row["count"]) / max_count if max_count else 0.0
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=max(5, float(row["count"]) / 4),
            color="rgba(0, 229, 255, 0.85)",
            weight=1.2,
            fill=True,
            fill_color="#00c2d4",
            fill_opacity=0.30 + 0.45 * ratio,
            tooltip=f"{row['location']}: {int(row['count'])}건",
        ).add_to(m)
    return m
