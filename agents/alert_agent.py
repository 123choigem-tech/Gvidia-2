# -*- coding: utf-8 -*-
"""
alert_agent.py — 고수온 지속 조건 감지 알림 서브에이전트

조건:
  - 🟡 주의보: 현재 1일↑ 연속 감지
  - 🔴 경보:   현재 3일↑ 연속 지속

공개 함수:
  check(threshold=28.0) -> list[dict]
    각 지역별 알림 레벨·지속일수 반환

  get_active_alerts(threshold=28.0, demo=False) -> list[dict]
    주의 이상 지역만 필터링해서 반환.
    demo=True 면 현재 streak이 없어도 과거 최장 streak 기준으로
    레벨을 산출하되, 결과에 demo=True 플래그를 남긴다(표시 문구 구분용).
"""

from __future__ import annotations

from utils.sst_stats import CONSEC_MIN, DATA_DIR, DEFAULT_THRESHOLD, iter_region_csvs

THRESHOLD = DEFAULT_THRESHOLD


def check(threshold: float = THRESHOLD) -> list[dict]:
    """전체 지역 고수온 감지 결과 반환."""
    from utils.sst_stats import hot_stats

    results = []
    for region, df in iter_region_csvs(DATA_DIR):
        try:
            stat = hot_stats(df, threshold)
            latest_sst = float(df["sst"].iloc[-1]) if not df.empty else None
            latest_date = str(df["date"].iloc[-1])[:10] if not df.empty else None

            streak = stat["current_streak"]
            if streak >= CONSEC_MIN:
                level = "alarm"     # 🔴 경보  (3일↑ 연속)
            elif streak >= 1:
                level = "advisory"  # 🟡 주의보 (1~2일 연속)
            else:
                level = "normal"

            results.append({
                "region": region,
                "hot_freq": stat["hot_freq"],
                "max_consec": stat["max_consec"],
                "current_streak": streak,
                "level": level,
                "latest_sst": latest_sst,
                "latest_date": latest_date,
                "threshold": threshold,
                "demo": False,
            })
        except Exception as exc:
            print(f"[alert_agent] {region} 처리 실패 → 건너뜀: {exc}")
            continue
    return results


def get_active_alerts(threshold: float = THRESHOLD, demo: bool = False) -> list[dict]:
    """주의보/경보 지역만 반환, 경보 우선 정렬.

    demo=True: 현재 streak이 없어도 과거 최장 streak(max_consec) 기준으로
    레벨을 산출해 화면에서 결과를 확인할 수 있게 한다. 이때 current_streak을
    조작하지 않고 demo=True 플래그만 남기므로, 표시 측(alert_widget)이
    '과거 최장 N일' 문구로 구분해 보여준다.
    """
    all_r = check(threshold)

    if demo:
        for r in all_r:
            if r["current_streak"] == 0 and r["level"] == "normal":
                if r["max_consec"] >= CONSEC_MIN:
                    r["level"] = "alarm"
                    r["demo"] = True
                elif r["max_consec"] >= 1:
                    r["level"] = "advisory"
                    r["demo"] = True

    active = [r for r in all_r if r["level"] != "normal"]
    active.sort(key=lambda x: (
        0 if x["level"] == "alarm" else 1,
        -(x["current_streak"] or x["max_consec"]),
    ))
    return active


if __name__ == "__main__":
    alerts = check()
    for a in alerts:
        icon = "🔴" if a["level"] == "alarm" else ("🟡" if a["level"] == "advisory" else "✅")
        print(f"{icon} {a['region']}: 누적 {a['hot_freq']}일, 최장연속 {a['max_consec']}일, "
              f"현재streak {a['current_streak']}일 | 최근 {a['latest_sst']}°C ({a['latest_date']})")
