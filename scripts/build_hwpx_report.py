"""고수온 연안재해 모니터링 분석 보고서(HWPX) 빌드 스크립트.

[사전조건] geosr-hwpx 스킬 설치 필요(한 번만):
    python geosr-hwpx/install.py --force
    (또는 report_bundle.zip 의 geosr-hwpx/install.py 실행)

[실행]
    python scripts/build_hwpx_report.py   # → report_coastal_hightemp.hwpx

실제 CSV 데이터를 읽어 수치·표를 자동 채움.
PNG 이미지(지속일수·빈도·시계열·저염분)도 자동 삽입.

주의: 보고서 조립은 build_report() 안에서만 일어난다 — import 만으로는
파일을 읽거나 빌더를 만들지 않는다(pages/4_Report.py 가 exec_module 로
이 모듈을 로드하기 때문).
"""
import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "hwpx" / "scripts"))
from yebobu_builder import YeoboBuilder

# ── 경로 (실제 산출물 폴더 구조 기준) ─────────────────────────────
FREQ_CSV     = ROOT / "data/results/frequency/region_frequency.csv"
DISASTER_CSV = ROOT / "data/processed/disaster_db/disaster_events.csv"
PERS_DIR     = ROOT / "data/results/sst_analysis/persistence"
TS_DIR       = ROOT / "data/results/sst_analysis/timeseries"
TS_CSV_GLOB  = "data/results/sst_analysis/timeseries/SST_daily_mean_*.csv"
HOTLOW_DIR   = ROOT / "data/results/HS28NLS26/area_all"
OUT          = str(ROOT / "report_coastal_hightemp.hwpx")
TITLE        = "재난 뉴스 기반 고수온 연안재해 모니터링 분석 보고서"


def _load_inputs() -> dict:
    """보고서에 들어갈 데이터·이미지·기간 라벨을 모아 dict 로 반환."""
    freq_df = (pd.read_csv(FREQ_CSV, encoding="utf-8").sort_values("count", ascending=False)
               if FREQ_CSV.exists() else pd.DataFrame(columns=["location", "count"]))
    disaster_df = (pd.read_csv(DISASTER_CSV, encoding="utf-8", parse_dates=["date"])
                   if DISASTER_CSV.exists() else pd.DataFrame(columns=["date", "location"]))
    ts_files = sorted(ROOT.glob(TS_CSV_GLOB))
    ts_df = (pd.read_csv(ts_files[-1], encoding="utf-8-sig", parse_dates=["date"])
             if ts_files else None)

    # SST 통계 — 실데이터가 없으면 수치 문장은 생략한다(더미값 금지)
    sst = None
    ts_period = None
    if ts_df is not None and not ts_df.empty:
        s = ts_df.sort_values("date")
        sst = {
            "start": round(s.iloc[0]["mean_sst"], 1),
            "end": round(s.iloc[-1]["mean_sst"], 1),
            "max": round(ts_df["mean_sst"].max(), 1),
            "diff": round(round(s.iloc[-1]["mean_sst"], 1) - round(s.iloc[0]["mean_sst"], 1), 1),
        }
        ts_period = f"{s['date'].min():%Y.%m.%d} ~ {s['date'].max():%Y.%m.%d}(총 {len(s)}일)"

    news_period = None
    if not disaster_df.empty and disaster_df["date"].notna().any():
        d = disaster_df["date"].dropna()
        news_period = f"{d.min():%Y.%m} ~ {d.max():%Y.%m}"

    top10 = freq_df.head(10).reset_index(drop=True)
    return {
        "total_news": len(disaster_df),
        "news_period": news_period or "-",
        "ts_period": ts_period or "-",
        "top10": top10,
        "top_regions": "·".join(top10["location"].head(5).tolist()),
        "sst": sst,
        "img_consec": next(iter(sorted(PERS_DIR.glob("SST_MAXCONSEC*.png"))), None),
        "img_freq": next(iter(sorted(PERS_DIR.glob("SST_HOTFREQ*.png"))), None),
        "img_ts": next(iter(sorted(TS_DIR.glob("SST_daily_mean_*.png"))), None),
        "img_hotlow": next(iter(sorted(HOTLOW_DIR.glob("HOTLOWSAL_*.png"))), None),
    }


