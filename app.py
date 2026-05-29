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
        "search_error": "",
        "filtered_articles": ARTICLES,
        # 1단계 고쳐쓰기
        "revised_claim": "", "revised_reason": "",
        "revision_feedback": None, "show_hint": False,
        # 2단계 반론
        "rebuttal_admit": "", "rebuttal_but": "", "rebuttal_evidence": "",
        "rebuttal": "", "ai_rebuttal": None,
        "rebuttal_feedback": None,
        # 3단계
        "best_evidence_key": "", "best_evidence_reason": "",
        "final_speech": "", "selected_evidence": [],
        "revision_hint": None,
        "substep": "main",  # "main" | "rewrite"
        "revised_evidence": "",
        "combined_essay": "",
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
    """단계 버튼 — 클릭하면 해당 단계로 이동"""
    revised_done = bool(st.session_state.get("revised_claim", ""))

    # 단계 정의: (label, target_step, 접근 가능 조건)
    stages = [
        ("🌊 1단계 주장 펼치기",  0, True),
        ("✏️ 고쳐쓰기",           0, True),
        ("🗣️ 2단계 반론하기",    1, True),
        ("🏆 3단계 주장 다지기", 2, True),
    ]

    # 각 단계 상태 계산
    def get_state(idx):
        if idx == 0:   # 주장 펼치기
            return "active" if step == 0 else "done"
        elif idx == 1: # 고쳐쓰기
            if revised_done: return "done"
            if step == 0:    return "sub"    # 1단계 내부 서브
            return "done"
        elif idx == 2: # 반론
            if step == 1: return "active"
            if step == 2: return "done"
            return "todo"
        elif idx == 3: # 다지기
            if step == 2: return "active"
            return "todo"
        return "todo"

    state_style = {
        "active": ("background:#0ea5e9;color:white;border:2px solid #0284c7;",          "▶ "),
        "done":   ("background:#bbf7d0;color:#166534;border:2px solid #86efac;",        "✅ "),
        "sub":    ("background:#fef9c3;color:#854d0e;border:2px dashed #fde047;",       "✏️ "),
        "todo":   ("background:#f1f5f9;color:#94a3b8;border:2px solid #e2e8f0;",        ""),
    }

    cols = st.columns(4)
    for idx, (label, target_step, accessible) in enumerate(stages):
        state = get_state(idx)
        style, prefix = state_style[state]
        display = prefix + label.replace("\n", " ")
        with cols[idx]:
            if st.button(
                display,
                key=f"nav_step_{idx}",
                help=f"{'클릭해서 이동' if accessible else '아직 이동 불가'}",
                use_container_width=True,
            ):
                if accessible:
                    st.session_state.step = target_step
                    if idx == 0:                              # 1단계 버튼
                        st.session_state.substep = "main"    # 반드시 main으로
                    elif idx == 1:                            # 고쳐쓰기 버튼
                        st.session_state.substep = "rewrite"
                    st.rerun()

    st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

    # CSS: 버튼 스타일 개별 적용 (Streamlit 버튼 override)
    st.markdown("""
    <style>
    div[data-testid="column"] button[kind="secondary"] {
        border-radius: 12px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        padding: 8px 4px !important;
        white-space: pre-wrap !important;
        line-height: 1.4 !important;
        min-height: 52px !important;
    }
    </style>
    """, unsafe_allow_html=True)


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


