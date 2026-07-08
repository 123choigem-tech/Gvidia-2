# -*- coding: utf-8 -*-
"""
alert_widget.py — 고수온 특보 통합 알림 카드

inject_alerts(alerts) 를 각 페이지에서 호출하면 우상단에 알림 '카드 한 장'이 표시된다.
  - 지역별 토스트를 따로 띄우지 않고 한 카드에 목록으로 묶는다 (닫기도 한 번).
  - 12초 후 자동으로 사라진다. ✕ 로 닫으면 같은 내용은 다시 띄우지 않는다(localStorage).
  - LLM 패널(우측)이 열려 있으면 패널을 가리지 않도록 왼쪽으로 비켜난다.

alerts: alert_agent.get_active_alerts() 반환값
"""

from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components

_PANEL_W = 400  # utils/chat_widget._PANEL_W 와 동일


def inject_alerts(alerts: list[dict]) -> None:
    """고수온 감지 알림을 우상단 통합 카드로 표시."""
    if not alerts:
        return

    alerts_json = json.dumps(alerts, ensure_ascii=False)
    # LLM 패널이 열려 있으면 그 왼쪽에 표시 (패널을 가리지 않음)
    right_px = _PANEL_W + 36 if st.session_state.get("chat_open") else 20

    components.html(f"""<!DOCTYPE html>
<html><head></head><body>
<script>
(function() {{
  var doc = window.parent.document;
  var alerts = {alerts_json};
  var RIGHT = {right_px};
  var sig = JSON.stringify(alerts);

  // 사용자가 ✕ 로 닫은 알림(같은 내용)은 다시 띄우지 않는다
  try {{
    if (window.parent.localStorage.getItem('hwaDismissed') === sig) return;
  }} catch (e) {{}}

  var existing = doc.getElementById('hwa-card');
  if (existing) {{
    if (existing.dataset.sig === sig) {{
      existing.style.right = RIGHT + 'px';   // 패널 여닫이에 맞춰 위치만 갱신
      return;
    }}
    existing.remove();                        // 내용이 바뀌면 새로 표시
  }}

  if (!doc.getElementById('hwa-style')) {{
    var style = doc.createElement('style');
    style.id = 'hwa-style';
    style.textContent = `
      #hwa-card {{
        position: fixed !important;
        top: 64px !important;
        width: 330px !important;
        z-index: 999900 !important;          /* LLM 패널(999990)보다 아래 */
        background: linear-gradient(180deg, #041529 0%, #020d1a 100%) !important;
        border: 1px solid rgba(0,194,212,0.25) !important;
        border-radius: 14px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.55) !important;
        font-family: 'Pretendard','Noto Sans KR',sans-serif !important;
        overflow: hidden !important;
        animation: hwaIn .35s cubic-bezier(.4,0,.2,1) !important;
        transition: right .35s cubic-bezier(.4,0,.2,1), opacity .4s, transform .4s !important;
      }}
      @keyframes hwaIn {{
        from {{ transform: translateY(-12px); opacity: 0; }}
        to   {{ transform: translateY(0);     opacity: 1; }}
      }}
      #hwa-head {{
        display: flex !important; align-items: center !important; gap: 8px !important;
        padding: 11px 14px !important;
        border-bottom: 1px solid rgba(0,194,212,0.12) !important;
        color: #e8f4f8 !important; font-size: 13px !important; font-weight: 700 !important;
      }}
      #hwa-head .hwa-n {{
        background: rgba(0,194,212,0.15) !important; color: #00e5ff !important;
        border-radius: 999px !important; padding: 1px 9px !important;
        font-size: 11px !important; font-weight: 800 !important;
      }}
      #hwa-x {{
        margin-left: auto !important; background: none !important; border: none !important;
        color: #7aacbf !important; font-size: 15px !important; cursor: pointer !important;
        padding: 0 2px !important; line-height: 1 !important;
      }}
      #hwa-x:hover {{ color: #00e5ff !important; }}
      .hwa-row {{
        display: flex !important; align-items: baseline !important; gap: 8px !important;
        padding: 8px 14px !important; font-size: 12.5px !important;
      }}
      .hwa-row + .hwa-row {{ border-top: 1px solid rgba(255,255,255,0.04) !important; }}
      .hwa-row .r {{ font-weight: 700 !important; min-width: 34px !important; }}
      .hwa-row.alarm    .r {{ color: #ff8a8a !important; }}
      .hwa-row.advisory .r {{ color: #ffd75e !important; }}
      .hwa-row .lv {{ font-size: 11px !important; font-weight: 800 !important;
                      border-radius: 6px !important; padding: 1px 7px !important; }}
      .hwa-row.alarm    .lv {{ background: rgba(255,80,80,0.15) !important; color: #ff8a8a !important; }}
      .hwa-row.advisory .lv {{ background: rgba(255,215,0,0.12) !important; color: #ffd75e !important; }}
      .hwa-row .d {{ color: #7aacbf !important; font-size: 11.5px !important; }}
      #hwa-bar {{
        height: 3px !important; background: linear-gradient(90deg,#00c2d4,#00e5a0) !important;
        animation: hwaBar 12s linear forwards !important;
      }}
      @keyframes hwaBar {{ from {{ width: 100%; }} to {{ width: 0%; }} }}
    `;
    doc.head.appendChild(style);
  }}

  var card = doc.createElement('div');
  card.id = 'hwa-card';
  card.dataset.sig = sig;
  card.style.right = RIGHT + 'px';

  var rows = alerts.map(function(a) {{
    var cls   = a.level === 'alarm' ? 'alarm' : 'advisory';
    var label = a.level === 'alarm' ? '경보' : '주의보';
    var sstTxt = (a.latest_sst != null) ? a.latest_sst.toFixed(1) + '°C' : '-';
    var days = a.demo ? ('최장 ' + a.max_consec + '일(과거)') : ('연속 ' + a.current_streak + '일');
    return '<div class="hwa-row ' + cls + '">' +
           '<span class="r">' + a.region + '</span>' +
           '<span class="lv">' + label + '</span>' +
           '<span class="d">' + days + ' · ' + sstTxt + '</span>' +
           '</div>';
  }}).join('');

  card.innerHTML =
    '<div id="hwa-head">🌡️ 고수온 특보 <span class="hwa-n">' + alerts.length + '</span>' +
    '<button id="hwa-x" title="닫기 (같은 내용은 다시 표시 안 함)">✕</button></div>' +
    rows + '<div id="hwa-bar"></div>';
  doc.body.appendChild(card);

  function dismiss(persist) {{
    if (persist) {{
      try {{ window.parent.localStorage.setItem('hwaDismissed', sig); }} catch (e) {{}}
    }}
    card.style.opacity = '0';
    card.style.transform = 'translateY(-12px)';
    setTimeout(function() {{ if (card.parentNode) card.remove(); }}, 400);
  }}

  card.querySelector('#hwa-x').onclick = function() {{ dismiss(true); }};
  setTimeout(function() {{ if (card.parentNode) dismiss(false); }}, 12000);
}})();
</script>
</body></html>
""", height=1, scrolling=False)