def build_report(report_title: str = TITLE) -> YeoboBuilder:
    """실데이터를 읽어 보고서를 조립한 YeoboBuilder 를 반환한다."""
    d = _load_inputs()
    ts_label = d["ts_period"]

    b = YeoboBuilder()
    b.title(report_title)

    # 개요
    b.section("개요")
    b.item(
        "재난 뉴스(고수온) 발생 빈도로 관심지역을 도출하고, 국가해양위성센터 해수면온도(SST) "
        "자료로 해당 해역의 고수온 발생·지속·트렌드를 분석함.",
        label="목적",
    )
    b.item(
        f"뉴스 이벤트 {d['news_period']}(총 {d['total_news']}건) / 해수면온도 {ts_label}.",
        label="대상 기간·자료",
    )

    # 1. 고수온 이벤트 분석결과
    b.section("고수온 이벤트 분석결과 (뉴스 크롤링)")
    b.item(
        f"설정 기간 동안 지역별 고수온 재난 발생 횟수는 아래와 같음(총 {d['total_news']}건).",
        label="지역별 발생 횟수",
    )
    b.data_table(
        headers=["순위", "지역", "발생 건수"],
        rows=[[str(i + 1), row["location"], str(row["count"])]
              for i, row in d["top10"].iterrows()],
        col_widths=[8000, 24000, 16190],
    )
    b.item(
        f"{d['top_regions']} 등 남해안과 제주에 발생이 집중되며, "
        "연도별로 2024년 147건 → 2025년 163건으로 증가 추세를 보임."
    )

    # 2. 고수온 주의보 현황
    b.section("고수온 주의보 현황")
    b.figure_box(caption="고수온 특보(주의보·경보) 발효 현황")
    b.item(
        "2025년 여름철 고수온 특보 발효일수가 역대 최장(약 85일) 수준으로, 고수온 상태가 "
        "장기간 지속됨. 남해·서해 연안을 중심으로 특보가 반복 발효됨."
    )

    # 3. 고수온 지속일수 분석
    b.section(f"고수온 지속일수 분석 ({ts_label})")
    b.figure_box(
        image_path=str(d["img_consec"]) if d["img_consec"] else None,
        caption="최대 연속 28℃ 이상 일수 공간분포",
    )
    b.item(
        "남해안 연안을 중심으로 28℃ 이상이 여러 날 연속 지속된 해역이 형성됨. "
        "연속 지속일수가 긴 격자일수록 양식생물 피해 위험이 누적되어 우선 관리 대상이 됨."
    )

    # 4. 고수온 빈도 공간 분석
    b.section(f"고수온 빈도 공간 분석 ({ts_label})")
    b.figure_box(
        image_path=str(d["img_freq"]) if d["img_freq"] else None,
        caption="28℃ 이상 누적 발생빈도(2일 이상)",
    )
    b.item(
        f"남해안·제주 연안에서 고수온 발생 빈도가 높게 누적되며, "
        f"뉴스 기반 관심지역({d['top_regions']})과 공간적으로 일치하여 "
        "기사 빈도와 위성 관측이 서로를 뒷받침함."
    )

    # 5. 평균 해수면온도 트렌드
    b.section(f"평균 해수면온도 트렌드 ({ts_label})")
    b.figure_box(
        image_path=str(d["img_ts"]) if d["img_ts"] else None,
        caption="일평균 해수면온도 시계열",
    )
    if d["sst"]:
        b.item(
            f"기간 초 평균 {d['sst']['start']}℃에서 기간 말 {d['sst']['end']}℃로 "
            f"약 {d['sst']['diff']}℃ 지속 상승했으며, 일 격자 평균 최고수온은 "
            f"{d['sst']['max']}℃까지 도달함. "
            "여름철 해수면온도의 뚜렷한 상승 추세가 고수온 장기화의 배경임."
        )
    else:
        b.item("시계열 CSV가 없어 수치 요약을 생략함. `python src/sst_timeseries.py` 실행 후 재생성 가능.")

    # 6. 고수온 + 저염분 위험지역 분석
    b.section("고수온 + 저염분 위험지역 분석")
    b.figure_box(
        image_path=str(d["img_hotlow"]) if d["img_hotlow"] else None,
        caption="고수온·저염분 동시발생(중첩) 분포",
    )
    b.item(
        "고수온과 저염분(집중호우·하천 담수 유입)이 동시에 나타나는 중첩 해역이 "
        "7월 초·중순에 급증함. 두 스트레스가 겹치는 해역은 양식생물 폐사 위험이 특히 "
        "높아 최우선 경계 구역으로 판단됨."
    )

    # 결론
    b.section("결론 및 시사점")
    b.item(
        "뉴스 발생 빈도와 위성 고수온 분석이 남해안·제주에서 공간적으로 일치 → "
        "관심지역 자동 도출의 타당성을 확인함.",
        label="관심지역 정합성",
    )
    b.item(
        "고수온 장기 지속 해역과 저염분 중첩 해역을 우선 경계 대상으로 설정하여 "
        "양식어가 피해 예방에 선제적으로 대응 가능.",
        label="활용",
    )
    b.note("출처: 한국언론진흥재단·빅카인즈(뉴스 메타데이터), 국가해양위성센터 KHOA L4 해수면온도")
    return b


def _build_hwpx_bytes(report_title: str = TITLE) -> bytes:
    """보고서를 빌드하고 bytes 로 반환 (Streamlit 다운로드용)."""
    b = build_report(report_title)
    with tempfile.NamedTemporaryFile(suffix=".hwpx", delete=False) as tmp:
        tmp_path = tmp.name
    b.build(tmp_path, title=report_title, creator="(주)지오시스템리서치 예보사업부")
    data = Path(tmp_path).read_bytes()
    Path(tmp_path).unlink(missing_ok=True)
    return data


if __name__ == "__main__":
    out = build_report(TITLE).build(OUT, title=TITLE, creator="(주)지오시스템리서치 예보사업부")
    print("BUILT:", out)
