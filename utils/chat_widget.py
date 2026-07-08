"""우측 슬라이드 LLM 어시스턴트 패널 (서버측 호출 — 키/구독이 서버를 떠나지 않음).

- 화면 오른쪽에 대화형 패널이 고정되고, 가장자리 화살표(◀/▶)로 열고 닫는다
  (좌우 슬라이드 애니메이션).
- 메시지 영역이 화면 높이를 꽉 채우고 입력창은 항상 하단에 붙는다.
- 백엔드는 utils/chatbot.ask_stream() — 로컬 Claude Code CLI 우선,
  없으면 OpenAI API 폴백.
- inject() 시그니처는 그대로라 각 페이지 수정이 필요 없다.
"""
import html as _html

import streamlit as st

from utils.chatbot import ask_stream, available_providers

_PANEL_W = 400  # px — utils/alert_widget._PANEL_W 와 동일하게 유지


def _bubble(text: str, who: str) -> str:
    body = _html.escape(text).replace("\n", "<br>")
    return f'<div class="{"cu" if who == "user" else "cb"}">{body}</div>'


def _send():
    q = (st.session_state.get("chat_input") or "").strip()
    if q:
        st.session_state["chat_pending"] = q
        st.session_state["chat_input"] = ""


def _css(open_: bool, top_offset: int = 172):
    tx = "0" if open_ else "105%"
    right = f"{_PANEL_W}px" if open_ else "0px"
    st.markdown(f"""
<style>
/* ── 우측 슬라이드 LLM 패널 ─────────────────────────────── */
.st-key-chat_panel {{
    position: fixed !important;
    top: 0 !important; right: 0 !important;
    width: {_PANEL_W}px !important; height: 100vh !important;
    background: linear-gradient(180deg, #041529 0%, #020d1a 100%) !important;
    border-left: 1px solid rgba(0,194,212,0.25) !important;
    box-shadow: -8px 0 40px rgba(0,0,0,0.55) !important;
    z-index: 999990 !important;
    padding: 16px 16px 12px !important;
    transform: translateX({tx});
    transition: transform .35s cubic-bezier(.4,0,.2,1) !important;
    overflow: hidden !important;
}}
/* 패널 내부 세로 간격을 줄여 입력창이 하단에 붙도록 */
.st-key-chat_panel [data-testid="stVerticalBlock"] {{ gap: 0.55rem !important; }}
.chat-title {{
    font-weight: 800; font-size: 16px; color: #e8f4f8;
    font-family: 'Pretendard','Noto Sans KR',sans-serif;
}}
.chat-status {{ font-size: 11px; color: #7aacbf; }}

/* 모델 선택 드롭다운 — 컴팩트하게 */
.st-key-chat_provider [data-testid="stSelectbox"] > div {{ min-height: 34px !important; }}

/* 메시지 영역 — 화면 높이를 꽉 채우고 내부 스크롤.
   st.container(height=...)의 560px 은 부모 stLayoutWrapper 에 걸리므로
   그 래퍼의 높이를 뷰포트 기준으로 재정의한다. */
div[data-testid="stLayoutWrapper"]:has(> div.st-key-chat_msgs) {{
    /* 래퍼는 flex 아이템이라 주축 크기는 flex-basis 가 결정한다 */
    height: calc(100vh - {top_offset}px) !important;
    flex: 0 0 calc(100vh - {top_offset}px) !important;
}}
div[data-testid="stVerticalBlock"].st-key-chat_msgs {{
    background: rgba(0,194,212,0.03) !important;
    border: 1px solid rgba(0,194,212,0.10) !important;
    border-radius: 12px !important;
    padding: 10px !important;
    overflow-y: auto !important;
}}
.cu {{
    background: linear-gradient(135deg,#005f6e,#00a896); color: #fff;
    padding: 9px 13px; border-radius: 14px 14px 4px 14px;
    font-size: 13px; line-height: 1.6; word-break: keep-all;
    margin: 5px 0 5px auto; max-width: 86%; width: fit-content;
    font-family: 'Pretendard','Noto Sans KR',sans-serif;
}}
.cb {{
    background: rgba(0,194,212,0.07); color: #c8e6f0;
    border: 1px solid rgba(0,194,212,0.10);
    padding: 9px 13px; border-radius: 14px 14px 14px 4px;
    font-size: 13px; line-height: 1.6; word-break: keep-all;
    margin: 5px auto 5px 0; max-width: 86%; width: fit-content;
    font-family: 'Pretendard','Noto Sans KR',sans-serif;
}}

/* 입력 행 — 하단 고정 느낌으로 여백 최소화 */
.st-key-chat_send button {{
    height: 40px !important; min-height: 40px !important;
    background: linear-gradient(135deg,#005f6e,#00c2d4) !important;
    color: #fff !important; border: none !important; font-weight: 700 !important;
}}

/* ── 가장자리 토글 화살표 ────────────────────────────────── */
.st-key-chat_toggle_box {{
    position: fixed !important;
    top: 50% !important; right: {right} !important;
    transform: translateY(-50%) !important;
    z-index: 999991 !important;
    width: 34px !important;
    transition: right .35s cubic-bezier(.4,0,.2,1) !important;
}}
.st-key-chat_toggle_box button {{
    width: 34px !important; height: 88px !important; min-height: 88px !important;
    padding: 0 !important;
    border-radius: 12px 0 0 12px !important;
    background: linear-gradient(135deg,#005f6e,#00c2d4) !important;
    color: #fff !important; border: none !important;
    font-size: 15px !important; font-weight: 700 !important;
    box-shadow: -4px 0 18px rgba(0,194,212,0.35) !important;
}}
.st-key-chat_toggle_box button:hover {{ filter: brightness(1.15); }}
</style>
""", unsafe_allow_html=True)