# ── 웹 검색 결과 카드 (제목 + 링크 + 선택 버튼) ─────────────────
def _render_search_card(item: dict, idx: int):
    wid    = f"web_{idx}"
    is_sel = wid in st.session_state.selected_articles
    url    = item.get("url", "")
    title  = item.get("title", "기사 제목")
    source = item.get("source_label", "뉴스")
    side   = item.get("side", "neutral")

    side_badge = {
        "pro":     '<span style="background:#dcfce7;color:#166534;border-radius:99px;padding:2px 9px;font-size:11px;font-weight:800;">🟢 찬성 측</span>',
        "con":     '<span style="background:#fee2e2;color:#991b1b;border-radius:99px;padding:2px 9px;font-size:11px;font-weight:800;">🔴 반대 측</span>',
        "neutral": '<span style="background:#f1f5f9;color:#475569;border-radius:99px;padding:2px 9px;font-size:11px;font-weight:800;">🔵 참고</span>',
    }.get(side, "")

    link_btn = (
        f'<a href="{url}" target="_blank" style="display:inline-block;background:#0ea5e9;color:white;'
        f'border-radius:10px;padding:7px 16px;font-size:13px;font-weight:800;text-decoration:none;">'
        f'🔗 기사 읽으러 가기 ↗</a>'
    ) if url else '<span style="font-size:12px;color:#94a3b8;">링크 없음</span>'

    border = "2px solid #0ea5e9" if is_sel else "1.5px solid #e2e8f0"
    bg     = "#f0f9ff" if is_sel else "white"

    st.markdown(f"""
    <div style="background:{bg};border:{border};border-radius:16px;padding:16px;margin-bottom:10px;">
        <div style="font-size:12px;color:#0ea5e9;font-weight:700;margin-bottom:6px;">
            📰 {source} &nbsp; {side_badge}
        </div>
        <div style="font-size:15px;font-weight:800;color:#0f172a;line-height:1.5;margin-bottom:12px;">
            {title}
        </div>
        <div style="background:#fff7ed;border-left:4px solid #f97316;border-radius:8px;
                    padding:10px 14px;margin-bottom:12px;font-size:13px;color:#92400e;line-height:1.6;">
            💡 <b>이 기사를 읽고</b> 내 주장과 관련된 사실·수치·발언을 찾아서<br>
            아래 <b>근거 메모</b> 칸에 직접 정리해봐요!
        </div>
        <div style="display:flex;align-items:center;gap:10px;">
            {link_btn}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 선택 버튼
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("✅ 선택됨!" if is_sel else "📌 이 기사 근거로 쓸게요", key=f"sel_web_{idx}"):
            if is_sel:
                st.session_state.selected_articles.remove(wid)
            else:
                st.session_state.selected_articles.append(wid)
            st.rerun()
    with col2:
        # 기사별 메모 입력
        memo_key = f"memo_web_{idx}"
        if memo_key not in st.session_state:
            st.session_state[memo_key] = ""
        memo = st.text_input(
            "📝 내가 찾은 근거 문장",
            value=st.session_state[memo_key],
            placeholder="기사에서 찾은 핵심 문장을 적어봐요",
            key=f"input_memo_{idx}",
            label_visibility="collapsed",
        )
        if memo:
            st.session_state[memo_key] = memo
            # 메모가 있으면 자동 선택
            if wid not in st.session_state.selected_articles:
                st.session_state.selected_articles.append(wid)
            # search_results에 메모 반영
            results = st.session_state.get("search_results", [])
            if idx < len(results):
                results[idx]["evidence"] = memo
                results[idx]["why"]      = "내가 직접 기사를 읽고 찾은 근거예요."



# ════════════════════════════════════════════════════════════
# 1단계: 주장 펼치기
# ════════════════════════════════════════════════════════════
def step1():
    # substep 분기: "main" | "rewrite"
    if st.session_state.get("substep","main") == "rewrite":
        step1_rewrite()
        return

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


def step1_rewrite():
    """고쳐쓰기 전용 페이지 — 주장·이유·근거 + 글 합치기"""
    ana = st.session_state.ai_analysis or {}

    st.markdown("""
    <div style="background:linear-gradient(135deg,#fef9c3,#fde68a);border-radius:18px;
                padding:18px 20px 14px;margin-bottom:16px;">
        <div style="font-size:1.3rem;font-weight:900;color:#92400e;">✏️ 고쳐쓰기</div>
        <div style="font-size:0.85rem;color:#78350f;margin-top:4px;">
            AI 피드백과 찾은 근거를 보면서 주장·이유·근거를 고쳐쓰고, 하나의 글로 완성해봐요!
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 상단: 처음 쓴 글 + AI 피드백 나란히 ──
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("#### 📄 처음 쓴 글")
        score_icon = {"매우잘함": "🌟", "잘함": "👍", "노력바람": "💪"}
        cs = ana.get("claimScore", "잘함")
        rs = ana.get("reasonScore", "잘함")

        # 일관성 경고
        if not ana.get("isConsistent", True):
            st.markdown(f"""
            <div style="background:#fff1f2;border:2px solid #f87171;border-radius:10px;
                        padding:10px 14px;margin-bottom:8px;font-size:12px;color:#b91c1c;font-weight:700;">
                ⚠️ 주장({ana.get("claimStance","")})과 이유({ana.get("reasonStance","")})
                방향이 달라요! 고쳐야 해요.
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#eff6ff;border-left:4px solid #3b82f6;border-radius:10px;
                    padding:12px 14px;margin-bottom:8px;font-size:14px;line-height:1.6;">
            <div style="font-size:11px;font-weight:800;color:#1d4ed8;margin-bottom:4px;">
                💬 주장 {score_icon.get(cs,"")} {cs}
            </div>
            {st.session_state.claim}
        </div>
        <div style="background:#f0fdf4;border-left:4px solid #22c55e;border-radius:10px;
                    padding:12px 14px;font-size:14px;line-height:1.6;">
            <div style="font-size:11px;font-weight:800;color:#166534;margin-bottom:4px;">
                🌿 이유 {score_icon.get(rs,"")} {rs}
            </div>
            {st.session_state.reason}
        </div>
        """, unsafe_allow_html=True)

        # 내가 찾은 근거 목록
        memos, art_evidences = [], []
        for i, item in enumerate(st.session_state.get("search_results", [])):
            memo = st.session_state.get(f"memo_web_{i}", "")
            if memo:
                memos.append(f"• {memo} ({item.get('source_label','')})")
        for sid in [s for s in st.session_state.get("selected_articles",[]) if isinstance(s, int)]:
            art = next((a for a in ARTICLES if a["id"] == sid), None)
            if art:
                art_evidences.append(f"• {art['evidence']} ({art['source']})")

        all_ev_list = memos + art_evidences
        if all_ev_list:
            st.markdown(f"""
            <div style="background:#fff7ed;border-left:4px solid #f97316;border-radius:10px;
                        padding:12px 14px;margin-top:8px;font-size:13px;color:#92400e;line-height:1.8;">
                <b>📌 내가 찾은 근거:</b><br>{"<br>".join(all_ev_list)}
            </div>
            """, unsafe_allow_html=True)

    with col_r:
        st.markdown("#### 💡 AI 피드백")

        if not ana.get("isConsistent", True):
            st.markdown(f"""
            <div style="background:#fff1f2;border-radius:10px;padding:10px 14px;
                        font-size:13px;color:#991b1b;margin-bottom:8px;line-height:1.7;">
                <b>🚨 일관성 문제:</b><br>{ana.get("consistencyAlert","")}
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#fff7ed;border-radius:10px;padding:12px 14px;
                    font-size:13px;color:#92400e;line-height:1.9;margin-bottom:8px;">
            {"<b>💬 주장 개선:</b> " + ana.get("claimImprove","") + "<br>" if ana.get("claimImprove") else "<b>💬 주장:</b> 잘 썼어요!<br>"}
            {"<b>🌿 이유 개선:</b> " + ana.get("reasonImprove","") + "<br>" if ana.get("reasonImprove") else "<b>🌿 이유:</b> 잘 썼어요!<br>"}
            {"<b>🤔 더 생각해봐요:</b> " + ana.get("reasonDeeperQ","") if ana.get("reasonDeeperQ") else ""}
        </div>
        """, unsafe_allow_html=True)

        # 근거 힌트
        en = ana.get("evidenceNeed", {})
        if en:
            st.markdown(f"""
            <div style="background:#f0fdf4;border-radius:10px;padding:12px 14px;
                        font-size:13px;color:#166534;line-height:1.8;">
                <b>📊 필요한 근거:</b><br>
                통계: {en.get("stat","")}<br>
                전문가: {en.get("expert","")}<br>
                사례: {en.get("case","")}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── 고쳐쓰기 입력 3칸 ──
    st.markdown("#### ✏️ 고쳐 쓴 글")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown('<div style="font-size:13px;font-weight:800;color:#1d4ed8;margin-bottom:4px;">💬 고쳐 쓴 주장</div>', unsafe_allow_html=True)
        revised_claim = st.text_area("고쳐쓴주장",
            value=st.session_state.revised_claim,
            placeholder="주장을 고쳐봐요. 입장이 명확하게!",
            height=130, label_visibility="collapsed", key="rw_claim")

    with c2:
        st.markdown('<div style="font-size:13px;font-weight:800;color:#166534;margin-bottom:4px;">🌿 고쳐 쓴 이유</div>', unsafe_allow_html=True)
        revised_reason = st.text_area("고쳐쓴이유",
            value=st.session_state.revised_reason,
            placeholder="이유를 더 구체적으로 고쳐봐요. 왜냐하면~",
            height=130, label_visibility="collapsed", key="rw_reason")

    with c3:
        st.markdown('<div style="font-size:13px;font-weight:800;color:#c2410c;margin-bottom:4px;">📌 고쳐 쓴 근거</div>', unsafe_allow_html=True)
        revised_evidence = st.text_area("고쳐쓴근거",
            value=st.session_state.revised_evidence,
            placeholder="찾은 기사에서 근거 문장을 옮겨 써봐요.\n출처도 함께 써주세요!",
            height=130, label_visibility="collapsed", key="rw_evidence")

    # 힌트 + 완료 버튼
    col_hint, col_done = st.columns([1, 1])
    with col_hint:
        if st.button("🆘 막혔어요! 예시 힌트", key="btn_hint_rw", use_container_width=True):
            st.session_state.show_hint = True
            _run_hint()
    with col_done:
        can_done = bool(revised_claim.strip() and revised_reason.strip())
        if st.button("✅ 고쳐쓰기 완료!", disabled=not can_done,
                     key="btn_revision_done_rw", use_container_width=True):
            st.session_state.revised_claim    = revised_claim
            st.session_state.revised_reason   = revised_reason
            st.session_state.revised_evidence = revised_evidence
            _run_revision_feedback(revised_claim, revised_reason, revised_evidence)

    # 힌트 표시
    if st.session_state.get("show_hint") and st.session_state.get("revision_hint"):
        hint = st.session_state.revision_hint
        st.markdown(f"""
        <div style="background:#ede9fe;border-left:4px solid #8b5cf6;border-radius:12px;
                    padding:14px 16px;margin-top:10px;font-size:14px;color:#4c1d95;line-height:1.7;">
            <div style="font-weight:800;margin-bottom:6px;">🆘 예시 힌트</div>
            <b>주장 예시:</b> {hint.get("claimExample","")}<br><br>
            <b>이유 예시:</b> {hint.get("reasonExample","")}<br><br>
            <b>근거 예시:</b> {hint.get("evidenceExample","연구 결과에 따르면 해상풍력은 탄소 배출을 크게 줄입니다. (출처: 환경부, 2024)")}<br>
            <div style="margin-top:8px;font-size:12px;color:#6d28d9;">
                💡 예시를 그대로 쓰지 말고, 참고해서 나만의 문장으로 바꿔봐요!
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 고쳐쓰기 피드백 + 글 합치기
    if st.session_state.get("revision_feedback"):
        _render_revision_feedback()


def _render_rewrite_section():
    pass  # step1_rewrite()로 대체됨


def _run_hint():
    """막혔을 때 조건부 힌트 예시 생성"""
    ana = st.session_state.ai_analysis or {}
    sys_prompt = f"""초등학교 6학년 토론 선생님입니다.
학생이 주장·이유·근거를 고쳐쓰다가 막혔어요. 예시 힌트를 주세요.

원래 주장: {st.session_state.claim}
원래 이유: {st.session_state.reason}
주장 개선점: {ana.get("claimImprove","")}
이유 개선점: {ana.get("reasonImprove","")}
토론 주제: {TOPIC}

코드블록 없이 JSON만 출력:
{{
  "claimExample": "고쳐쓴 주장 예시 1문장 (학생 입장 유지, 지침 반영)",
  "reasonExample": "고쳐쓴 이유 예시 1~2문장 (구체적 인과관계 포함)",
  "evidenceExample": "근거 예시 1문장 (출처 포함, 예: OO에 따르면 ~하다 (출처: 환경부, 2024))"
}}"""
    with st.spinner("🆘 힌트 생성 중..."):
        result = call_gemini_json(sys_prompt, "")
    try:
        st.session_state.revision_hint = json.loads(re.sub(r"```json|```|`","",result).strip())
    except Exception:
        st.session_state.revision_hint = {
            "claimExample": "해상풍력 발전단지 건설은 기후 위기를 막기 위해 반드시 필요하다.",
            "reasonExample": "왜냐하면 석탄·가스 대신 바람으로 전기를 만들면 이산화탄소가 줄어들기 때문이다.",
            "evidenceExample": "환경부에 따르면 해상풍력 발전은 같은 전력량 대비 탄소 배출을 95% 줄일 수 있다. (출처: 환경부, 2023)",
        }


def _run_revision_feedback(revised_claim: str, revised_reason: str, revised_evidence: str = ""):
    """고쳐쓴 글 vs 원본 비교 피드백"""
    sys_prompt = f"""초등학교 6학년 토론 선생님입니다.
학생이 피드백을 받고 주장과 이유를 고쳐 썼어요. 전후를 비교해서 칭찬해주세요.

[원본]
주장: {st.session_state.claim}
이유: {st.session_state.reason}

[고쳐쓴 글]
주장: {revised_claim}
이유: {revised_reason}
근거: {revised_evidence if revised_evidence else "(미작성)"}

코드블록 없이 JSON만 출력:
{{
  "overallPraise": "전체적으로 어떻게 좋아졌는지 칭찬 2문장 (초등학생 언어, 구체적으로)",
  "claimChange": "주장이 어떻게 좋아졌는지 1문장",
  "reasonChange": "이유가 어떻게 좋아졌는지 1문장",
  "evidenceChange": "근거가 잘 작성됐는지 평가 1문장 (없으면 근거 추가 권유)",
  "stillImprove": "아직 아쉬운 점 1문장 (있으면, 없으면 빈 문자열)",
  "readyForDebate": true 또는 false
}}"""
    with st.spinner("📝 고쳐쓴 글을 비교하고 있어요..."):
        result = call_gemini_json(sys_prompt, "")
    try:
        parsed = json.loads(re.sub(r"```json|```|`","",result).strip())
    except Exception:
        parsed = {
            "overallPraise": "고쳐쓰기를 열심히 했어요! 주장이 훨씬 명확해졌어요.",
            "claimChange": "주장에 주어가 생겨서 무엇에 대한 주장인지 잘 드러나요.",
            "reasonChange": "이유에 구체적인 설명이 더해졌어요.",
            "evidenceChange": "근거도 잘 찾았어요!" if revised_evidence else "근거를 추가하면 더 강한 글이 돼요.",
            "stillImprove": "",
            "readyForDebate": True,
        }
    st.session_state.revision_feedback = parsed
    st.session_state.revised_claim    = revised_claim
    st.session_state.revised_reason   = revised_reason
    st.session_state.revised_evidence = revised_evidence


def _render_revision_feedback():
    fb = st.session_state.revision_feedback
    ready = fb.get("readyForDebate", True)

    emoji = "🎉" if ready else "💪"
    bg    = "#f0fdf4" if ready else "#fef9c3"
    border= "#22c55e" if ready else "#fde047"

    st.markdown(f"""
    <div style="background:{bg};border:2px solid {border};border-radius:16px;
                padding:18px;margin-top:14px;">
        <div style="font-size:1.1rem;font-weight:900;color:#166534;margin-bottom:10px;">
            {emoji} 고쳐쓰기 피드백
        </div>
        <div style="font-size:14px;color:#14532d;line-height:1.8;">
            <b>🌟 전체 평가:</b> {fb.get("overallPraise","")}<br>
            <b>💬 주장 변화:</b> {fb.get("claimChange","")}<br>
            <b>🌿 이유 변화:</b> {fb.get("reasonChange","")}<br>
            {"<b>💡 아직 아쉬운 점:</b> " + fb.get("stillImprove","") if fb.get("stillImprove") else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 전후 나란히 비교 (3칸)
    st.markdown("#### 📊 처음 vs 고쳐쓴 글 비교")
    col_b, col_a = st.columns(2)
    with col_b:
        st.markdown(f"""
        <div style="background:#fee2e2;border-radius:12px;padding:14px;font-size:13px;line-height:1.7;">
            <div style="font-weight:800;color:#991b1b;margin-bottom:6px;">📄 처음 쓴 글</div>
            <b>주장:</b> {st.session_state.claim}<br><br>
            <b>이유:</b> {st.session_state.reason}
        </div>
        """, unsafe_allow_html=True)
    with col_a:
        ev_txt = st.session_state.get("revised_evidence","")
        st.markdown(f"""
        <div style="background:#dcfce7;border-radius:12px;padding:14px;font-size:13px;line-height:1.7;">
            <div style="font-weight:800;color:#166534;margin-bottom:6px;">✏️ 고쳐쓴 글</div>
            <b>주장:</b> {st.session_state.revised_claim}<br><br>
            <b>이유:</b> {st.session_state.revised_reason}<br><br>
            <b>근거:</b> {ev_txt if ev_txt else "<span style='color:#94a3b8'>미작성</span>"}
        </div>
        """, unsafe_allow_html=True)

    # ── 글 합치기 ──
    st.markdown("---")
    st.markdown("#### 📝 주장하는 글 완성하기")
    st.markdown("""
    <div style="background:#f0f9ff;border-radius:12px;padding:10px 14px;
                margin-bottom:10px;font-size:13px;color:#0369a1;line-height:1.7;">
        💡 고쳐쓴 주장·이유·근거를 합쳐서 하나의 완성된 주장하는 글을 만들어봐요!
        AI가 자연스럽게 이어주거나, 직접 써볼 수도 있어요.
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("🤖 AI가 글 합쳐주기", key="btn_combine_ai", use_container_width=True):
            _run_combine_essay()
    with c2:
        if st.button("✍️ 내가 직접 쓸게요", key="btn_combine_manual", use_container_width=True):
            # 빈칸으로 직접 쓰기 모드
            st.session_state.combined_essay = (
                f"{st.session_state.revised_claim} "
                f"{st.session_state.revised_reason} "
                f"{st.session_state.get('revised_evidence','')}"
            ).strip()

    if st.session_state.get("combined_essay"):
        combined = st.text_area("완성된 주장하는 글",
            value=st.session_state.combined_essay,
            height=150, key="essay_edit",
            label_visibility="collapsed")
        st.session_state.combined_essay = combined

        st.markdown(f"""
        <div style="background:white;border:2px solid #0ea5e9;border-radius:14px;
                    padding:16px;margin-top:8px;">
            <div style="font-size:11px;font-weight:800;color:#0369a1;margin-bottom:8px;">
                📋 최종 완성된 주장하는 글
            </div>
            <div style="font-size:15px;color:#0f172a;line-height:1.9;white-space:pre-wrap;">
                {combined}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.code(combined, language=None)

    if ready:
        st.markdown("""
        <div style="background:#dcfce7;border-radius:12px;padding:12px 16px;
                    text-align:center;margin-top:10px;font-size:14px;
                    font-weight:800;color:#166534;">
            🎯 훌륭해요! 이제 반론 단계로 넘어갈 준비가 됐어요!
        </div>
        """, unsafe_allow_html=True)

    if st.button("➡️ 2단계: 반론하기로 가기!", key="btn_goto_step2_from_revision"):
        st.session_state.step    = 1
        st.session_state.substep = "main"
        st.rerun()


def _run_combine_essay():
    """주장+이유+근거를 하나의 자연스러운 글로 합치기"""
    rc = st.session_state.revised_claim
    rr = st.session_state.revised_reason
    re_ev = st.session_state.get("revised_evidence", "")

    sys_p = """초등학교 6학년 학생이 쓴 주장·이유·근거를 하나의 자연스러운 주장하는 글로 완성해주세요.

[조건]
- 주장 → 이유 → 근거 순서로 자연스럽게 연결
- 연결어 활용: "왜냐하면", "또한", "따라서", "이처럼" 등
- 전체 150~200자 (초등학생이 실제로 발표할 수 있는 분량)
- 어려운 말 금지, 자연스럽고 당당한 말투
- 글만 출력 (설명 없이)"""

    user_msg = f"주장: {rc}\n이유: {rr}\n근거: {re_ev if re_ev else '(없음)'}"

    with st.spinner("📝 글을 합치고 있어요..."):
        result = call_gemini_json(sys_p, user_msg)

    st.session_state.combined_essay = result if not result.startswith("__") else f"{rc} {rr} {re_ev}".strip()


# ════════════════════════════════════════════════════════════
# 2단계: 반론 펼치기
# ════════════════════════════════════════════════════════════
def step2():
    st.markdown("""
    <div class="card" style="background:linear-gradient(135deg,#fdf4ff,#ede9fe);padding:18px 20px 14px;">
        <div style="font-size:1.3rem;font-weight:900;color:#7c3aed;">🗣️ 2단계: 반론 펼치기</div>
        <div style="font-size:0.85rem;color:#8b5cf6;margin-top:4px;">
            상대방 입장을 이해하고, 인정+하지만+근거 구조로 반론해봐요!
        </div>
    </div>
    """, unsafe_allow_html=True)

    is_pro   = any(w in st.session_state.claim for w in ["필요","건설","찬성","해야"])
    opposite = ("해상풍력 발전단지 건설은 어민의 생존권과 해양 생태계를 파괴하므로 중단해야 한다."
                if is_pro else
                "기후 위기를 막으려면 해상풍력 발전단지 건설을 반드시 추진해야 한다.")

    # 상대 주장
    st.markdown(f"""
    <div style="background:#fdf4ff;border-left:5px solid #a855f7;border-radius:12px;
                padding:14px 18px;margin-bottom:16px;">
        <div style="font-size:11px;font-weight:800;color:#7c3aed;margin-bottom:4px;">🔵 상대방의 주장</div>
        <div style="font-size:15px;font-weight:600;color:#4c1d95;">{opposite}</div>
    </div>
    """, unsafe_allow_html=True)

    # STEP A: 역지사지 — 상대 입장 이해하기
    st.markdown("### 🤔 STEP 1. 상대방 입장 이해하기")
    st.markdown("""
    <div style="background:#f5f3ff;border-radius:12px;padding:12px 16px;
                margin-bottom:12px;font-size:13px;color:#5b21b6;line-height:1.7;">
        반론을 잘 하려면 먼저 상대방의 입장을 이해해야 해요.<br>
        "상대방은 왜 그렇게 생각할까?"를 생각해보고 써봐요.
    </div>
    """, unsafe_allow_html=True)

    if st.button("💡 상대방 입장 분석해줘", key="btn_rebuttal"):
        _run_rebuttal(opposite)

    if st.session_state.ai_rebuttal:
        ana = st.session_state.ai_rebuttal
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px;">
            <div style="background:#eff6ff;border-radius:12px;padding:13px;border:1.5px solid #bae6fd;">
                <div style="font-size:11px;font-weight:800;color:#1d4ed8;margin-bottom:5px;">🤔 상대방이 이렇게 생각하는 이유</div>
                <div style="font-size:13px;color:#1e40af;line-height:1.6;">{ana.get("question","")}</div>
            </div>
            <div style="background:#fff1f2;border-radius:12px;padding:13px;border:1.5px solid #fecdd3;">
                <div style="font-size:11px;font-weight:800;color:#9f1239;margin-bottom:5px;">🔍 내 주장의 약점</div>
                <div style="font-size:13px;color:#881337;line-height:1.6;">{ana.get("weakPoint","")}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # STEP B: 인정+하지만+근거 구조 연습
        st.markdown("### ✍️ STEP 2. 반론 구조로 써봐요")
        st.markdown("""
        <div style="background:#fdf4ff;border-radius:12px;padding:12px 16px;margin-bottom:14px;">
            <div style="font-size:13px;font-weight:800;color:#7c3aed;margin-bottom:8px;">
                📐 반론의 3단계 구조
            </div>
            <div style="display:flex;gap:8px;font-size:13px;">
                <div style="background:#dbeafe;border-radius:8px;padding:8px 12px;flex:1;text-align:center;">
                    <b style="color:#1d4ed8;">① 인정하기</b><br>
                    <span style="color:#3730a3;font-size:12px;">"그 말도 맞아요,<br>하지만..."</span>
                </div>
                <div style="background:#dcfce7;border-radius:8px;padding:8px 12px;flex:1;text-align:center;">
                    <b style="color:#166534;">② 하지만 + 반론</b><br>
                    <span style="color:#14532d;font-size:12px;">내 핵심 반론을<br>써요</span>
                </div>
                <div style="background:#fff7ed;border-radius:8px;padding:8px 12px;flex:1;text-align:center;">
                    <b style="color:#c2410c;">③ 근거 제시</b><br>
                    <span style="color:#9a3412;font-size:12px;">기사·자료로<br>뒷받침해요</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3칸 구조 입력
        st.markdown("**① 상대방 주장의 일부를 인정하는 문장**")
        admit = st.text_area("인정", value=st.session_state.rebuttal_admit,
            placeholder='예) "어민들의 생존권이 중요하다는 점은 맞습니다."',
            height=70, label_visibility="collapsed", key="input_admit")

        st.markdown("**② 하지만 + 내 반론**")
        but = st.text_area("반론", value=st.session_state.rebuttal_but,
            placeholder='예) "하지만 기후 위기를 막지 않으면 결국 바다 생태계가 파괴되어 어민도 더 큰 피해를 입습니다."',
            height=80, label_visibility="collapsed", key="input_but")

        st.markdown("**③ 근거 (기사·자료 내용)**")
        ev = st.text_area("근거", value=st.session_state.rebuttal_evidence,
            placeholder='예) "오마이뉴스에 따르면, 기후 변화로 어획량이 매년 줄어들고 있습니다."',
            height=70, label_visibility="collapsed", key="input_ev")

        # 자동 완성된 반론문 미리보기
        if admit.strip() and but.strip():
            full_rebuttal = f"{admit} {but}{(' ' + ev) if ev.strip() else ''}"
            st.markdown(f"""
            <div style="background:#f5f3ff;border-left:4px solid #8b5cf6;border-radius:12px;
                        padding:12px 16px;margin:10px 0;font-size:14px;color:#4c1d95;line-height:1.7;">
                <div style="font-size:11px;font-weight:800;margin-bottom:5px;">📝 완성된 반론문 미리보기</div>
                {full_rebuttal}
            </div>
            """, unsafe_allow_html=True)
        else:
            full_rebuttal = ""

        # 반론 근거 자료 (제공 기사)
        with st.expander("📰 반론 근거 자료 보기"):
            for a in ARTICLES:
                _render_news_card(a)

        # STEP C: AI 피드백
        can_fb = bool(admit.strip() and but.strip())
        if st.button("🔍 내 반론 피드백 받기", disabled=not can_fb, key="btn_rebuttal_fb"):
            st.session_state.rebuttal_admit    = admit
            st.session_state.rebuttal_but      = but
            st.session_state.rebuttal_evidence = ev
            st.session_state.rebuttal          = full_rebuttal
            _run_rebuttal_feedback(opposite, admit, but, ev)

        if st.session_state.rebuttal_feedback:
            _render_rebuttal_feedback()


def _run_rebuttal(opposite: str):
    sys_p = """초등학교 6학년 토론 선생님입니다. JSON으로만 응답하세요. 코드블록 없이.
{
  "question":   "상대방이 왜 그렇게 생각하는지 이유 추측 2문장 (초등학생 언어)",
  "weakPoint":  "내 주장의 약점 1문장 + 어떻게 보완하면 좋을지 (초등학생 언어)",
  "rebuttalHint": "인정+하지만+근거 구조 힌트 2문장"
}"""
    with st.spinner("🤔 상대방 입장 분석 중..."):
        result = call_gemini_json(sys_p,
            f"상대 주장: {opposite}\n내 주장: {st.session_state.claim}\n내 이유: {st.session_state.reason}")
    if result.startswith("__NO_KEY__"): render_no_key_warning(); return
    try:
        parsed = json.loads(re.sub(r"```json|```|`","",result).strip())
    except Exception:
        parsed = {"question":"상대방은 어민 피해를 걱정하기 때문이에요.",
                  "weakPoint":"내 주장은 환경 측면만 강조했어요. 어민 보상 방안도 함께 이야기하면 더 좋아요.",
                  "rebuttalHint":"상대방 주장의 좋은 점을 먼저 인정하고, '하지만'으로 연결해봐요."}
    st.session_state.ai_rebuttal = parsed


def _run_rebuttal_feedback(opposite, admit, but, ev):
    sys_p = f"""초등학교 6학년 토론 선생님입니다.
학생이 인정+하지만+근거 구조로 반론을 썼어요. 피드백해주세요.

상대 주장: {opposite}
① 인정: {admit}
② 하지만+반론: {but}
③ 근거: {ev}

코드블록 없이 JSON만 출력:
{{
  "structurePraise": "인정+하지만+근거 구조를 잘 지켰는지 칭찬 1~2문장",
  "admitFb":   "인정 부분 피드백 1문장",
  "butFb":     "반론 부분 피드백 1문장",
  "evFb":      "근거 부분 피드백 1문장 (근거가 없으면 근거 추가 권유)",
  "overall":   "전체 반론 강도 평가: 강함/보통/약함 중 하나",
  "tip":       "반론을 더 강하게 만드는 팁 1문장"
}}"""
    with st.spinner("🔍 반론 피드백 분석 중..."):
        result = call_gemini_json(sys_p, "")
    try:
        parsed = json.loads(re.sub(r"```json|```|`","",result).strip())
    except Exception:
        parsed = {"structurePraise":"구조를 잘 지켰어요!","admitFb":"인정 부분이 자연스러워요.",
                  "butFb":"반론이 명확해요.","evFb":"근거를 추가하면 더 강해져요.",
                  "overall":"보통","tip":"구체적인 수치가 있는 근거를 추가해봐요."}
    st.session_state.rebuttal_feedback = parsed


def _render_rebuttal_feedback():
    fb = st.session_state.rebuttal_feedback
    strength = fb.get("overall","보통")
    strength_color = {"강함":"#166534","보통":"#854d0e","약함":"#991b1b"}.get(strength,"#334155")
    strength_bg    = {"강함":"#dcfce7","보통":"#fef9c3","약함":"#fee2e2"}.get(strength,"#f1f5f9")

    st.markdown(f"""
    <div style="background:white;border:2px solid #8b5cf6;border-radius:16px;padding:18px;margin-top:14px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
            <div style="font-size:1rem;font-weight:900;color:#7c3aed;">🔍 반론 피드백</div>
            <span style="background:{strength_bg};color:{strength_color};border-radius:99px;
                         padding:3px 12px;font-size:12px;font-weight:800;">
                반론 강도: {strength}
            </span>
        </div>
        <div style="font-size:13px;line-height:1.9;color:#1e293b;">
            <b>🌟 구조 평가:</b> {fb.get("structurePraise","")}<br>
            <b>① 인정:</b> {fb.get("admitFb","")}<br>
            <b>② 반론:</b> {fb.get("butFb","")}<br>
            <b>③ 근거:</b> {fb.get("evFb","")}<br>
            <b>💡 강화 팁:</b> {fb.get("tip","")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➡️ 3단계: 주장 다지기로 가기!", key="btn_to_step3"):
        st.session_state.step = 2
        st.rerun()


# ════════════════════════════════════════════════════════════
# 3단계: 주장 다지기
# ════════════════════════════════════════════════════════════
def step3():
    st.markdown("""
    <div class="card" style="background:linear-gradient(135deg,#fff7ed,#fed7aa);padding:18px 20px 14px;">
        <div style="font-size:1.3rem;font-weight:900;color:#c2410c;">🏆 3단계: 주장 다지기</div>
        <div style="font-size:0.85rem;color:#ea580c;margin-top:4px;">
            가장 강한 근거 1개를 선택하고, 최종 발표문을 완성해봐요!
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── STEP A: 처음 vs 고쳐쓴 글 비교 ──────────────────────────
    st.markdown("### 📊 STEP 1. 내 글의 성장 확인하기")
    has_revised = bool(st.session_state.revised_claim)

    col_orig, col_rev = st.columns(2)
    with col_orig:
        st.markdown(f"""
        <div style="background:#fee2e2;border-radius:14px;padding:14px;min-height:140px;">
            <div style="font-size:12px;font-weight:800;color:#991b1b;margin-bottom:8px;">
                📄 처음 쓴 글
            </div>
            <div style="font-size:13px;color:#7f1d1d;line-height:1.7;">
                <b>주장:</b> {st.session_state.claim}<br><br>
                <b>이유:</b> {st.session_state.reason}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_rev:
        if has_revised:
            st.markdown(f"""
            <div style="background:#dcfce7;border-radius:14px;padding:14px;min-height:140px;">
                <div style="font-size:12px;font-weight:800;color:#166534;margin-bottom:8px;">
                    ✏️ 고쳐쓴 글 ✨
                </div>
                <div style="font-size:13px;color:#14532d;line-height:1.7;">
                    <b>주장:</b> {st.session_state.revised_claim}<br><br>
                    <b>이유:</b> {st.session_state.revised_reason}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#f1f5f9;border-radius:14px;padding:14px;min-height:140px;
                        display:flex;align-items:center;justify-content:center;">
                <div style="text-align:center;color:#94a3b8;font-size:13px;">
                    1단계에서 고쳐쓰기를 하지 않았어요.<br>
                    처음 쓴 글로 진행할게요.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 2단계 반론도 보여주기
    if st.session_state.rebuttal:
        st.markdown(f"""
        <div style="background:#f5f3ff;border-left:4px solid #8b5cf6;border-radius:12px;
                    padding:12px 16px;margin-top:10px;font-size:13px;color:#4c1d95;">
            <b>🗣️ 내가 쓴 반론:</b> {st.session_state.rebuttal}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── STEP B: 가장 강한 근거 1개 선택 ──────────────────────────
    st.markdown("### 📌 STEP 2. 가장 강한 근거 1개 선택하기")
    st.markdown("""
    <div style="background:#fff7ed;border-radius:10px;padding:10px 14px;
                margin-bottom:12px;font-size:13px;color:#92400e;">
        💡 여러 근거 중에서 <b>내 주장을 가장 잘 뒷받침하는 근거 1개</b>를 골라봐요.
        왜 그 근거가 가장 강한지도 써봐요!
    </div>
    """, unsafe_allow_html=True)

    all_ev = []
    for a in ARTICLES:
        all_ev.append({"key": f"a_{a['id']}", "text": a['evidence'],
                        "label": f"[{a['source']}] {a['evidence'][:50]}...",
                        "source": a['source'], "url": a['url']})
    for i, item in enumerate(st.session_state.get("search_results", [])):
        memo = st.session_state.get(f"memo_web_{i}", "")
        ev_text = memo or item.get('evidence', '')
        if ev_text:
            all_ev.append({"key": f"w_{i}", "text": ev_text,
                            "label": f"[인터넷] {ev_text[:50]}...",
                            "source": item.get('source_label','인터넷'), "url": item.get('url','')})

    # 라디오 버튼으로 1개만 선택
    ev_labels  = [ev["label"] for ev in all_ev]
    ev_labels_with_none = ["(아직 선택 안 함)"] + ev_labels
    current_key = st.session_state.best_evidence_key
    current_idx = 0
    for i, ev in enumerate(all_ev):
        if ev["key"] == current_key:
            current_idx = i + 1
            break

    selected_idx = st.radio("근거 선택", ev_labels_with_none,
                             index=current_idx, label_visibility="collapsed")

    best_ev = None
    if selected_idx != "(아직 선택 안 함)":
        best_ev = next((ev for ev in all_ev if ev["label"] == selected_idx), None)
        if best_ev:
            st.session_state.best_evidence_key = best_ev["key"]
            st.markdown(f"""
            <div style="background:#fff7ed;border-left:4px solid #f97316;border-radius:10px;
                        padding:12px 14px;margin:8px 0;font-size:14px;color:#7c2d12;font-weight:600;">
                📌 선택한 근거: "{best_ev['text']}"
                <div style="font-size:12px;font-weight:400;margin-top:4px;">출처: {best_ev['source']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("**왜 이 근거가 가장 강하다고 생각했나요?**")
    ev_reason = st.text_area("근거 이유", value=st.session_state.best_evidence_reason,
        placeholder="예) 실제 정부 기관의 공식 통계라 믿을 수 있고, 내 주장을 직접 뒷받침하기 때문이에요.",
        height=70, label_visibility="collapsed", key="input_ev_reason")
    if ev_reason:
        st.session_state.best_evidence_reason = ev_reason

    st.markdown("---")

    # ── STEP C: 최종 발표문 생성 ──────────────────────────────────
    st.markdown("### 🎤 STEP 3. 최종 발표문 완성하기")
    final_claim  = st.session_state.revised_claim or st.session_state.claim
    final_reason = st.session_state.revised_reason or st.session_state.reason

    can_gen = bool(best_ev)
    if st.button("✍️ 최종 발표문 만들기!", disabled=not can_gen, key="btn_speech"):
        _run_speech(final_claim, final_reason, best_ev, all_ev)

    if st.session_state.final_speech:
        _render_final_speech(final_claim, final_reason)


def _run_speech(final_claim, final_reason, best_ev, all_ev):
    rebuttal_txt = st.session_state.rebuttal or ""
    ev_text = best_ev["text"] if best_ev else ""
    ev_src  = best_ev["source"] if best_ev else ""

    sys_p = """초등학교 6학년 토론 선생님입니다.
학생의 주장·이유·근거·반론 대비 내용을 바탕으로 최종 발표문을 써주세요.

[발표문 구조]
1단락: 주장 (1~2문장)
2단락: 이유 + 근거 (2~3문장, 근거 출처 포함)
3단락: 반론 대비 + 결론 (2문장)

[조건]
- 초등학생이 실제로 말할 수 있는 자연스러운 말투
- 전체 350자 이내
- 어려운 말 금지
- 발표문만 출력 (설명 없이)"""

    user_msg = f"""주장: {final_claim}
이유: {final_reason}
핵심 근거: {ev_text} (출처: {ev_src})
내 반론: {rebuttal_txt}"""

    with st.spinner("✍️ 최종 발표문 작성 중..."):
        result = call_gemini_json(sys_p, user_msg)

    st.session_state.final_speech = result if not result.startswith("__") else "오류가 발생했어요. 다시 시도해 주세요."


def _render_final_speech(final_claim, final_reason):
    st.markdown("#### 🎤 나의 최종 발표문")
    st.markdown(f"""
    <div style="background:white;border:2px solid #f97316;border-radius:18px;
                padding:20px;margin-bottom:16px;">
        <div style="font-size:15px;color:#1e293b;line-height:1.9;white-space:pre-wrap;">
            {st.session_state.final_speech}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.code(st.session_state.final_speech, language=None)

    # ── 처음 vs 최종 최종 비교 ──
    st.markdown("#### 📈 나의 성장 기록")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background:#fee2e2;border-radius:14px;padding:14px;">
            <div style="font-size:12px;font-weight:800;color:#991b1b;margin-bottom:6px;">📄 처음 쓴 주장+이유</div>
            <div style="font-size:13px;color:#7f1d1d;line-height:1.6;">
                {st.session_state.claim}<br><br>{st.session_state.reason}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:#dcfce7;border-radius:14px;padding:14px;">
            <div style="font-size:12px;font-weight:800;color:#166534;margin-bottom:6px;">🏆 최종 발표문</div>
            <div style="font-size:13px;color:#14532d;line-height:1.6;">
                {st.session_state.final_speech[:200]}{"..." if len(st.session_state.final_speech)>200 else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#fef9c3;border-radius:16px;padding:18px;text-align:center;
                border:2px solid #fde047;margin-top:12px;">
        <div style="font-size:2rem;">🎉</div>
        <div style="font-size:1.1rem;font-weight:900;color:#854d0e;">토론 준비 완료!</div>
        <div style="font-size:0.85rem;color:#92400e;margin-top:4px;">
            주장 → 고쳐쓰기 → 반론 → 최종 발표문까지 완성했어요!
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 처음부터 다시 하기", key="btn_restart"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ════════════════════════════════════════════════════════════
# 메인
# ════════════════════════════════════════════════════════════
def main():
    init_session()
    render_header()
    render_progress(st.session_state.step)
    if not st.secrets.get("GEMINI_API_KEY", ""):
        render_no_key_warning()
    if   st.session_state.step == 0: step1()
    elif st.session_state.step == 1: step2()
    elif st.session_state.step == 2: step3()
    st.markdown("""
    <div class="info-box">
        💡 <b>주장</b>은 내 생각 &nbsp;·&nbsp;
           <b>이유</b>는 왜 그렇게 생각하는지 &nbsp;·&nbsp;
           <b>근거</b>는 이유를 뒷받침하는 <b>객관적 자료</b>예요!
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


# ══════════════════════════════════════════════════════════════
# 복원: _run_analysis / _run_web_search / _render_analysis_result
# ══════════════════════════════════════════════════════════════

CLAIM_GUIDE = """
[초등 6학년 '주장' 작성 10가지 지침]
1. 찬성 또는 반대 입장을 명확하게 한 가지만 선택해서 쓴다.
2. "~해야 한다 / ~하면 안 된다 / ~이 필요하다" 처럼 주장의 의지가 담긴 표현을 쓴다.
3. 무엇에 대한 주장인지 주어(주제)가 분명하게 드러나야 한다.
4. "좋다 / 나쁘다" 처럼 너무 막연한 표현은 피한다.
5. 사실을 그대로 서술하는 문장은 주장이 아니다.
6. 한 문장 안에 두 가지 주장을 섞지 않는다.
7. 과장되거나 극단적인 표현("절대로 / 무조건 / 100%")은 신뢰를 낮춘다.
8. 토론 주제와 직접 연관된 주장을 써야 한다.
9. 읽는 사람이 동의하거나 반박하고 싶어지는 주장이 좋은 주장이다.
10. 이유와 근거를 떠올렸을 때 뒷받침이 가능한 주장을 선택한다.
"""

REASON_GUIDE = """
[초등 6학년 '이유' 작성 10가지 지침]
1. 주장에 "왜?"라고 물었을 때 답이 되는 문장이어야 한다.
2. "왜냐하면 ~하기 때문이다" 구조로 인과관계를 명확히 한다.
3. 주장을 그대로 반복하면 이유가 아니다.
4. 또 다른 주장처럼 들리는 문장도 이유가 아니다.
5. 구체적인 현상, 원리, 과정을 설명해야 한다.
6. 하나의 이유는 하나의 핵심 내용만 담는다.
7. 감정적인 호소만으로는 약한 이유가 된다.
8. 이유는 1~3가지로 압축하여 명확하게 제시한다.
9. 이유 뒤에 근거가 연결될 수 있는 내용이어야 한다.
10. 읽는 사람이 "그렇구나, 그래서 그 주장을 하는구나"라고 이해할 수 있어야 한다.
"""

EVIDENCE_GUIDE = """
[초등 6학년 '근거' 활용 10가지 지침]
1. 근거는 내 생각이나 느낌이 아닌 객관적인 자료여야 한다.
2. 출처를 반드시 밝혀야 한다.
3. 통계·수치가 포함된 자료는 설득력이 높다.
4. 정부 기관, 연구소, 전문가의 공식 발언이나 보고서를 우선 활용한다.
5. 실제로 일어난 사건이나 사례는 주장을 현실감 있게 뒷받침한다.
6. 근거는 이유를 뒷받침하는 것이어야 한다.
7. 최신 자료일수록 신뢰도가 높다.
8. 한쪽에 유리한 자료만 골라 쓰는 것은 바람직하지 않다.
9. 근거 문장은 짧고 핵심만 담아 인용한다.
10. 근거가 주장·이유와 어떻게 연결되는지 설명해 주면 더 좋다.
"""

SCORE_LABELS = {
    "매우잘함": "🌟 매우 잘함",
    "잘함":    "👍 잘함",
    "노력바람": "💪 노력 바람",
}
SCORE_COLORS = {
    "매우잘함": ("#dcfce7", "#166534"),
    "잘함":    ("#fef9c3", "#854d0e"),
    "노력바람": ("#fee2e2", "#991b1b"),
}


def _run_analysis(claim: str, reason: str):
    system = f"""당신은 초등학교 6학년 학생의 주장하는 글쓰기를 돕는 선생님입니다.
아래 지침을 기준으로 학생의 주장과 이유를 평가하고 구체적인 피드백을 주세요.

{CLAIM_GUIDE}
{REASON_GUIDE}
{EVIDENCE_GUIDE}

[핵심 평가 원칙]
★ 주장-이유 일관성 검사 (최우선):
  - 주장의 입장(찬성/반대)과 이유의 방향이 반드시 같아야 합니다.
  - 불일치하면 reasonScore는 반드시 "노력바람"

[평가 등급]
- 매우잘함: 일관성 OK + 지침 8개 이상
- 잘함: 일관성 OK + 지침 5~7개
- 노력바람: 일관성 불일치 OR 지침 4개 이하

코드블록 없이 JSON만 출력:
{{
  "keywords": ["키워드1","키워드2","키워드3","키워드4"],
  "claimStance": "찬성 또는 반대",
  "reasonStance": "찬성 또는 반대",
  "isConsistent": true,
  "consistencyAlert": "",
  "claimScore": "매우잘함 또는 잘함 또는 노력바람",
  "claimChecked": ["1","2"],
  "claimMissed": ["4"],
  "claimPraise": "칭찬 1~2문장",
  "claimImprove": "개선 제안 (없으면 빈 문자열)",
  "reasonScore": "매우잘함 또는 잘함 또는 노력바람",
  "reasonChecked": ["1","2"],
  "reasonMissed": ["5"],
  "reasonPraise": "칭찬 1~2문장",
  "reasonImprove": "개선 제안 (없으면 빈 문자열)",
  "reasonDeeperQ": "더 깊이 생각하게 만드는 질문 1문장",
  "evidenceNeed": {{
    "stat": "필요한 통계 근거",
    "expert": "필요한 전문가 의견",
    "case": "필요한 실제 사례"
  }},
  "searchQueries": {{
    "stat": "검색어",
    "expert": "검색어",
    "case": "검색어"
  }}
}}"""

    with st.spinner("✏️ AI 선생님이 주장과 이유를 꼼꼼히 읽고 있어요..."):
        result = call_gemini_json(system, f"학생의 주장: {claim}\n학생의 이유: {reason}")

    if result.startswith("__NO_KEY__"): render_no_key_warning(); return
    if result.startswith("__ERROR__"):  st.error(f"AI 오류: {result}"); return

    try:
        parsed = json.loads(re.sub(r"```json|```|`", "", result).strip())
    except Exception:
        parsed = {
            "keywords": ["해상풍력","기후 위기","어민 피해","에너지 전환"],
            "claimStance": "찬성", "reasonStance": "찬성",
            "isConsistent": True, "consistencyAlert": "",
            "claimScore": "잘함", "claimChecked": ["1","2","3"],
            "claimMissed": ["4","7"],
            "claimPraise": "찬성·반대 입장이 잘 드러나 있어요!",
            "claimImprove": "주어를 더 명확하게 넣어봐요.",
            "reasonScore": "잘함", "reasonChecked": ["1","2"],
            "reasonMissed": ["5","6"],
            "reasonPraise": "이유를 쓰려고 노력했어요!",
            "reasonImprove": "왜 그런지 한 단계 더 설명해봐요.",
            "reasonDeeperQ": "구체적으로 어떤 변화가 생길까요?",
            "evidenceNeed": {
                "stat": "해상풍력 탄소감축 수치",
                "expert": "환경부 해상풍력 의견",
                "case": "해상풍력 성공 사례"
            },
            "searchQueries": {
                "stat": "해상풍력 탄소감축 효과 수치",
                "expert": "환경부 해상풍력 전문가 의견",
                "case": "덴마크 해상풍력 성공 사례"
            }
        }

    st.session_state.ai_analysis = parsed
    st.session_state.keywords    = parsed.get("keywords", [])
    kws = parsed.get("keywords", [])
    filtered = [a for a in ARTICLES if any(k in " ".join(a["keywords"]) for k in kws)]
    st.session_state.filtered_articles = filtered if filtered else ARTICLES


def _run_web_search(claim: str, reason: str):
    ana     = st.session_state.ai_analysis or {}
    kw_list = ana.get("keywords", [])
    if not kw_list:
        words = re.findall(r'[가-힣]{2,5}', reason)
        stop  = {"때문에","하기가","위해서","그리고","이유는","있기","없기","이다","이기",
                 "하면","에서","으로","이라","있어","없어","하는","위한","대한","통해"}
        kw_list = [w for w in words if w not in stop][:4]
    kw_str = " ".join(kw_list[:4])

    query = (
        f"{kw_str} 해상풍력 뉴스 기사 2023 2024 2025 "
        f"site:yonhapnews.co.kr OR site:hani.co.kr OR site:ohmynews.com "
        f"OR site:kbs.co.kr OR site:yna.co.kr OR site:chosun.com OR site:joongang.co.kr"
    )
    with st.spinner("🔍 관련 뉴스 기사를 검색하고 있어요..."):
        _, grounding_sources = call_gemini_with_search(query)

    items = []
    domain_map = {
        "yonhapnews": "연합뉴스", "yna.co": "연합뉴스",
        "hani.co": "한겨레", "ohmynews": "오마이뉴스",
        "kbs.co": "KBS", "chosun": "조선일보",
        "joongang": "중앙일보", "donga": "동아일보",
        "khan.co": "경향신문", "mbc.co": "MBC",
        "newsis": "뉴시스", "news1": "뉴스1",
        "ikbc": "KBC", "lghellovision": "LG헬로비전",
    }
    for s in grounding_sources:
        url   = s.get("url", "").strip()
        title = s.get("title", "").strip()
        if not url or not title:
            continue
        source_label = "뉴스"
        for key, name in domain_map.items():
            if key in url:
                source_label = name
                break
        items.append({
            "title": title, "source_label": source_label,
            "url": url, "side": "neutral", "evidence_type": "뉴스기사",
        })

    if not items:
        fallback_sys = f"""초등학교 6학년 토론 수업용 뉴스 기사를 3개 알려주세요.
토론 주제: {TOPIC} / 키워드: {kw_str}
코드블록 없이 JSON 배열만:
[{{"title":"제목","source_label":"언론사, 날짜","url":"","side":"neutral","evidence_type":"뉴스기사"}}]"""
        with st.spinner("📰 기사 목록 가져오는 중..."):
            fb = call_gemini_json(fallback_sys, "")
        try:
            clean = re.sub(r"```json|```|`", "", fb).strip()
            m = re.search(r'\[.*\]', clean, re.DOTALL)
            items = json.loads(m.group() if m else clean)
        except Exception:
            items = []

    st.session_state.search_results = items[:5]
    st.session_state.search_error   = "" if items else "기사를 찾지 못했어요. 다시 시도해봐요."


def _render_analysis_result():
    ana = st.session_state.ai_analysis

    if st.session_state.praise:
        st.markdown(f'<div class="praise-box">{st.session_state.praise}</div>', unsafe_allow_html=True)

    # 일관성 경고
    if not ana.get("isConsistent", True):
        alert     = ana.get("consistencyAlert", "주장과 이유의 방향이 다를 수 있어요.")
        cs_stance = ana.get("claimStance", "")
        rs_stance = ana.get("reasonStance", "")
        st.markdown(f"""
        <div style="background:#fff1f2;border:2px solid #f87171;border-radius:14px;
                    padding:14px 18px;margin-bottom:14px;">
            <div style="font-size:14px;font-weight:900;color:#b91c1c;margin-bottom:8px;">
                ⚠️ 주장과 이유의 방향이 달라요!
            </div>
            <div style="font-size:13px;color:#7f1d1d;line-height:1.8;">
                주장 입장: <b style="color:#1d4ed8;">{cs_stance}</b> &nbsp;↔&nbsp;
                이유 방향: <b style="color:#dc2626;">{rs_stance}</b><br>
                {alert}<br><br>
                <b>💡 고쳐쓰기 단계에서 수정해봐요!</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 📋 주장 · 이유 · 근거 구분 & AI 피드백")

    def score_badge_html(score):
        label = SCORE_LABELS.get(score, score)
        bg, fg = SCORE_COLORS.get(score, ("#f1f5f9","#334155"))
        return f'<span style="background:{bg};color:{fg};border-radius:99px;padding:4px 14px;font-size:13px;font-weight:800;">{label}</span>'

    def guide_chips(checked, missed):
        html = '<div style="display:flex;flex-wrap:wrap;gap:4px;margin:6px 0;">'
        for n in checked:
            html += f'<span style="background:#dcfce7;color:#166534;border-radius:6px;padding:2px 8px;font-size:11px;font-weight:700;">✅ 지침{n}</span>'
        for n in missed:
            html += f'<span style="background:#fee2e2;color:#991b1b;border-radius:6px;padding:2px 8px;font-size:11px;font-weight:700;">❌ 지침{n}</span>'
        html += '</div>'
        return html

    # 주장 카드
    cs  = ana.get("claimScore","잘함")
    claim_fb = f"""{score_badge_html(cs)}
{guide_chips(ana.get("claimChecked",[]), ana.get("claimMissed",[]))}
<div style="font-size:13px;line-height:1.8;margin-top:4px;">
  <b>✅ 잘한 점:</b> {ana.get("claimPraise","")}
  {"<br><b>💡 이렇게 고쳐봐요:</b> " + ana.get("claimImprove","") if ana.get("claimImprove") else ""}
</div>"""
    render_arg_card("💬 주장", "arg-claim", "💬", st.session_state.claim, claim_fb, "fb-claim")

    # 이유 카드
    rs  = ana.get("reasonScore","잘함")
    reason_fb = f"""{score_badge_html(rs)}
{guide_chips(ana.get("reasonChecked",[]), ana.get("reasonMissed",[]))}
<div style="font-size:13px;line-height:1.8;margin-top:4px;">
  <b>✅ 잘한 점:</b> {ana.get("reasonPraise","")}
  {"<br><b>💡 이렇게 고쳐봐요:</b> " + ana.get("reasonImprove","") if ana.get("reasonImprove") else ""}
  {"<br><b>🤔 더 생각해봐요:</b> " + ana.get("reasonDeeperQ","") if ana.get("reasonDeeperQ") else ""}
</div>"""
    render_arg_card("🌿 이유", "arg-reason", "🌿", st.session_state.reason, reason_fb, "fb-reason")

    # 근거 힌트 카드
    en = ana.get("evidenceNeed", {})
    st.markdown(f"""
    <div class="arg-evidence">
        <div class="arg-label">📌 근거 (아직 찾는 중!)</div>
        <div class="arg-text" style="color:#c2410c;margin-bottom:10px;">
            근거는 내 생각이 아닌 <b>객관적인 자료</b>예요!
        </div>
        <div style="display:flex;flex-direction:column;gap:6px;">
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

    # 키워드
    st.markdown("#### 🏷️ AI가 찾은 핵심 키워드")
    chips = "".join([f'<span class="chip">{k}</span>' for k in st.session_state.keywords])
    st.markdown(f'<div class="chip-wrap">{chips}</div>', unsafe_allow_html=True)

    # 탭: 기사 / 검색
    tab1, tab2 = st.tabs(["📰 제공 기사 자료", "🌐 인터넷 검색 자료"])
    with tab1:
        for a in st.session_state.get("filtered_articles", ARTICLES):
            _render_news_card(a)
    with tab2:
        err     = st.session_state.get("search_error", "")
        results = st.session_state.get("search_results", [])
        if err and not results:
            st.warning(f"⚠️ {err}")
        elif not results:
            st.info("🔍 '근거 찾기' 버튼을 눌러 관련 기사를 검색해봐요!")
        else:
            st.markdown(f"""
            <div style="background:#f0fdf4;border-radius:12px;padding:10px 14px;
                        margin-bottom:12px;font-size:13px;color:#166534;font-weight:600;">
                📰 <b>{len(results)}개</b> 기사를 찾았어요! 직접 읽고 근거 문장을 메모해봐요. ✍️
            </div>
            """, unsafe_allow_html=True)
            for i, item in enumerate(results):
                _render_search_card(item, i)

    _render_selected_summary()


def _render_selected_summary():
    sel_int = [s for s in st.session_state.selected_articles if isinstance(s, int)]
    sel_str = [s for s in st.session_state.selected_articles if isinstance(s, str)]
    if not sel_int and not sel_str:
        # 선택 없어도 고쳐쓰기 버튼 표시
        st.markdown("---")
        if st.session_state.get("ai_analysis"):
            st.markdown("""
            <div style="background:linear-gradient(135deg,#fef9c3,#fde68a);border-radius:14px;
                        padding:14px 18px;margin-bottom:10px;font-size:14px;color:#78350f;line-height:1.7;">
                ✅ AI 피드백을 확인했나요?
                이제 피드백을 바탕으로 <b>주장과 이유를 고쳐써봐요!</b>
            </div>
            """, unsafe_allow_html=True)
            if st.button("✏️ 고쳐쓰기 시작하기 →", key="btn_goto_rewrite", use_container_width=True):
                st.session_state.substep = "rewrite"
                st.rerun()
        return

    st.markdown("#### 📌 내가 선택한 근거 모음")
    citation_lines = []

    for sid in sel_int:
        art = next((x for x in ARTICLES if x["id"] == sid), None)
        if art:
            st.markdown(f"""
            <div style="background:#fff7ed;border-left:4px solid #f97316;border-radius:10px;
                        padding:10px 14px;margin-bottom:6px;">
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
            memo = st.session_state.get(f"memo_web_{idx}","")
            ev_text = memo or item.get("evidence","기사를 직접 읽고 근거를 찾아봐요.")
            link = f'<a href="{url}" target="_blank" style="font-size:12px;color:#0284c7;">🔗 출처 보기</a>' if url and url != "#" else ""
            st.markdown(f"""
            <div style="background:#f0fdf4;border-left:4px solid #22c55e;border-radius:10px;
                        padding:10px 14px;margin-bottom:6px;">
                <div style="font-size:12px;color:#15803d;font-weight:700;">{item.get('source_label','')} · 인터넷</div>
                <div style="font-size:14px;color:#14532d;font-weight:600;">"{ev_text}"</div>
                {link}
            </div>
            """, unsafe_allow_html=True)
            citation_lines.append(f"[출처] {item.get('source_label','인터넷 자료')}\n제목: {item.get('title','')}\nURL: {url}")

    if citation_lines:
        st.markdown("#### 📋 출처 자동 정리")
        ct = "\n\n".join(citation_lines)
        st.code(ct, language=None)

    st.markdown("---")
    st.markdown("""
    <div style="background:linear-gradient(135deg,#fef9c3,#fde68a);border-radius:14px;
                padding:14px 18px;margin-bottom:10px;font-size:14px;color:#78350f;line-height:1.7;">
        ✅ AI 피드백과 근거 자료를 확인했나요?
        이제 피드백을 바탕으로 <b>주장과 이유를 고쳐써봐요!</b>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✏️ 고쳐쓰기 시작하기 →", key="btn_goto_rewrite_sel", use_container_width=True):
        st.session_state.substep = "rewrite"
        st.rerun()
