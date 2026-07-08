"""지역별 SST CSV 로딩·고수온 통계 공용 모듈.

기존에 pages/1_Home.py, pages/3_Heat_Analysis.py, agents/alert_agent.py,
agents/report_agent.py 네 곳에 같은 로직(CSV 스캔 → source 확인 →
28℃ 연속일수 계산)이 복붙되어 있던 것을 한 곳으로 모았다.

CSV 스키마: date, lat, lon, sst, source  (예: data/거제_20250601_20250831.csv)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = _ROOT / "data"

# 수집기별 source 표기가 달라(KHOA_OPeNDAP=위성 격자, KOSC=API 수집)
# 둘 다 유효한 지역 시계열로 취급한다.
REGION_SOURCES = {"KHOA_OPeNDAP", "KOSC"}

DEFAULT_THRESHOLD = 28.0
FREQ_MIN = 2    # 누적 기준 (sst_frequency.py 동일)
CONSEC_MIN = 3  # 연속 기준 (sst_persistence.py 동일)


def iter_region_csvs(data_dir: Path | str = DATA_DIR):
    """data_dir의 지역별 SST CSV를 (region, DataFrame)으로 순회한다.

    sst 컬럼이 없거나 source가 REGION_SOURCES 밖이면 건너뛴다.
    깨진 파일은 경고를 남기고 건너뛴다(조용히 삼키지 않음).
    """
    for f in sorted(Path(data_dir).glob("*_20*.csv")):
        region = f.stem.split("_")[0]
        try:
            df = pd.read_csv(f, encoding="utf-8", parse_dates=["date"])
        except Exception as exc:
            print(f"[sst_stats] {f.name} 읽기 실패 → 건너뜀: {exc}")
            continue
        if df.empty or "sst" not in df.columns:
            continue
        src = str(df.get("source", pd.Series([""])).iloc[0])
        if src not in REGION_SOURCES:
            continue
        yield region, df.sort_values("date").reset_index(drop=True)


def load_region_data(data_dir: Path | str = DATA_DIR) -> dict[str, pd.DataFrame]:
    """{지역명: 정렬된 DataFrame} 딕셔너리 반환."""
    return dict(iter_region_csvs(data_dir))


def hot_stats(df: pd.DataFrame, threshold: float = DEFAULT_THRESHOLD) -> dict:
    """고수온(≥threshold) 누적일수·최장연속·현재진행 streak 계산."""
    sst = df["sst"].dropna()
    hot = (sst.values >= threshold).tolist()

    freq = int(sum(hot))
    cur = max_c = 0
    for v in hot:
        cur = cur + 1 if v else 0
        max_c = max(max_c, cur)

    current_streak = 0
    for v in reversed(hot):
        if v:
            current_streak += 1
        else:
            break

    return {
        "avg": float(sst.mean()) if len(sst) else None,
        "max": float(sst.max()) if len(sst) else None,
        "hot_freq": freq,
        "max_consec": max_c,
        "current_streak": current_streak,
        "persist2": freq >= FREQ_MIN,
        "persist3": max_c >= CONSEC_MIN,
    }