def inject():
    open_ = st.session_state.setdefault("chat_open", False)
    history = st.session_state.setdefault("chat_history", [])
    providers = available_providers()
    ok = bool(providers)

    # 모델 드롭다운이 있으면 그만큼 메시지 영역을 줄인다
    _css(open_, top_offset=218 if len(providers) > 1 else 172)

    # 가장자리 토글 화살표 — 닫혀 있으면 ◀(열기), 열려 있으면 ▶(닫기)
    with st.container(key="chat_toggle_box"):
        if st.button("◀" if not open_ else "▶", key="chat_toggle",
                     help="LLM 패널 열기/닫기"):
            st.session_state["chat_open"] = not open_
            st.rerun()

    # 패널은 항상 렌더하고 CSS transform 으로 슬라이드 (열림/닫힘 애니메이션)
    with st.container(key="chat_panel"):
        status = providers[0][1] if len(providers) == 1 else (
            "" if providers else "미설정 — claude CLI 로그인 또는 OPENROUTER/OPENAI API 키 필요")
        st.markdown(
            f'<div class="chat-title">🌊 고수온 LLM 어시스턴트</div>'
            + (f'<div class="chat-status">{"🟢" if ok else "🔴"} {status}</div>' if status else ""),
            unsafe_allow_html=True,
        )

        # 백엔드가 여러 개면 모델 선택 드롭다운 표시
        if len(providers) > 1:
            labels = dict(providers)
            with st.container(key="chat_provider"):
                st.selectbox(
                    "모델", options=[p for p, _ in providers],
                    format_func=lambda p: "🧠 " + labels[p],
                    key="chat_provider_sel", label_visibility="collapsed",
                )

        with st.container(height=560, key="chat_msgs"):
            if not history:
                st.markdown(_bubble(
                    "안녕하세요! 고수온 연안재해 LLM 어시스턴트입니다.\n"
                    "관심지역, 수온 데이터, 분석 결과에 대해 질문하세요.", "bot"),
                    unsafe_allow_html=True)
            for m in history:
                st.markdown(_bubble(m["content"], "user" if m["role"] == "user" else "bot"),
                            unsafe_allow_html=True)

            pending = st.session_state.pop("chat_pending", None)
            if pending:
                st.markdown(_bubble(pending, "user"), unsafe_allow_html=True)
                answer = st.write_stream(ask_stream(
                    pending, history,
                    provider=st.session_state.get("chat_provider_sel")))
                cleaned = str(answer).replace("<br>", "\n").strip()
                history.append({"role": "user", "content": pending})
                history.append({"role": "assistant", "content": cleaned})
                st.rerun()

        col_in, col_btn = st.columns([4.2, 1], gap="small")
        with col_in:
            st.text_input(
                "질문", key="chat_input", on_change=_send,
                placeholder="질문 입력 후 Enter" if ok else "LLM 백엔드 미설정",
                label_visibility="collapsed", disabled=not ok,
            )
        with col_btn:
            st.button("➤", key="chat_send", on_click=_send,
                      disabled=not ok, use_container_width=True)
