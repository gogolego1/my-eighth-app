import streamlit as st
from google import genai
from google.genai import types
import json
import re

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="H.E.A.L 프로젝트 - AI 토론 도우미",
    page_icon="🌊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.stApp { background: linear-gradient(180deg,#e0f7fa 0%,#f0f9ff 60%,#f8fafc 100%); }

.heal-header {
    background: linear-gradient(135deg,#0284c7,#0ea5e9,#06b6d4);
    border-radius: 0 0 28px 28px;
    padding: 28px 24px 36px;
    text-align: center;
    margin: -1rem -1rem 1.5rem -1rem;
    box-shadow: 0 4px 20px rgba(14,165,233,0.2);
}
.heal-header h1 { color:white; font-size:2rem; font-weight:900; margin:0.3rem 0 0.2rem; letter-spacing:-0.5px; }
.heal-header p  { color:#bae6fd; font-size:0.85rem; margin:0; }
.heal-icons     { font-size:2.2rem; margin-bottom:4px; }

.step-bar  { display:flex; gap:8px; margin:0 0 1.2rem 0; }
.step-item { flex:1; text-align:center; font-size:11px; font-weight:700; padding:6px 4px 4px; border-radius:10px; border:2px solid transparent; }
.step-active { background:#0ea5e9; color:white; border-color:#0284c7; }
.step-done   { background:#bbf7d0; color:#166534; border-color:#86efac; }
.step-todo   { background:#f1f5f9; color:#94a3b8; border-color:#e2e8f0; }

.card { background:white; border-radius:18px; padding:20px; margin-bottom:14px; box-shadow:0 2px 16px rgba(14,165,233,0.07); }

.arg-claim    { background:#eff6ff; border-left:5px solid #3b82f6; border-radius:12px; padding:14px 18px; margin-bottom:10px; }
.arg-reason   { background:#f0fdf4; border-left:5px solid #22c55e; border-radius:12px; padding:14px 18px; margin-bottom:10px; }
.arg-evidence { background:#fff7ed; border-left:5px solid #f97316; border-radius:12px; padding:14px 18px; margin-bottom:10px; }
.arg-label    { font-size:11px; font-weight:800; margin-bottom:6px; letter-spacing:0.5px; }
.arg-text     { font-size:15px; line-height:1.7; }

.fb-box      { border-radius:12px; padding:12px 16px; margin-top:8px; font-size:13px; line-height:1.7; }
.fb-claim    { background:#dbeafe; color:#1e40af; border:1px solid #bfdbfe; }
.fb-reason   { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }
.fb-evidence { background:#ffedd5; color:#9a3412; border:1px solid #fed7aa; }
.fb-title    { font-weight:800; font-size:12px; margin-bottom:4px; }

.chip-wrap { display:flex; flex-wrap:wrap; gap:6px; margin:8px 0; }
.chip      { display:inline-block; background:#e0f2fe; color:#0369a1; border-radius:99px; padding:4px 14px; font-size:13px; font-weight:700; }
.chip:nth-child(2n) { background:#dcfce7; color:#166534; }
.chip:nth-child(3n) { background:#fef9c3; color:#854d0e; }
.chip:nth-child(4n) { background:#ede9fe; color:#5b21b6; }

.news-card   { background:white; border:1.5px solid #e2e8f0; border-radius:16px; padding:16px; margin-bottom:10px; }
.news-source { font-size:12px; color:#0ea5e9; font-weight:700; margin-bottom:4px; }
.news-title  { font-size:15px; font-weight:800; color:#0f172a; margin-bottom:6px; line-height:1.4; }
.news-summary{ font-size:13px; color:#475569; line-height:1.6; margin-bottom:10px; }
.evidence-box   { background:#fff7ed; border-left:4px solid #f97316; border-radius:8px; padding:10px 14px; margin-top:8px; }
.evidence-label { font-size:11px; color:#ea580c; font-weight:800; margin-bottom:4px; }
.evidence-text  { font-size:14px; color:#7c2d12; font-weight:600; line-height:1.5; font-style:italic; }
.evidence-why   { font-size:12px; color:#9a3412; margin-top:5px; }
.source-link    { font-size:12px; color:#0284c7; text-decoration:none; font-weight:600; }

.search-card     { background:#f8fafc; border:1.5px solid #cbd5e1; border-radius:14px; padding:14px 16px; margin-bottom:8px; }
.search-card-pro { border-color:#86efac; background:#f0fdf4; }
.search-card-con { border-color:#fca5a5; background:#fff5f5; }
.search-badge-pro { display:inline-block; background:#dcfce7; color:#166534; border-radius:99px; padding:2px 10px; font-size:11px; font-weight:800; margin-bottom:6px; }
.search-badge-con { display:inline-block; background:#fee2e2; color:#991b1b; border-radius:99px; padding:2px 10px; font-size:11px; font-weight:800; margin-bottom:6px; }
.search-badge-neu { display:inline-block; background:#f1f5f9; color:#475569;  border-radius:99px; padding:2px 10px; font-size:11px; font-weight:800; margin-bottom:6px; }

.praise-box   { background:#fef9c3; border:2px solid #fde047; border-radius:14px; padding:12px 16px; text-align:center; font-size:16px; font-weight:800; color:#854d0e; margin-bottom:14px; }
.citation-box { background:#f0fdf4; border:1.5px solid #86efac; border-radius:14px; padding:14px 16px; margin-top:10px; font-size:12px; color:#14532d; line-height:1.9; white-space:pre-wrap; font-family:monospace; }
.info-box     { background:#e0f2fe; border-radius:14px; padding:12px 16px; font-size:13px; color:#0369a1; line-height:1.7; margin-top:16px; }

.stButton > button { border-radius:14px !important; font-weight:800 !important; font-size:15px !important; padding:12px 0 !important; width:100% !important; border:none !important; transition:opacity 0.2s !important; }
.stButton > button:hover { opacity:0.88 !important; }
.stTextArea textarea { border-radius:12px !important; font-size:15px !important; font-family:'Noto Sans KR',sans-serif !important; }
</style>
""", unsafe_allow_html=True)


# ── Gemini 클라이언트 (신규 SDK: google-genai) ────────────────
def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def call_gemini_json(system_prompt: str, user_message: str) -> str:
    """일반 JSON 응답 — 검색 없이"""
    client = get_client()
    if client is None:
        return "__NO_KEY__"
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\n{user_message}",
            config=types.GenerateContentConfig(
                max_output_tokens=1200,
                temperature=0.6,
            ),
        )
        return response.text
    except Exception as e:
        return f"__ERROR__:{e}"


def call_gemini_with_search(prompt: str) -> tuple:
    """Google Search 그라운딩 활성화 — 최신 SDK 방식"""
    client = get_client()
    if client is None:
        return "__NO_KEY__", []
    try:
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[grounding_tool],
                max_output_tokens=2000,
                temperature=0.5,
            ),
        )
        # 출처 수집
        sources = []
        try:
            meta = response.candidates[0].grounding_metadata
            if meta and meta.grounding_chunks:
                for chunk in meta.grounding_chunks:
                    if hasattr(chunk, "web") and chunk.web:
                        sources.append({
                            "title": chunk.web.title or "출처 보기",
                            "url":   chunk.web.uri   or "#",
                        })
        except Exception:
            pass
        return response.text, sources
    except Exception as e:
        return f"__ERROR__:{e}", []


# ── 샘플 기사 ─────────────────────────────────────────────────
ARTICLES = [
    {
        "id": 1,
        "title": "완도 금일도 주민, 해상풍력 반대… '해상풍력 철회하라'",
        "summary": "한국남동발전이 완도 금일도 해상 7km 지점에 15MW 발전기 40기(600MW) 설치를 추진하자, 어선 100여 척이 앞바다에 멈춰 서며 반대 시위를 벌였습니다. 주민들은 해조류 양식장 피해와 생태계 파괴, 보상 기준 부재를 우려하고 있습니다.",
        "source": "LG헬로비전", "date": "2024.09.03",
        "url": "https://news.lghellovision.net/news/articleView.html?idxno=480155",
        "evidence": "금일도 어민들은 어선 100여 척을 동원해 해상 시위를 벌이며 '보상 기준도, 책임지는 사람도 없다'고 주장했습니다.",
        "evidence_type": "주민 증언", "side": "반대",
        "keywords": ["어민 반대", "생존권", "보상 부재", "생태계 피해"],
    },
    {
        "id": 2,
        "title": "해상풍력, 어업인 생존권 충돌… '해풍법' 주민 수용성 가능할까",
        "summary": "신안 해상풍력 8.2GW 조성구역은 연안 어선의 조업공간 91.3%와 겹칩니다. 그 면적은 서울시의 3배에 달합니다. 해상풍력 특별법(해풍법)은 인허가 기간을 8개월 단축하지만 어업인 보상 규정은 없어 국회 토론회에서 강하게 비판받았습니다.",
        "source": "오마이뉴스", "date": "2025.05.16",
        "url": "https://www.ohmynews.com/NWS_Web/View/at_pg.aspx?CNTN_CD=A0003131395",
        "evidence": "신안 해상풍력 조성구역은 연안 어선 조업공간의 91.3%와 중복되며, 그 면적은 서울시의 3배에 달합니다.",
        "evidence_type": "통계", "side": "반대",
        "keywords": ["조업 공간", "91.3% 중복", "보상 규정 없음", "해풍법"],
    },
    {
        "id": 3,
        "title": "해상 경계 분쟁, '어장'에서 '해상 풍력'으로 확대",
        "summary": "완도-제주 해상경계 분쟁은 1996년부터 지금까지 해결되지 않고 있습니다. 해역 경계가 불명확하면 인허가 지연과 법적 불확실성이 생겨 지역 경제에 큰 손실이 발생합니다.",
        "source": "KBC", "date": "2025.03.16",
        "url": "https://news.ikbc.co.kr/%EC%A0%80%EB%85%81%EB%89%B4%EC%8A%A4(%EC%82%AC%ED%9A%8C)/article/view/kbc202503160032",
        "evidence": "해상경계가 불명확하면 해상풍력 인허가가 지연되고 법적 분쟁이 발생해 지역 경제 기회가 손실됩니다.",
        "evidence_type": "전문가 분석", "side": "조건부",
        "keywords": ["해상경계 분쟁", "인허가 지연", "지역 경제", "해양 자원"],
    },
    {
        "id": 4,
        "title": "하나은행·한국남동발전, 완도금일해상풍력 업무협약 체결",
        "summary": "하나은행이 한국남동발전과 600MW 규모 완도금일해상풍력 발전단지 조성을 위한 MOU를 맺었습니다. 생산 전력은 국가 AI 데이터센터와 호남권 첨단전략산업 전력 인프라로 활용될 예정입니다.",
        "source": "조선비즈", "date": "2026.02.27",
        "url": "https://biz.chosun.com/stock/finance/2026/02/27/Q35WW4LYFNE6HAGNSMB4X6S2L4/",
        "evidence": "하나은행과 남동발전이 600MW 완도금일해상풍력 MOU를 체결했고, 연내 착공이 가능한 단계로 평가받고 있습니다.",
        "evidence_type": "공식 발표", "side": "찬성",
        "keywords": ["MOU 체결", "600MW", "AI 데이터센터", "착공 임박"],
    },
]

PRAISE_LIST = [
    "👏 정말 훌륭한 주장이에요!",
    "⭐ 생각을 아주 잘 정리했어요!",
    "🎉 논리적인 주장이에요!",
    "💪 멋진 이유를 썼어요!",
    "🌟 토론 준비가 훌륭해요!",
]
TOPIC = "기후 위기를 막기 위해 해상풍력 발전단지 건설은 반드시 필요하다"


# ── 세션 초기화 ───────────────────────────────────────────────
def init_session():
    defaults = {
        "step": 0, "claim": "", "reason": "",
        "keywords": [], "ai_analysis": None,
        "selected_articles": [], "praise": "",
        "search_results": [],
        "filtered_articles": ARTICLES,
        "rebuttal": "", "ai_rebuttal": None,
        "final_speech": "", "selected_evidence": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── 공통 UI ───────────────────────────────────────────────────
def render_header():
    st.markdown(f"""
    <div class="heal-header">
        <div class="heal-icons">🌿🌊🐠</div>
        <h1>H.E.A.L 프로젝트</h1>
        <p>해상풍력 발전단지 건설 · AI 토론 도우미</p>
    </div>
    """, unsafe_allow_html=True)

def render_progress(step: int):
    labels = ["1단계: 주장 펼치기", "2단계: 반론 펼치기", "3단계: 주장 다지기"]
    html = '<div class="step-bar">'
    for i, s in enumerate(labels):
        if i < step:    cls, pre = "step-done",   "✅ "
        elif i == step: cls, pre = "step-active", "▶ "
        else:           cls, pre = "step-todo",   ""
        html += f'<div class="step-item {cls}">{pre}{s}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def render_no_key_warning():
    st.warning("⚠️ **Gemini API 키가 없어요.**\n\nStreamlit → Settings → Secrets에 `GEMINI_API_KEY = \"AIza...\"` 를 추가해 주세요.")

def render_arg_card(label, css_class, icon, text, feedback=None, feedback_css=None):
    display = text if text else f'<span style="color:#94a3b8">아직 입력하지 않았어요</span>'
    fb_html = ""
    if feedback:
        fb_html = f'<div class="fb-box {feedback_css}"><div class="fb-title">💬 AI 선생님 의견</div>{feedback}</div>'
    st.markdown(f"""
    <div class="{css_class}">
        <div class="arg-label">{icon} {label}</div>
        <div class="arg-text">{display}</div>
        {fb_html}
    </div>
    """, unsafe_allow_html=True)


# ── 기사 카드 ─────────────────────────────────────────────────
def _render_news_card(article: dict):
    sid = article["id"]
    is_sel = sid in st.session_state.selected_articles
    border = "border:2px solid #0ea5e9;" if is_sel else "border:1.5px solid #e2e8f0;"
    badge  = {"찬성":"🟢 찬성 측","반대":"🔴 반대 측","조건부":"🟡 조건부"}.get(article["side"],"")
    st.markdown(f"""
    <div class="news-card" style="{border}">
        <div class="news-source">📰 {article['source']} · {article['date']} &nbsp;
            <span style="background:#f1f5f9;padding:2px 8px;border-radius:99px;font-size:11px;">{badge}</span>
        </div>
        <div class="news-title">{article['title']}</div>
        <div class="news-summary">{article['summary']}</div>
        <div class="evidence-box">
            <div class="evidence-label">✅ 근거로 쓸 수 있는 문장</div>
            <div class="evidence-text">"{article['evidence']}"</div>
            <div class="evidence-why">💡 <b>{article['source']}</b>의 <b>{article['evidence_type']}</b>이라 믿을 수 있어요!</div>
        </div>
        <div style="margin-top:8px;">
            <a href="{article['url']}" target="_blank" class="source-link">🔗 원문 기사 보러가기 ↗</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✅ 선택됨!" if is_sel else "📌 근거로 사용하기", key=f"sel_art_{sid}"):
        if is_sel: st.session_state.selected_articles.remove(sid)
        else:      st.session_state.selected_articles.append(sid)
        st.rerun()


# ── 웹 검색 결과 카드 ─────────────────────────────────────────
def _render_search_card(item: dict, idx: int):
    wid   = f"web_{idx}"
    is_sel = wid in st.session_state.selected_articles
    side  = item.get("side", "neutral")
    if side == "pro":
        card_cls, badge = "search-card search-card-pro", '<span class="search-badge-pro">🟢 찬성 측 근거</span>'
    elif side == "con":
        card_cls, badge = "search-card search-card-con", '<span class="search-badge-con">🔴 반대 측 근거</span>'
    else:
        card_cls, badge = "search-card", '<span class="search-badge-neu">🔵 참고 자료</span>'
    url      = item.get("url", "#")
    link_html = f'<a href="{url}" target="_blank" class="source-link">🔗 원문 보러가기 ↗</a>' if url and url != "#" else ""
    border   = "border:2px solid #0ea5e9;" if is_sel else ""
    st.markdown(f"""
    <div class="{card_cls}" style="{border}">
        {badge}
        <div class="news-title" style="font-size:14px;">{item.get('title','제목 없음')}</div>
        <div class="news-summary">{item.get('summary','')}</div>
        <div class="evidence-box">
            <div class="evidence-label">✅ 근거 문장</div>
            <div class="evidence-text">"{item.get('evidence','')}"</div>
            <div class="evidence-why">💡 {item.get('why','이 자료는 믿을 수 있는 출처에서 나왔어요.')}</div>
        </div>
        <div style="margin-top:8px;display:flex;align-items:center;gap:12px;">
            {link_html}
            <span style="font-size:11px;color:#94a3b8;">{item.get('source_label','')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✅ 선택됨!" if is_sel else "📌 근거로 사용하기", key=f"sel_web_{idx}"):
        if is_sel: st.session_state.selected_articles.remove(wid)
        else:      st.session_state.selected_articles.append(wid)
        st.rerun()


# ════════════════════════════════════════════════════════════
# 1단계: 주장 펼치기
# ════════════════════════════════════════════════════════════
def step1():
    st.markdown(f"""
    <div class="card" style="background:linear-gradient(135deg,#e0f7f4,#b2ebf2);padding:18px 20px 14px;">
        <div style="font-size:1.3rem;font-weight:900;color:#0369a1;">🌊 1단계: 주장 펼치기</div>
        <div style="font-size:0.85rem;color:#0ea5e9;margin-top:4px;">나의 주장과 이유를 쓰고, AI로 근거를 찾아봐요!</div>
        <div style="margin-top:10px;background:white;border-radius:10px;padding:10px 14px;font-size:0.9rem;color:#0369a1;font-weight:700;">
            📌 토론 주제: {TOPIC}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**💬 나의 주장** (찬성 또는 반대 입장을 써보세요)")
    claim = st.text_area("주장", value=st.session_state.claim,
        placeholder='예) "해상풍력 발전단지 건설은 기후 위기 해결을 위해 반드시 필요하다."',
        height=80, label_visibility="collapsed", key="input_claim")

    st.markdown("**🌿 그렇게 생각하는 이유**")
    reason = st.text_area("이유", value=st.session_state.reason,
        placeholder='예) "석탄·가스 발전을 줄이고 재생에너지를 늘려야 탄소 배출을 줄일 수 있기 때문이다."',
        height=100, label_visibility="collapsed", key="input_reason")

    can_analyze = bool(claim.strip() and reason.strip())
    if st.button("🔍 AI 피드백 + 근거 찾기!", disabled=not can_analyze, key="btn_analyze"):
        st.session_state.claim  = claim
        st.session_state.reason = reason
        _run_analysis(claim, reason)
        _run_web_search(claim, reason)
        import random
        st.session_state.praise = random.choice(PRAISE_LIST)

    if st.session_state.ai_analysis:
        _render_analysis_result()


# ═══════════════════════════════════════════════════════════
# 피드백 기준표 (프롬프트에 직접 내장)
# ═══════════════════════════════════════════════════════════
CLAIM_RUBRIC = """
[주장 평가 기준표]
★ 상 (아주 잘했어요!): 아래 조건 3가지 모두 충족
  - 찬성/반대 입장이 명확하게 드러남
  - 무엇에 대한 주장인지 주어가 있음
  - 단순 사실 진술이 아닌 논쟁 가능한 주장임

★ 중 (잘했어요!): 조건 2가지 충족, 또는
  - 입장은 있으나 너무 모호함 ("좋다/나쁘다" 수준)
  - 주어는 있으나 이유가 없어 설득력 약함

★ 하 (조금 더 다듬어봐요!): 조건 1가지 이하, 또는
  - 주어가 빠진 주장 ("반드시 필요하다" 만 쓴 경우)
  - 사실 진술 ("해상풍력은 바람으로 전기를 만든다")
  - 주장이 너무 극단적이거나 근거 없는 단정

[피드백 작성 규칙]
- 항상 칭찬 먼저 → 개선점 순서로 작성
- 개선점은 "이렇게 바꿔봐요" 형태로 구체적 예시 제시
- 초등학교 6학년이 이해할 수 있는 쉬운 말 사용
- 2~3문장으로 작성
"""

REASON_RUBRIC = """
[이유 평가 기준표]
★ 상 (아주 잘했어요!): 아래 조건 3가지 모두 충족
  - 주장과 직접 연결됨 (주장을 읽고 "왜?"라고 물으면 이유가 답이 됨)
  - 인과관계가 명확함 ("~하면 ~하기 때문에" 구조)
  - 구체적인 현상이나 원리를 언급함

★ 중 (잘했어요!): 조건 2가지 충족, 또는
  - 주장과 연결되지만 설명이 너무 짧거나 막연함
  - 구체성은 있으나 주장과의 연결이 약함

★ 하 (조금 더 다듬어봐요!): 조건 1가지 이하, 또는
  - 주장을 그대로 반복 ("왜냐하면 좋기 때문이다")
  - 또 다른 주장처럼 들림 ("재생에너지는 최고의 대안이다")
  - 너무 막연함 ("환경에 좋기 때문이다")

[피드백 작성 규칙]
- 항상 칭찬 먼저 → 개선점 순서로 작성
- "왜 그렇게 생각해요?" 한 단계 더 파고드는 질문 포함
- 구체적인 개선 예시 제시 ("~처럼 쓰면 더 좋아요")
- 초등학교 6학년이 이해할 수 있는 쉬운 말
- 2~3문장으로 작성
"""

EVIDENCE_RUBRIC = """
[좋은 근거의 조건]
1. 통계/숫자: "~% / ~배 / ~명" 처럼 측정된 수치
2. 전문가 의견: 연구자, 정부기관, 전문 단체의 공식 발언
3. 실제 사례: 특정 지역/국가에서 실제로 일어난 일
4. 연구 결과: 논문이나 보고서에서 나온 검증된 사실

[근거가 아닌 것]
- 내 생각이나 느낌 ("나는 ~라고 생각한다")
- 근거 없는 일반화 ("모든 사람들이 ~라고 한다")
- 출처 불명 정보
"""


def _run_analysis(claim: str, reason: str):
    system = f"""당신은 초등학교 6학년 학생을 돕는 친절한 국어·사회 선생님입니다.
아래 평가 기준표를 반드시 참고하여 학생의 주장과 이유를 분석해주세요.

{CLAIM_RUBRIC}

{REASON_RUBRIC}

{EVIDENCE_RUBRIC}

분석 결과를 반드시 아래 JSON 형식으로만 출력하세요. 코드블록(```) 없이 JSON만 출력하세요.
{{
  "keywords": ["키워드1","키워드2","키워드3","키워드4"],

  "claimScore": "상 또는 중 또는 하",
  "claimScoreReason": "이 점수를 준 이유 1문장 (기준표 근거 명시)",
  "claimPraise": "잘한 점 구체적으로 칭찬 1~2문장",
  "claimImprove": "개선점과 구체적 예시 1~2문장 (없으면 빈 문자열)",

  "reasonScore": "상 또는 중 또는 하",
  "reasonScoreReason": "이 점수를 준 이유 1문장 (기준표 근거 명시)",
  "reasonPraise": "잘한 점 구체적으로 칭찬 1~2문장",
  "reasonImprove": "개선점과 구체적 예시 1~2문장 (없으면 빈 문자열)",
  "reasonDeeperQ": "이유를 한 단계 더 깊게 생각하게 하는 질문 1문장",

  "evidenceNeed": {{
    "stat":   "이 주장에 필요한 통계/숫자 근거가 무엇인지 1문장",
    "expert": "이 주장에 필요한 전문가/기관 의견이 무엇인지 1문장",
    "case":   "이 주장에 필요한 실제 사례가 무엇인지 1문장"
  }},

  "searchQueries": {{
    "stat":   "통계·수치 자료를 찾기 위한 한국어 검색어",
    "expert": "전문가·기관 의견을 찾기 위한 한국어 검색어",
    "case":   "실제 사례를 찾기 위한 한국어 검색어"
  }}
}}"""

    with st.spinner("✏️ AI 선생님이 주장과 이유를 꼼꼼히 읽고 있어요..."):
        result = call_gemini_json(system, f"학생의 주장: {claim}\n학생의 이유: {reason}")

    if result.startswith("__NO_KEY__"): render_no_key_warning(); return
    if result.startswith("__ERROR__"):  st.error(f"AI 오류: {result}"); return

    try:
        parsed = json.loads(re.sub(r"```json|```", "", result).strip())
    except Exception:
        parsed = {
            "keywords": ["해상풍력","기후 위기","어민 피해","에너지 전환"],
            "claimScore": "중", "claimScoreReason": "입장은 있으나 조금 더 구체화가 필요해요.",
            "claimPraise": "찬성 또는 반대 입장이 드러나 있어요!", "claimImprove": "",
            "reasonScore": "중", "reasonScoreReason": "주장과 연결되지만 인과관계 설명이 짧아요.",
            "reasonPraise": "이유를 쓰려고 노력했어요!", "reasonImprove": "왜 그런지 한 단계 더 설명해봐요.",
            "reasonDeeperQ": "그렇다면 구체적으로 어떤 변화가 생길까요?",
            "evidenceNeed": {
                "stat":   "해상풍력 발전이 탄소 배출을 얼마나 줄이는지 수치 자료",
                "expert": "에너지 전문가나 환경부의 해상풍력 관련 공식 의견",
                "case":   "해상풍력으로 성공한 나라나 지역의 실제 사례"
            },
            "searchQueries": {
                "stat":   "해상풍력 탄소감축 효과 통계",
                "expert": "해상풍력 환경부 에너지전환 전문가 의견",
                "case":   "해상풍력 성공 사례 유럽 덴마크"
            }
        }

    st.session_state.ai_analysis = parsed
    st.session_state.keywords    = parsed.get("keywords", [])
    kws = parsed.get("keywords", [])
    filtered = [a for a in ARTICLES if any(k in " ".join(a["keywords"]) for k in kws)]
    st.session_state.filtered_articles = filtered if filtered else ARTICLES


def _run_web_search(claim: str, reason: str):
    """통계 / 전문가 / 사례 3트랙으로 분리 검색"""
    ana = st.session_state.ai_analysis or {}
    sq  = ana.get("searchQueries", {})
    en  = ana.get("evidenceNeed", {})

    q_stat   = sq.get("stat",   f"{reason} 통계 수치")
    q_expert = sq.get("expert", f"{reason} 전문가 의견")
    q_case   = sq.get("case",   f"{reason} 사례")

    need_stat   = en.get("stat",   "관련 통계")
    need_expert = en.get("expert", "전문가 의견")
    need_case   = en.get("case",   "실제 사례")

    prompt = f"""초등학교 6학년 학생이 아래 토론 주제로 주장하는 글을 쓰고 있어요.

토론 주제: {TOPIC}
학생 주장: {claim}
학생 이유: {reason}

학생의 이유를 뒷받침하거나 반박할 수 있는 자료를 Google에서 검색해주세요.
아래 3가지 유형을 각각 1~2개씩, 총 5~6개 찾아주세요.

[찾아야 할 자료 유형]
① 통계/수치 자료 (검색어: "{q_stat}")
   → 필요한 내용: {need_stat}

② 전문가/기관 의견 (검색어: "{q_expert}")
   → 필요한 내용: {need_expert}

③ 실제 사례 (검색어: "{q_case}")
   → 필요한 내용: {need_case}

[중요 조건]
- 각 자료에 evidence_type을 "통계" / "전문가 의견" / "실제 사례" 중 하나로 표시
- 학생 주장을 지지하면 side="pro", 반대하면 side="con", 중립이면 side="neutral"
- 출처가 불분명하거나 광고성 자료는 제외
- evidence 문장은 반드시 구체적 수치·사실·발언이 포함된 1문장
- why 는 "이 문장이 왜 근거가 되는지" 를 초등학생 언어로 설명 (예: "전문 기관이 직접 조사한 숫자이기 때문에 믿을 수 있어요")

코드블록(```) 없이 JSON 배열만 출력하세요:
[
  {{
    "title": "자료 제목",
    "summary": "초등학생도 이해할 수 있는 2~3문장 요약",
    "evidence": "근거 문장 1개 (반드시 수치·사실·발언 포함)",
    "why": "왜 이것이 근거가 되는지 1문장 (초등학생 언어)",
    "evidence_type": "통계 또는 전문가 의견 또는 실제 사례",
    "source_label": "출처 기관·매체명 + 연도",
    "side": "pro 또는 con 또는 neutral",
    "url": "실제 URL 또는 빈 문자열"
  }}
]"""

    with st.spinner("🌐 통계 · 전문가 의견 · 사례를 각각 검색하고 있어요..."):
        result, sources = call_gemini_with_search(prompt)

    if result.startswith("__NO_KEY__"): render_no_key_warning(); return
    if result.startswith("__ERROR__"):
        st.warning(f"검색 오류: {result}")
        st.session_state.search_results = []; return

    try:
        clean = re.sub(r"```json|```", "", result).strip()
        match = re.search(r'\[.*\]', clean, re.DOTALL)
        items = json.loads(match.group() if match else clean)
        for i, item in enumerate(items):
            if not item.get("url") and i < len(sources):
                item["url"] = sources[i].get("url", "#")
        st.session_state.search_results = items
    except Exception:
        st.session_state.search_results = []


def _render_analysis_result():
    ana = st.session_state.ai_analysis

    # ── 칭찬 배너 ──
    if st.session_state.praise:
        st.markdown(f'<div class="praise-box">{st.session_state.praise}</div>', unsafe_allow_html=True)

    st.markdown("#### 📋 주장 · 이유 · 근거 구분 & AI 피드백")

    # ── 점수 뱃지 ──
    score_badge = {
        "상": '<span style="background:#dcfce7;color:#166534;border-radius:99px;padding:3px 12px;font-size:12px;font-weight:800;">🌟 아주 잘했어요!</span>',
        "중": '<span style="background:#fef9c3;color:#854d0e;border-radius:99px;padding:3px 12px;font-size:12px;font-weight:800;">👍 잘했어요!</span>',
        "하": '<span style="background:#fee2e2;color:#991b1b;border-radius:99px;padding:3px 12px;font-size:12px;font-weight:800;">💪 조금 더 다듬어봐요!</span>',
    }

    # ── 주장 카드 ──
    cs  = ana.get("claimScore", "중")
    cb  = score_badge.get(cs, "")
    cpr = ana.get("claimPraise", "")
    cim = ana.get("claimImprove", "")
    csr = ana.get("claimScoreReason", "")
    claim_fb = f"""{cb}
<div style="margin-top:8px;font-size:13px;line-height:1.7;">
  <b>📍 평가 이유:</b> {csr}<br>
  <b>✅ 잘한 점:</b> {cpr}
  {"<br><b>💡 개선 제안:</b> " + cim if cim else ""}
</div>"""
    render_arg_card("💬 주장", "arg-claim", "💬", st.session_state.claim, claim_fb, "fb-claim")

    # ── 이유 카드 ──
    rs  = ana.get("reasonScore", "중")
    rb  = score_badge.get(rs, "")
    rpr = ana.get("reasonPraise", "")
    rim = ana.get("reasonImprove", "")
    rsr = ana.get("reasonScoreReason", "")
    rdq = ana.get("reasonDeeperQ", "")
    reason_fb = f"""{rb}
<div style="margin-top:8px;font-size:13px;line-height:1.7;">
  <b>📍 평가 이유:</b> {rsr}<br>
  <b>✅ 잘한 점:</b> {rpr}
  {"<br><b>💡 개선 제안:</b> " + rim if rim else ""}
  {"<br><b>🤔 더 생각해봐요:</b> " + rdq if rdq else ""}
</div>"""
    render_arg_card("🌿 이유", "arg-reason", "🌿", st.session_state.reason, reason_fb, "fb-reason")

    # ── 근거 힌트 카드 (3트랙) ──
    en = ana.get("evidenceNeed", {})
    st.markdown(f"""
    <div class="arg-evidence">
        <div class="arg-label">📌 근거 (아직 찾는 중!)</div>
        <div class="arg-text" style="color:#c2410c;">근거는 내 생각이 아닌 <b>객관적인 자료</b>예요! 아래 3가지를 찾아봐요.</div>
        <div style="display:flex;flex-direction:column;gap:6px;margin-top:10px;">
          <div style="background:#dbeafe;border-radius:10px;padding:9px 13px;font-size:13px;color:#1e40af;">
            <b>📊 통계/숫자</b>: {en.get("stat","숫자나 통계 자료를 찾아보세요.")}
          </div>
          <div style="background:#dcfce7;border-radius:10px;padding:9px 13px;font-size:13px;color:#166534;">
            <b>🧑‍🔬 전문가/기관 의견</b>: {en.get("expert","전문가나 공식 기관의 의견을 찾아보세요.")}
          </div>
          <div style="background:#ede9fe;border-radius:10px;padding:9px 13px;font-size:13px;color:#5b21b6;">
            <b>🌍 실제 사례</b>: {en.get("case","실제로 일어난 사례를 찾아보세요.")}
          </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 키워드 ──
    st.markdown("#### 🏷️ AI가 찾은 핵심 키워드")
    chips = "".join([f'<span class="chip">{k}</span>' for k in st.session_state.keywords])
    st.markdown(f'<div class="chip-wrap">{chips}</div>', unsafe_allow_html=True)

    # ── 탭: 기사 / 검색 ──
    tab1, tab2 = st.tabs(["📰 제공 기사 자료", "🌐 인터넷 검색 자료"])
    with tab1:
        for a in st.session_state.get("filtered_articles", ARTICLES):
            _render_news_card(a)
    with tab2:
        results = st.session_state.get("search_results", [])
        if not results:
            st.info("🔍 검색 결과가 없어요. '근거 찾기' 버튼을 눌러 다시 시도해봐요!")
        else:
            # 유형별 분류 표시
            type_order = ["통계", "전문가 의견", "실제 사례"]
            type_icon  = {"통계":"📊", "전문가 의견":"🧑‍🔬", "실제 사례":"🌍"}
            grouped = {}
            for item in results:
                t = item.get("evidence_type", "기타")
                grouped.setdefault(t, []).append(item)

            for t in type_order:
                if t not in grouped: continue
                st.markdown(f"""
                <div style="background:#f1f5f9;border-radius:10px;padding:7px 14px;margin:10px 0 6px;font-size:13px;font-weight:800;color:#334155;">
                    {type_icon.get(t,"📄")} {t} 자료
                </div>
                """, unsafe_allow_html=True)
                for i, item in enumerate(grouped[t]):
                    real_idx = results.index(item)
                    _render_search_card(item, real_idx)
            for t, items in grouped.items():
                if t in type_order: continue
                for item in items:
                    _render_search_card(item, results.index(item))

    _render_selected_summary()


def _render_selected_summary():
    sel_int = [s for s in st.session_state.selected_articles if isinstance(s, int)]
    sel_str = [s for s in st.session_state.selected_articles if isinstance(s, str)]
    if not sel_int and not sel_str: return

    st.markdown("#### 📌 내가 선택한 근거 모음")
    citation_lines = []

    for sid in sel_int:
        art = next((x for x in ARTICLES if x["id"] == sid), None)
        if art:
            st.markdown(f"""
            <div style="background:#fff7ed;border-left:4px solid #f97316;border-radius:10px;padding:10px 14px;margin-bottom:6px;">
                <div style="font-size:12px;color:#ea580c;font-weight:700;">{art['source']} ({art['date']})</div>
                <div style="font-size:14px;color:#7c2d12;font-weight:600;">"{art['evidence']}"</div>
                <a href="{art['url']}" target="_blank" style="font-size:12px;color:#0284c7;">🔗 출처 보기</a>
            </div>
            """, unsafe_allow_html=True)
            citation_lines.append(f"[출처] {art['source']}, {art['date']}\n제목: {art['title']}\nURL: {art['url']}")

    for wid in sel_str:
        try:
            idx = int(wid.replace("web_",""))
        except ValueError:
            continue
        results = st.session_state.get("search_results", [])
        if idx < len(results):
            item = results[idx]
            url  = item.get("url","#")
            link = f'<a href="{url}" target="_blank" style="font-size:12px;color:#0284c7;">🔗 출처 보기</a>' if url and url != "#" else ""
            st.markdown(f"""
            <div style="background:#f0fdf4;border-left:4px solid #22c55e;border-radius:10px;padding:10px 14px;margin-bottom:6px;">
                <div style="font-size:12px;color:#15803d;font-weight:700;">{item.get('source_label','')} · 인터넷 검색</div>
                <div style="font-size:14px;color:#14532d;font-weight:600;">"{item.get('evidence','')}"</div>
                {link}
            </div>
            """, unsafe_allow_html=True)
            citation_lines.append(f"[출처] {item.get('source_label','인터넷 자료')}\n제목: {item.get('title','')}\nURL: {url}")

    if citation_lines:
        st.markdown("#### 📋 출처 자동 정리")
        ct = "\n\n".join(citation_lines)
        st.markdown(f'<div class="citation-box">{ct}</div>', unsafe_allow_html=True)
        st.code(ct, language=None)

    if st.button("➡️ 2단계로 가기!", key="btn_to_step2"):
        st.session_state.step = 1; st.rerun()


# ════════════════════════════════════════════════════════════
# 2단계: 반론 펼치기
# ════════════════════════════════════════════════════════════
def step2():
    st.markdown("""
    <div class="card" style="background:linear-gradient(135deg,#fdf4ff,#ede9fe);padding:18px 20px 14px;">
        <div style="font-size:1.3rem;font-weight:900;color:#7c3aed;">🗣️ 2단계: 반론 펼치기</div>
        <div style="font-size:0.85rem;color:#8b5cf6;margin-top:4px;">상대방의 주장을 이해하고, 나의 반론을 준비해봐요!</div>
    </div>
    """, unsafe_allow_html=True)

    is_pro   = any(w in st.session_state.claim for w in ["필요","건설","찬성","해야"])
    opposite = ("해상풍력 발전단지 건설은 어민의 생존권과 해양 생태계를 파괴하므로 중단해야 한다."
                if is_pro else
                "기후 위기를 막으려면 해상풍력 발전단지 건설을 반드시 추진해야 한다.")

    st.markdown(f"""
    <div style="background:#fdf4ff;border-left:5px solid #a855f7;border-radius:12px;padding:14px 18px;margin-bottom:14px;">
        <div style="font-size:11px;font-weight:800;color:#7c3aed;margin-bottom:4px;">🔵 상대방의 주장</div>
        <div style="font-size:15px;font-weight:600;color:#4c1d95;">{opposite}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🤔 반론 도움받기", key="btn_rebuttal"):
        _run_rebuttal(opposite)

    if st.session_state.ai_rebuttal:
        _render_rebuttal_result()


def _run_rebuttal(opposite: str):
    system = """초등학교 6학년 토론 선생님입니다. JSON으로만 응답하세요. 코드블록 없이.
{
  "question":      "상대방이 왜 그렇게 생각했을지 추측하는 질문 (쉬운 말 1문장)",
  "rebuttalHint":  "반론 힌트 2문장 (쉬운 말)",
  "strongerPoint": "내 주장 강화 방법 1문장",
  "weakPoint":     "내 주장 약점과 보완 방법 1문장"
}"""
    with st.spinner("🤔 반론 전략 분석 중..."):
        result = call_gemini_json(system, f"상대 주장: {opposite}\n내 주장: {st.session_state.claim}\n내 이유: {st.session_state.reason}")
    if result.startswith("__NO_KEY__"): render_no_key_warning(); return
    try:
        parsed = json.loads(re.sub(r"```json|```","",result).strip())
    except Exception:
        parsed = {"question":"상대방은 어떤 걱정이 있었을까요?","rebuttalHint":"상대 주장의 약점을 찾아봐요. 우리 편 기사에서 반론 근거를 찾을 수 있어요.","strongerPoint":"통계나 전문가 의견을 넣으면 더 강해요.","weakPoint":"내 주장도 약한 부분이 있는지 생각해봐요."}
    st.session_state.ai_rebuttal = parsed


def _render_rebuttal_result():
    ana = st.session_state.ai_rebuttal
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div style="background:#eff6ff;border-radius:14px;padding:14px;border:1.5px solid #bae6fd;">
            <div style="font-size:12px;font-weight:800;color:#1d4ed8;margin-bottom:6px;">🤔 생각해볼 질문</div>
            <div style="font-size:14px;color:#1e40af;line-height:1.6;">{ana.get('question','')}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style="background:#f0fdf4;border-radius:14px;padding:14px;border:1.5px solid #86efac;">
            <div style="font-size:12px;font-weight:800;color:#166534;margin-bottom:6px;">💡 반론 힌트</div>
            <div style="font-size:14px;color:#14532d;line-height:1.6;">{ana.get('rebuttalHint','')}</div></div>""", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown(f"""<div style="background:#fef9c3;border-radius:14px;padding:14px;border:1.5px solid #fde047;margin-top:8px;">
            <div style="font-size:12px;font-weight:800;color:#854d0e;margin-bottom:4px;">⚡ 주장 강화 포인트</div>
            <div style="font-size:14px;color:#78350f;line-height:1.6;">{ana.get('strongerPoint','')}</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div style="background:#fff1f2;border-radius:14px;padding:14px;border:1.5px solid #fecdd3;margin-top:8px;">
            <div style="font-size:12px;font-weight:800;color:#9f1239;margin-bottom:4px;">🔍 내 주장 약점 체크</div>
            <div style="font-size:14px;color:#881337;line-height:1.6;">{ana.get('weakPoint','내 주장도 다시 점검해봐요.')}</div></div>""", unsafe_allow_html=True)

    st.markdown("**✍️ 내가 쓸 반론**")
    rebuttal = st.text_area("반론", value=st.session_state.rebuttal, placeholder="반론을 직접 써봐요!", height=100, label_visibility="collapsed", key="input_rebuttal")
    st.session_state.rebuttal = rebuttal

    st.markdown("#### 📰 반론 근거 자료")
    for a in ARTICLES: _render_news_card(a)

    if st.button("➡️ 3단계로 가기!", key="btn_to_step3"):
        st.session_state.step = 2; st.rerun()


# ════════════════════════════════════════════════════════════
# 3단계: 주장 다지기
# ════════════════════════════════════════════════════════════
def step3():
    st.markdown("""
    <div class="card" style="background:linear-gradient(135deg,#fff7ed,#fed7aa);padding:18px 20px 14px;">
        <div style="font-size:1.3rem;font-weight:900;color:#c2410c;">🏆 3단계: 주장 다지기</div>
        <div style="font-size:0.85rem;color:#ea580c;margin-top:4px;">가장 강한 근거를 골라 최종 발표문을 완성해봐요!</div>
    </div>
    """, unsafe_allow_html=True)

    render_arg_card("💬 내 최종 주장","arg-claim","💬",st.session_state.claim)
    render_arg_card("🌿 이유","arg-reason","🌿",st.session_state.reason)

    st.markdown("#### 📌 가장 강한 근거를 골라봐요! (여러 개 선택 가능)")
    all_ev = []
    for a in ARTICLES:
        all_ev.append({"key":f"a_{a['id']}", "label":f"[{a['source']}] {a['evidence'][:55]}...", "text":a['evidence'], "source":a['source'], "url":a['url']})
    for i, item in enumerate(st.session_state.get("search_results",[])):
        ev_text = item.get('evidence','')
        all_ev.append({"key":f"w_{i}", "label":f"[인터넷] {ev_text[:55]}...", "text":ev_text, "source":item.get('source_label','인터넷'), "url":item.get('url','')})

    for ev in all_ev:
        checked = ev["key"] in st.session_state.selected_evidence
        if st.checkbox(f"{'✅' if checked else '⬜'} {ev['label']}", value=checked, key=f"ev_{ev['key']}"):
            if ev["key"] not in st.session_state.selected_evidence:
                st.session_state.selected_evidence.append(ev["key"])
        else:
            if ev["key"] in st.session_state.selected_evidence:
                st.session_state.selected_evidence.remove(ev["key"])

    can_gen = len(st.session_state.selected_evidence) > 0
    if st.button("✍️ 최종 발표문 만들기!", disabled=not can_gen, key="btn_speech"):
        _run_speech(all_ev)

    if st.session_state.final_speech:
        _render_final_speech()


def _run_speech(all_ev: list):
    ev_texts = []
    for ekey in st.session_state.selected_evidence:
        item = next((e for e in all_ev if e["key"] == ekey), None)
        if item: ev_texts.append(f"- {item['text']} (출처: {item['source']})")

    system = """초등학교 6학년 토론 선생님. 학생의 주장·이유·근거로 발표문을 써주세요.
- 초등학생이 실제로 말할 수 있는 자연스러운 문체
- 3단락: 주장 → 이유+근거 → 결론
- 각 단락 2~3문장, 전체 300자 이내
- 어려운 말 금지, 친근하고 당당한 말투
- 발표문만 출력하세요"""

    with st.spinner("✍️ 발표문 작성 중..."):
        result = call_gemini_json(system, f"주장: {st.session_state.claim}\n이유: {st.session_state.reason}\n근거:\n" + "\n".join(ev_texts))
    st.session_state.final_speech = result if not result.startswith("__") else "오류가 발생했어요. 다시 시도해 주세요."


def _render_final_speech():
    st.markdown("#### 🎤 나의 최종 발표문")
    st.markdown(f"""
    <div style="background:white;border:2px solid #f97316;border-radius:18px;padding:20px;margin-bottom:16px;">
        <div style="font-size:15px;color:#1e293b;line-height:1.9;white-space:pre-wrap;">{st.session_state.final_speech}</div>
    </div>
    """, unsafe_allow_html=True)
    st.code(st.session_state.final_speech, language=None)
    st.markdown("""
    <div style="background:#fef9c3;border-radius:16px;padding:18px;text-align:center;border:2px solid #fde047;margin-top:8px;">
        <div style="font-size:2rem;">🎉</div>
        <div style="font-size:1.1rem;font-weight:900;color:#854d0e;">토론 준비 완료!</div>
        <div style="font-size:0.85rem;color:#92400e;">주장·이유·근거를 모두 갖춘 훌륭한 토론자예요!</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔄 처음부터 다시 하기", key="btn_restart"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()


# ════════════════════════════════════════════════════════════
# 메인
# ════════════════════════════════════════════════════════════
def main():
    init_session()
    render_header()
    render_progress(st.session_state.step)
    if not st.secrets.get("GEMINI_API_KEY",""):
        render_no_key_warning()
    if   st.session_state.step == 0: step1()
    elif st.session_state.step == 1: step2()
    elif st.session_state.step == 2: step3()
    st.markdown("""
    <div class="info-box">
        💡 <b>주장</b>은 내 생각 &nbsp;·&nbsp; <b>이유</b>는 왜 그렇게 생각하는지 &nbsp;·&nbsp; <b>근거</b>는 이유를 뒷받침하는 <b>객관적 자료</b>예요!
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
