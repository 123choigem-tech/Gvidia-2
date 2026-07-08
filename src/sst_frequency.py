# -*- coding: utf-8 -*-
"""
sst_frequency.py — [요구사항5-①] 고수온 '누적 빈도' 정보 생산 기능

무엇을 하나:
  여러 날의 일별 고수온 파일(_HOT28.nc 의 hot_mask=1/0)을 같은 위치끼리 합산해,
  각 격자가 분석기간 중 '며칠' 28℃ 이상이었는지(= 누적 빈도)를 만든다.
  → 2일 이상 시기에 대해 동일공간 고수온이 얼마나 누적되는지 보는 지도.

만들어지는 NC 변수 (lat×lon 2D):
  - hot_freq      : 고수온이었던 누적 '일수' (0~N), 육지·결측은 NaN
  - persist2_mask : persist_min(기본 2)일 이상 누적되면 1, 아니면 0 (육지 NaN)
  - crs           : EPSG:4326 좌표계

초보자 안내:
  - 함수 run(hot_dir, out_dir) 하나면 NC + 해안선 배경 지도 PNG 를 만들어 줍니다.
  - 단독 실행:  python sst_frequency.py [고수온폴더] [출력폴더] [누적기준일]
  - 파일이 많아도(수십 일치) 한 장씩 읽어 누적하므로 메모리에 안전합니다(스트리밍).

전제: 고수온폴더 안에 sst_processing.py 가 만든 *_HOT28.nc 들이 있어야 함.
"""

import os

import numpy as np

try:
    from sst_gridutil import (list_hot_files, grid_from_file, read_hot_2d,
                              period_tag, wrap_2d, save_map_png, save_nc)
except ImportError:
    from src.sst_gridutil import (list_hot_files, grid_from_file, read_hot_2d,
                                  period_tag, wrap_2d, save_map_png, save_nc)

# 누적 빈도에서 '지속'으로 볼 최소 일수 (요구사항5: 2일 이상)
PERSIST_MIN_DAYS = 2

# CWD가 아니라 저장소 루트 기준 기본 경로
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_HOT_DIR = os.path.join(_REPO_ROOT, "data", "results", "sst_analysis", "sst_over28")
DEFAULT_OUT_DIR = os.path.join(_REPO_ROOT, "data", "results", "sst_analysis", "persistence")


# ---------------------------------------------------------------------------
# 결과 2D 배열 → NC Dataset 으로 포장 (스트리밍/일괄 경로 공용)
# ---------------------------------------------------------------------------
def _assemble(lat, lon, times, freq, persist, persist_min):
    return wrap_2d(
        lat, lon, times,
        {
            "hot_freq": (freq, {
                "long_name": "number of days with SST >= 28 C",
                "units": "days",
                "comment": "분석기간 중 28℃ 이상이었던 누적 일수 (동일 격자 기준)",
            }),
            "persist2_mask": (persist, {
                "long_name": f"persistent high-SST mask (>= {persist_min} days total)",
                "units": "1",
                "flag_values": "0, 1",
                "flag_meanings": "not_persistent persistent",
                "comment": f"누적 {persist_min}일 이상 고수온이면 1",
            }),
        },
        title=f"고수온(≥28℃) 누적 빈도 지도 ({persist_min}일 이상 지속 분석)",
        extra_attrs={"persist_min_days": persist_min, "analysis": "cumulative_frequency"},
    )


# ---------------------------------------------------------------------------
# 전체 실행: 파일을 한 장씩 읽어 누적 → NC + 지도 PNG (메모리 안전)
# ---------------------------------------------------------------------------
def run(hot_dir: str = DEFAULT_HOT_DIR, out_dir: str = DEFAULT_OUT_DIR,
        persist_min: int = PERSIST_MIN_DAYS, make_png: bool = True) -> dict:
    """누적 빈도 NC 와 해안선 배경 지도 PNG 를 만든다. 결과 요약 dict 를 돌려준다."""
    paths = list_hot_files(hot_dir)
    lat, lon = grid_from_file(paths[0])

    freq = None       # 격자별 고수온 누적 일수 (정수 누적)
    sea = None        # 한 번이라도 값이 있었던 '바다' 격자
    times = []
    expected_shape = (lat.size, lon.size)
    for p in paths:
        t, arr = read_hot_2d(p)
        if arr.shape != expected_shape:
            print(f"  [경고] {os.path.basename(p)}: 격자 {arr.shape} != 기준 {expected_shape} → 건너뜀")
            continue
        times.append(t)
        finite = np.isfinite(arr)
        hot = (arr == 1.0)
        if freq is None:
            freq = hot.astype("int32")
            sea = finite.copy()
        else:
            freq += hot
            sea |= finite
        del arr

    n_days = len(times)
    if n_days < persist_min:
        print(f"  [주의] 분석 일수({n_days})가 누적 기준({persist_min}일)보다 적습니다.")

    freqf = freq.astype("float32")
    freqf[~sea] = np.nan
    persist = np.where(sea, (freqf >= persist_min), np.nan).astype("float32")

    ds = _assemble(lat, lon, times, freqf, persist, persist_min)

    _, tag = period_tag(times)
    nc_path = os.path.join(out_dir, f"SST_HOTFREQ_28C_{tag}.nc")
    save_nc(ds, nc_path)

    summary = {
        "feature": "누적빈도(cumulative frequency)",
        "n_days": n_days,
        "period": f"{ds.attrs['time_coverage_start']} ~ {ds.attrs['time_coverage_end']}",
        "nc": nc_path,
        "sea_cells": int(np.isfinite(freqf).sum()),
        "persist_min": persist_min,
        "persist_cells": int(np.nansum(persist)),
        "max_freq_observed": int(np.nanmax(freqf)) if np.isfinite(freqf).any() else 0,
    }

    if make_png:
        png = os.path.join(out_dir, f"SST_HOTFREQ_28C_{tag}.png")
        save_map_png(ds, "hot_freq", png,
                     title=f"Cumulative high-SST frequency (>=28C)  {summary['period']}",
                     cmap="YlOrRd", label="days >= 28C", vmin=0, vmax=n_days)
        summary["png"] = png

    return summary


if __name__ == "__main__":
    import sys

    hot_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOT_DIR
    out_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT_DIR
    p_min = int(sys.argv[3]) if len(sys.argv) > 3 else PERSIST_MIN_DAYS

    print("=== [요구사항5-①] 고수온 누적 빈도 정보 생산 ===")
    print(f"입력: {hot_dir}  →  출력: {out_dir}  (누적 기준 {p_min}일 이상)\n")

    s = run(hot_dir, out_dir, persist_min=p_min)

    print(f"분석 기간: {s['period']}  (총 {s['n_days']}일)")
    print(f"바다 격자 수: {s['sea_cells']:,}")
    print(f"  · {s['persist_min']}일 이상 누적 고수온 격자: {s['persist_cells']:,}")
    print(f"  · 관측된 최대 누적 일수: {s['max_freq_observed']}일")
    print(f"\n[NC]   → {s['nc']}")
    if "png" in s:
        print(f"[지도] → {s['png']}")
    print("\n완료.")
