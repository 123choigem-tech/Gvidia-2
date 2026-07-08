import os

import streamlit as st

import config
from agents.alert_agent import get_active_alerts
from utils.alert_widget import inject_alerts
from utils.chat_widget import inject
from utils.style import apply

st.set_page_config(page_title="Report", page_icon="📄", layout="wide")
apply()
inject()
inject_alerts(get_active_alerts(demo=True))

st.title("📄 보고서 생성")
st.caption("실제 데이터와 보고서 생성 agent를 연결해 Word/PDF 보고서를 만듭니다.")

DISASTER_DB = config.PROCESSED_DIR / "disaster_db" / "disaster_events.csv"
SUMMARY_DIR = config.DATA_DIR / "results" / "summary"

if not DISASTER_DB.exists():
    st.warning(
        f"재난 뉴스 데이터가 없습니다 (`{DISASTER_DB.name}`). "
        "Pipeline 페이지에서 크롤링을 먼저 실행하면 보고서에 뉴스 통계가 포함됩니다."
    )


def _has_anthropic_key() -> bool:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return True
    try:
        return bool(st.secrets.get("ANTHROPIC_API_KEY", ""))
    except Exception:
        return False


st.subheader("보고서 생성")

col_a, col_b = st.columns([1, 1])
with col_a:
    title = st.text_input("보고서 제목", value="2025년 하절기 고수온 연안재해 분석 보고서")
    threshold = st.slider("고수온 기준(℃)", 24.0, 32.0, 28.0, 0.5)
    top_n = 20
with col_b:
    fmt = st.radio("출력 형식", ["both", "docx", "pdf", "hwpx"], horizontal=True)
    ai_available = _has_anthropic_key()
    use_ai = st.checkbox("AI 서술 포함", value=ai_available, disabled=not ai_available)
    if not ai_available:
        st.caption("AI 서술은 `ANTHROPIC_API_KEY` 설정 시에만 생성됩니다.")
    st.caption("hwpx 선택 시 geosr-hwpx 스킬이 설치된 경우에만 생성됩니다.")

selected_sections = ["overview", "news", "consec_map", "freq_map", "timeseries", "sst_stats", "hotmap", "conclusion"]

if st.button("보고서 생성", type="primary", use_container_width=True):
    try:
        with st.spinner("보고서 생성 중..."):
            result = {"docx": None, "pdf": None, "hwpx": None, "filename_stem": "report"}

            if fmt in ("docx", "pdf", "both"):
                from agents.report_agent import run as report_run
                r = report_run(
                    title=title,
                    threshold=threshold,
                    include_sections=selected_sections,
                    top_n_regions=top_n,
                    fmt=fmt,
                    output_dir=str(SUMMARY_DIR),
                    use_ai=use_ai,
                )
                result.update(r)

            if fmt == "hwpx":
                import sys, importlib.util
                sys.path.insert(0, str(config.ROOT / "hwpx" / "scripts"))
                try:
                    spec = importlib.util.spec_from_file_location(
                        "build_hwpx_report", config.ROOT / "scripts" / "build_hwpx_report.py"
                    )
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    hwpx_bytes = mod._build_hwpx_bytes(title)
                    out_path = SUMMARY_DIR / f"{result['filename_stem']}.hwpx"
                    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
                    out_path.write_bytes(hwpx_bytes)
                    result["hwpx"] = {"bytes": hwpx_bytes, "path": str(out_path)}
                except ImportError:
                    st.warning("geosr-hwpx 스킬이 설치되지 않아 HWPX를 생성할 수 없습니다. "
                               "`python geosr-hwpx/install.py --force`를 먼저 실행하세요.")

        st.session_state["report_result"] = result
        st.success("보고서 생성이 완료되었습니다.")
    except Exception as e:
        st.error(f"보고서 생성 실패: {e}")

if "report_result" in st.session_state:
    result = st.session_state["report_result"]
    stem = result.get("filename_stem", "report")
    st.markdown("---")
    st.subheader("다운로드")
    d1, d2, d3 = st.columns(3)
    if result.get("docx") and result["docx"].get("bytes"):
        d1.download_button(
            "⬇ Word (.docx)",
            result["docx"]["bytes"],
            file_name=f"{stem}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    if result.get("pdf") and result["pdf"].get("bytes"):
        d2.download_button(
            "⬇ PDF",
            result["pdf"]["bytes"],
            file_name=f"{stem}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    if result.get("hwpx") and result["hwpx"].get("bytes"):
        d3.download_button(
            "⬇ 한글 (.hwpx)",
            result["hwpx"]["bytes"],
            file_name=f"{stem}.hwpx",
            mime="application/octet-stream",
            use_container_width=True,
        )

