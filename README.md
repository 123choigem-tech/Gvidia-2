# 🌊 고수온 연안재해 AI·AX 대시보드 (team-gvidia)

재난(고수온) 뉴스를 크롤링해 관심지역(AOI)을 자동 도출하고, KHOA 위성
해수면온도(SST)·저염분 자료를 수집·분석해 경보와 보고서(Word/PDF/HWPX)까지
생성하는 통합 모니터링 플랫폼입니다.

2026 예보사업부 AI·AX 해커톤 출품작. (해커톤 스타터 킷 안내문은
`docs/STARTER_KIT_README.md` 로 옮겼습니다.)

---

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py          # → http://localhost:8501
```

LLM 어시스턴트는 **OpenRouter API(Nemotron)** 를 사용합니다 — 프로젝트 루트 `.env` 에 키 한 줄이면 됩니다:

```bash
# .env
OPENROUTER_API_KEY=sk-or-...
# OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free   # 선택(기본값)
```

보고서 AI 서술은 별도로 `ANTHROPIC_API_KEY` 가 필요합니다(.env 또는 secrets.toml).

뉴스 수집 API 키(네이버·공공데이터포털 등)는 `.env` 에 둡니다 — `config.py` 참고.

## 페이지 구성

| 페이지 | 내용 |
|---|---|
| Home | 수집 현황 KPI · 고수온 특보 알림 · 진행 흐름 (전 페이지 공통: 우측 LLM 어시스턴트 패널) |
| Disaster Areas | 재난 뉴스 목록 · 발생 위치 빈도 · 관심지역(AOI) 지도 |
| Heat Analysis | 지역별 SST 추세 · 고수온 기준(28℃) 분석 · 공간분포/저염분 시각자료 |
| Report | Word/PDF/HWPX 보고서 생성 · 다운로드 |
| Pipeline | 크롤링→관심지역→SST 수집→경보→보고서 원클릭 실행 |
| SST Timeseries | KHOA SST 일별 평균 인터랙티브 시계열 |

## 데이터 파이프라인 (CLI)

위성 원자료 다운로드부터 분석 산출물 재생성까지:

```bash
python src/download_khoa_sst.py            # KHOA SST 원자료(.nc) 다운로드
python src/download_lss.py                 # 저염분(LSS) 원자료 다운로드
python src/run_pipeline.py                 # 28℃ 추출→누적빈도→연속지속 일괄 분석
python src/sst_timeseries.py               # 일평균 시계열 CSV·PNG
python src/hot_lowsal.py                   # 고수온∩저염분 중첩 분석
python scripts/run_crawl.py --keyword 고수온  # 뉴스 크롤링(CLI)
python scripts/build_hwpx_report.py        # HWPX 보고서
```

`data/results/` 의 분석 산출물(NetCDF·PNG)은 위 스크립트로 재생성 가능하므로
git 에는 넣지 않습니다(.gitignore 참고).

## 폴더 구조

```
app.py               Streamlit 진입점
pages/               대시보드 페이지 6개
utils/               스타일·챗봇·알림·SST 통계 공용 모듈
agents/              뉴스→수집→경보→보고서 에이전트 (CLI: python -m agents.main_agent)
src/                 SST 분석 모듈 + 뉴스 크롤러 패키지(src/news/)
scripts/             수집·크롤링·보고서 CLI 스크립트
hwpx/                HWPX(한글) 보고서 템플릿·빌더
data/                지역 SST CSV · 뉴스 DB · 분석 산출물(results/)
docs/                해커톤 스타터 킷 안내문 등
```

> 참고: 뉴스 크롤링 경로는 현재 두 갈래가 있습니다 —
> 웹 앱(Pipeline 페이지)은 `agents/crawler_collection_agent`,
> CLI(`scripts/run_crawl.py`)는 `src/news/` 패키지를 사용합니다.
> `src/app.py` 는 독립 실행용 크롤러 데모(실험용)로 메인 앱과 별개입니다.

## 팀

**team-gvidia** — 2026 예보사업부 AI·AX 해커톤 · GeoSystem Research Corporation
