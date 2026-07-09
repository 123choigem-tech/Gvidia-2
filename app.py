"""엔트리포인트 — st.navigation 라우터.

첫 화면이 곧 Home 이다(별도 랜딩 페이지 없음). 공통 스타일과
LLM 패널은 여기서 한 번만 주입하고, 각 페이지는 내용만 그린다.
"""
import streamlit as st

from utils.chat_widget import inject
from utils.style import apply

st.set_page_config(
    page_title="고수온 연안재해 모니터링",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation([
    st.Page("pages/1_Home.py", title="Home", default=True),
    st.Page("pages/2_Disaster_Areas.py", title="Disaster Areas", url_path="Disaster_Areas"),
    st.Page("pages/3_Heat_Analysis.py", title="Heat Analysis", url_path="Heat_Analysis"),
    st.Page("pages/4_Report.py", title="Report", url_path="Report"),
    st.Page("pages/5_Pipeline.py", title="Pipeline", url_path="Pipeline"),
    st.Page("pages/5_SST_Timeseries.py", title="SST Timeseries", url_path="SST_Timeseries"),
])

apply()
inject()
pg.run()
