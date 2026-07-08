"""서버측 LLM 백엔드 — OpenRouter(Nemotron) 전용. API 키가 서버를 떠나지 않는다.

이안류 프로젝트와 동일한 방식(OpenAI 호환 OpenRouter API)으로 호출한다.

키/모델 설정 (.env 또는 .streamlit/secrets.toml 또는 환경변수):
  OPENROUTER_API_KEY               (필수)
  OPENROUTER_MODEL 또는 AGENT_MODEL (선택 — nvidia/... 슬러그, 기본 nemotron-70b)
"""
from __future__ import annotations  # py3.9 호환

import os
from pathlib import Path
from typing import Iterator

import pandas as pd
import streamlit as st

_ROOT = Path(__file__).resolve().parent.parent
REGION_FREQ = _ROOT / "data" / "results" / "frequency" / "region_frequency.csv"
DISASTER_DB = _ROOT / "data" / "processed" / "disaster_db" / "disaster_events.csv"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "nvidia/llama-3.1-nemotron-70b-instruct"

SYSTEM_PROMPT = """당신은 '고수온 연안재해 모니터링 플랫폼'의 해양 기상 전문 AI 어시스턴트입니다.

역할:
- 제공된 수집 데이터(재난 뉴스, 관심지역 빈도, 해수면온도)를 해석합니다.
- 한국 남해안 연안의 고수온 피해, SST 분석, 양식장 피해에 대한 전문 지식을 갖고 있습니다.

원칙:
- 반드시 제공된 데이터에 근거해 답하고, 데이터에 없는 사실은 추측하지 마세요.
- 한국어로 간결하게 2~5문장으로 답하세요."""


def _load_env() -> None:
    """프로젝트 루트 .env 를 환경변수로 로드 (dotenv 없으면 수동 파싱)."""
    env_path = _ROOT / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        return
    except ImportError:
        pass
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _secret(name: str) -> str:
    """환경변수 우선, 없으면 st.secrets. secrets.toml 부재 시에도 죽지 않는다."""
    val = os.environ.get(name, "")
    if val:
        return val
    try:
        return st.secrets.get(name, "") or ""
    except Exception:  # StreamlitSecretNotFoundError 등
        return ""


def get_openrouter_key() -> str:
    _load_env()  # .env 가 나중에 추가돼도 재시작 없이 반영
    return _secret("OPENROUTER_API_KEY")


def get_model() -> str:
    m = _secret("OPENROUTER_MODEL")
    if not m:
        cand = _secret("AGENT_MODEL")  # 이안류 .env 슬러그 재사용
        m = cand if "/" in cand else ""
    return m or DEFAULT_MODEL


def provider_status() -> tuple[bool, str]:
    """(사용가능 여부, 상태 문구)"""
    if get_openrouter_key():
        short = get_model().split("/")[-1].split(":")[0]
        return True, f"{short} (OpenRouter) 연결됨"
    return False, "미설정 — `.env` 에 OPENROUTER_API_KEY 필요"


def available_providers() -> list[tuple[str, str]]:
    """chat_widget 이 사용하는 모델 선택 목록.

    키가 없으면 빈 목록을 반환해 UI 입력창만 비활성화하고,
    앱 자체는 계속 열리게 한다.
    """
    ok, status = provider_status()
    return [("openrouter", status)] if ok else []


def _load_context() -> str:
    parts = []
    if REGION_FREQ.exists():
        df = pd.read_csv(REGION_FREQ)
        parts.append(f"관심지역 빈도:\n{df.to_string(index=False)}")
    if DISASTER_DB.exists():
        df = pd.read_csv(DISASTER_DB)
        parts.append(f"재난 뉴스 건수: {len(df)}건\n최근 5건:\n{df.tail(5).to_string(index=False)}")
    return "\n\n".join(parts) if parts else "아직 수집된 데이터가 없습니다."


def ask_stream(question: str, history: list, provider: str | None = None) -> Iterator[str]:
    """질문에 대한 답을 스트리밍으로 생성 (OpenRouter/Nemotron)."""
    api_key = get_openrouter_key()
    if not api_key:
        yield "⚠️ OPENROUTER_API_KEY 가 설정되지 않았습니다. 프로젝트 루트 `.env` 에 추가하세요."
        return
    try:
        from openai import OpenAI
    except ImportError:
        yield "⚠️ openai 패키지가 설치되어 있지 않습니다. `pip install -r requirements.txt`를 실행하세요."
        return

    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
        default_headers={"X-Title": "Coastal High-SST Monitor"},  # ASCII only
    )
    messages = [{"role": "system",
                 "content": SYSTEM_PROMPT + "\n\n=== 현재 수집 데이터 ===\n" + _load_context()}]
    for m in history[-8:]:
        role = "assistant" if m["role"] == "assistant" else "user"
        messages.append({"role": role, "content": m["content"]})
    messages.append({"role": "user", "content": question})

    try:
        stream = client.chat.completions.create(
            model=get_model(), messages=messages, max_tokens=1024, stream=True,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as exc:
        yield f"⚠️ API 호출 실패: {exc}"


def ask(question: str, history: list) -> str:
    """비스트리밍 편의 함수."""
    return "".join(ask_stream(question, history))
