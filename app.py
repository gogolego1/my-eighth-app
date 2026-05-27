import streamlit as st
import google.generativeai as genai
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

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 전체 배경 */
.stApp {
    background: linear-gradient(180deg, #e0f7fa 0%, #f0f9ff 60%, #f8fafc 100%);
}

/* 헤더 */
.heal-header {
    background: linear-gradient(135deg, #0284c7, #0ea5e9, #06b6d4);
    border-radius: 0 0 28px 28px;
    padding: 28px 24px 36px;
    text-align: center;
    margin: -1rem -1rem 1.5rem -1rem;
    box-shadow: 0 4px 20px rgba(14,165,233,0.2);
}
.heal-header h1 {
    color: white;
    font-size: 2rem;
    font-weight: 900;
    margin: 0.3rem 0 0.2rem;
    letter-spacing: -0.5px;
}
.heal-header p {
    color: #bae6fd;
    font-size: 0.85rem;
    margin: 0;
}
.heal-icons { font-size: 2.2rem; margin-bottom: 4px; }

/* 진행 단계 */
.step-bar {
    display: flex;
    gap: 8px;
    margin: 0 0 1.2rem 0;
}
.step-item {
    flex: 1;
    text-align: center;
    font-size: 11px;
    font-weight: 700;
    padding: 6px 4px 4px;
    border-radius: 10px;
    border: 2px solid transparent;
}
.step-active {
    background: #0ea5e9;
    color: white;
    border-color: #0284c7;
}
.step-done {
    background: #bbf7d0;
    color: #166534;
    border-color: #86efac;
}
.step-todo {
    background: #f1f5f9;
    color: #94a3b8;
    border-color: #e2e8f0;
}

/* 카드 */
.card {
    background: white;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 2px 16px rgba(14,165,233,0.07);
}

/* 주장·이유·근거 구분 박스 */
.arg-claim {
    background: #eff6ff;
    border-left: 5px solid #3b82f6;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
}
.arg-reason {
    background: #f0fdf4;
    border-left: 5px solid #22c55e;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
}
.arg-evidence {
    background: #fff7ed;
    border-left: 5px solid #f97316;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
}
.arg-label {
    font-size: 11px;
    font-weight: 800;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.arg-text {
    font-size: 15px;
    line-height: 1.6;
}

/* 키워드 칩 */
.chip-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
.chip {
    display: inline-block;
    background: #e0f2fe;
    color: #0369a1;
    border-radius: 99px;
    padding: 4px 14px;
    font-size: 13px;
    font-weight: 700;
}
.chip:nth-child(2n) { background: #dcfce7; color: #166534; }
.chip:nth-child(3n) { background: #fef9c3; color: #854d0e; }
.chip:nth-child(4n) { background: #ede9fe; color: #5b21b6; }

/* 기사 카드 */
.news-card {
    background: white;
    border: 1.5px solid #e2e8f0;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 10px;
}
.news-source {
    font-size: 12px;
    color: #0ea5e9;
    font-weight: 700;
    margin-bottom: 4px;
}
.news-title {
    font-size: 15px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 6px;
    line-height: 1.4;
}
.news-summary {
    font-size: 13px;
    color: #475569;
    line-height: 1.6;
    margin-bottom: 10px;
}
.evidence-box {
    background: #fff7ed;
    border-left: 4px solid #f97316;
    border-radius: 8px;
    padding: 10px 14px;
    margin-top: 8px;
}
.evidence-label {
    font-size: 11px;
    color: #ea580c;
    font-weight: 800;
    margin-bottom: 4px;
}
.evidence-text {
    font-size: 14px;
    color: #7c2d12;
    font-weight: 600;
    line-height: 1.5;
    font-style: italic;
}
.evidence-why {
    font-size: 12px;
    color: #9a3412;
    margin-top: 5px;
}

/* 칭찬 박스 */
.praise-box {
    background: #fef9c3;
    border: 2px solid #fde047;
    border-radius: 14px;
    padding: 12px 16px;
    text-align: center;
    font-size: 16px;
    font-weight: 800;
    color: #854d0e;
    margin-bottom: 14px;
}

/* 출처 박스 */
.citation-box {
    background: #f0fdf4;
    border: 1.5px solid #86efac;
    border-radius: 14px;
    padding: 14px 16px;
    margin-top: 10px;
    font-size: 12px;
    color: #14532d;
    line-height: 1.9;
    white-space: pre-wrap;
    font-family: monospace;
}

/* 안내 박스 */
.info-box {
    background: #e0f2fe;
    border-radius: 14px;
    padding: 12px 16px;
    font-size: 13px;
    color: #0369a1;
    line-height: 1.7;
    margin-top: 16px;
}

/* 버튼 공통 */
.stButton > button {
    border-radius: 14px !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    padding: 12px 0 !important;
    width: 100% !important;
    border: none !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* 텍스트 에어리어 */
.stTextArea textarea {
    border-radius: 12px !important;
    font-size: 15px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)


# ── Gemini 설정 ───────────────────────────────────────────────
def get_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")


def call_gemini(system_prompt: str, user_message: str) -> str:
    model = get_gemini_client()
    if model is None:
        return "__NO_KEY__"
    try:
        response = model.generate_content(
            f"{system_prompt}\n\n{user_message}",
            generation_config={"max_output_tokens": 1000, "temperature": 0.7},
        )
        return response.text
    except Exception as e:
        return f"__ERROR__:{e}"


# ── 샘플 기사 데이터 ──────────────────────────────────────────
ARTICLES = [
    {
        "id": 1,
        "title": "완도 금일도 주민, 해상풍력 반대… '해상풍력 철회하라'",
        "summary": (
            "한국남동발전이 완도 금일도 해상 7km 지점에 15MW 발전기 40기(600MW) 설치를 추진하자, "
            "어선 100여 척이 앞바다에 멈춰 서며 반대 시위를 벌였습니다. "
            "주민들은 해조류 양식장 피해와 생태계 파괴, 보상 기준 부재를 우려하고 있습니다."
        ),
        "source": "LG헬로비전",
        "date": "2024.09.03",
        "url": "https://news.lghellovision.net/news/articleView.html?idxno=480155",
        "evidence": "금일도 어민들은 어선 100여 척을 동원해 해상 시위를 벌이며 '보상 기준도, 책임지는 사람도 없다'고 주장했습니다.",
        "evidence_type": "주민 증언",
        "side": "반대",
        "keywords": ["어민 반대", "생존권", "보상 부재", "생태계 피해"],
    },
    {
        "id": 2,
        "title": "해상풍력, 어업인 생존권 충돌… '해풍법' 주민 수용성 가능할까",
        "summary": (
            "신안 해상풍력 8.2GW 조성구역은 연안 어선의 조업공간 91.3%와 겹칩니다. "
            "그 면적은 서울시의 3배에 달합니다. '해상풍력 특별법(해풍법)'은 인허가 기간을 "
            "8개월 단축하지만 어업인 보상 규정은 없어 국회 토론회에서 강하게 비판받았습니다."
        ),
        "source": "오마이뉴스",
        "date": "2025.05.16",
        "url": "https://www.ohmynews.com/NWS_Web/View/at_pg.aspx?CNTN_CD=A0003131395",
        "evidence": "신안 해상풍력 조성구역은 연안 어선 조업공간의 91.3%와 중복되며, 그 면적은 서울시의 3배에 달합니다.",
        "evidence_type": "통계",
        "side": "반대",
        "keywords": ["조업 공간", "91.3% 중복", "보상 규정 없음", "해풍법"],
    },
    {
        "id": 3,
        "title": "해상 경계 분쟁, '어장'에서 '해상 풍력'으로 확대",
        "summary": (
            "완도-제주 해상경계 분쟁은 1996년부터 지금까지 해결되지 않고 있습니다. "
            "바다는 이제 어업을 넘어 해상풍력·블루카본·해양관광이 집중되는 미래 자원 공간으로, "
            "해역 경계가 불명확하면 인허가 지연과 법적 불확실성이 생겨 지역 경제에 큰 손실이 발생합니다."
        ),
        "source": "KBC",
        "date": "2025.03.16",
        "url": "https://news.ikbc.co.kr/저녁뉴스(사회)/article/view/kbc202503160032",
        "evidence": "해상경계가 불명확하면 해상풍력 인허가가 지연되고 법적 분쟁이 발생해 지역 경제 기회가 손실됩니다.",
        "evidence_type": "전문가 분석",
        "side": "조건부",
        "keywords": ["해상경계 분쟁", "인허가 지연", "지역 경제", "해양 자원"],
    },
    {
        "id": 4,
        "title": "하나은행·한국남동발전, 완도금일해상풍력 업무협약 체결",
        "summary": (
            "하나은행이 한국남동발전과 600MW 규모 완도금일해상풍력 발전단지 조성을 위한 MOU를 맺었습니다. "
            "이 사업은 국내 최대 규모로, 생산 전력은 국가 AI 데이터센터와 "
            "호남권 첨단전략산업 전력 인프라로 활용될 예정입니다."
        ),
        "source": "조선비즈",
        "date": "2026.02.27",
        "url": "https://biz.chosun.com/stock/finance/2026/02/27/Q35WW4LYFNE6HAGNSMB4X6S2L4/",
        "evidence": "하나은행과 남동발전이 600MW 완도금일해상풍력 MOU를 체결했고, 연내 착공이 가능한 단계로 평가받고 있습니다.",
        "evidence_type": "공식 발표",
        "side": "찬성",
        "keywords": ["MOU 체결", "600MW", "AI 데이터센터", "착공 임박"],
    },
]

PRAISE_LIST = [
    "👏 정말 훌륭한 이유예요!",
    "⭐ 생각을 아주 잘 정리했어요!",
    "🎉 논리적인 주장이에요!",
    "💪 멋진 근거를 찾았어요!",
    "🌟 훌륭한 토론 준비예요!",
]

TOPIC = "기후 위기를 막기 위해 해상풍력 발전단지 건설은 반드시 필요하다"


# ── 세션 초기화 ───────────────────────────────────────────────
def init_session():
    defaults = {
        "step": 0,
        "claim": "",
        "reason": "",
        "keywords": [],
        "ai_analysis": None,
        "selected_articles": [],
        "praise": "",
        "rebuttal": "",
        "ai_rebuttal": None,
        "final_speech": "",
        "selected_evidence": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── 헤더 ─────────────────────────────────────────────────────
def render_header():
    st.markdown("""
    <div class="heal-header">
        <div class="heal-icons">🌿🌊🐠</div>
        <h1>H.E.A.L 프로젝트</h1>
        <p>해상풍력 발전단지 건설 · AI 토론 도우미</p>
    </div>
    """, unsafe_allow_html=True)


# ── 진행 바 ───────────────────────────────────────────────────
def render_progress(current_step: int):
    steps = ["1단계: 주장 펼치기", "2단계: 반론 펼치기", "3단계: 주장 다지기"]
    html = '<div class="step-bar">'
    for i, s in enumerate(steps):
        if i < current_step:
            cls = "step-done"
            prefix = "✅ "
        elif i == current_step:
            cls = "step-active"
            prefix = "▶ "
        else:
            cls = "step-todo"
            prefix = ""
        html += f'<div class="step-item {cls}">{prefix}{s}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ── 주장·이유·근거 카드 ────────────────────────────────────────
def render_arg_card(label, color_class, icon, text, placeholder="아직 입력하지 않았어요"):
    display = text if text else f'<span style="color:#94a3b8">{placeholder}</span>'
    st.markdown(f"""
    <div class="{color_class}">
        <div class="arg-label">{icon} {label}</div>
        <div class="arg-text">{display}</div>
    </div>
    """, unsafe_allow_html=True)


# ── API 키 없음 경고 ──────────────────────────────────────────
def render_no_key_warning():
    st.warning(
        "⚠️ **Gemini API 키가 설정되지 않았어요.**\n\n"
        "Streamlit 앱의 **Settings → Secrets**에 아래 내용을 추가해 주세요:\n\n"
        "```toml\nGEMINI_API_KEY = \"여기에_API_키_입력\"\n```"
    )


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
    claim = st.text_area(
        "주장",
        value=st.session_state.claim,
        placeholder='예) "해상풍력 발전단지 건설은 기후 위기 해결을 위해 반드시 필요하다."',
        height=80,
        label_visibility="collapsed",
        key="input_claim",
    )

    st.markdown("**🌿 그렇게 생각하는 이유**")
    reason = st.text_area(
        "이유",
        value=st.session_state.reason,
        placeholder='예) "석탄·가스 발전을 줄이고 재생에너지를 늘려야 탄소 배출을 줄일 수 있기 때문이다."',
        height=100,
        label_visibility="collapsed",
        key="input_reason",
    )

    can_analyze = bool(claim.strip() and reason.strip())

    if st.button("🔍 근거 찾기!", disabled=not can_analyze, key="btn_analyze"):
        st.session_state.claim = claim
        st.session_state.reason = reason
        _run_analysis(claim, reason)
        import random
        st.session_state.praise = random.choice(PRAISE_LIST)

    # 결과 표시
    if st.session_state.ai_analysis:
        _render_analysis_result()


def _run_analysis(claim: str, reason: str):
    system = """당신은 초등학교 6학년 학생을 돕는 친절한 선생님입니다.
학생의 주장과 이유를 분석하여 반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요.
{
  "keywords": ["키워드1", "키워드2", "키워드3", "키워드4"],
  "claimFeedback": "주장에 대한 칭찬 한 문장 (초등학생 눈높이)",
  "reasonFeedback": "이유에 대한 칭찬 한 문장 (초등학생 눈높이)",
  "evidenceHint": "어떤 근거를 찾으면 좋을지 안내 두 문장 (쉬운 말)"
}
키워드는 이유 문장에서 핵심 단어 4개만 추출하세요."""

    with st.spinner("🔍 AI가 분석 중이에요..."):
        result = call_gemini(system, f"주장: {claim}\n이유: {reason}")

    if result.startswith("__NO_KEY__"):
        render_no_key_warning()
        return
    if result.startswith("__ERROR__"):
        st.error(f"AI 오류: {result}")
        return

    try:
        clean = re.sub(r"```json|```", "", result).strip()
        parsed = json.loads(clean)
    except Exception:
        parsed = {
            "keywords": ["해상풍력", "기후 위기", "어민 피해", "에너지 전환"],
            "claimFeedback": "좋은 주장이에요!",
            "reasonFeedback": "이유를 잘 설명했어요!",
            "evidenceHint": "전문 기관 자료에서 통계와 사실을 찾아보세요.",
        }

    st.session_state.ai_analysis = parsed
    st.session_state.keywords = parsed.get("keywords", [])

    # 키워드 기반 기사 필터링
    kws = parsed.get("keywords", [])
    filtered = [
        a for a in ARTICLES
        if any(k in " ".join(a["keywords"]) for k in kws)
    ]
    st.session_state.filtered_articles = filtered if filtered else ARTICLES


def _render_analysis_result():
    ana = st.session_state.ai_analysis

    if st.session_state.praise:
        st.markdown(f'<div class="praise-box">{st.session_state.praise}</div>', unsafe_allow_html=True)

    # 주장·이유·근거 구분 카드
    st.markdown("#### 📋 주장 · 이유 · 근거 구분")
    render_arg_card("💬 주장", "arg-claim", "💬", st.session_state.claim)
    render_arg_card("🌿 이유", "arg-reason", "🌿", st.session_state.reason)
    st.markdown(f"""
    <div class="arg-evidence">
        <div class="arg-label">📌 근거 (아직 찾는 중!)</div>
        <div class="arg-text" style="color:#c2410c;font-size:13px;">
            💡 {ana.get('evidenceHint', '전문 자료에서 사실과 수치를 찾아보세요.')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 키워드
    st.markdown("#### 🏷️ AI가 찾은 핵심 키워드")
    chips = "".join([f'<span class="chip">{k}</span>' for k in st.session_state.keywords])
    st.markdown(f'<div class="chip-wrap">{chips}</div>', unsafe_allow_html=True)

    # 기사 카드
    st.markdown("#### 📰 관련 기사 · 자료")
    articles = getattr(st.session_state, "filtered_articles", ARTICLES) if hasattr(st.session_state, "filtered_articles") else ARTICLES
    # session_state에 filtered_articles 저장 확인
    articles = st.session_state.get("filtered_articles", ARTICLES)

    for a in articles:
        _render_news_card(a)

    # 선택된 근거 요약
    sel = st.session_state.selected_articles
    if sel:
        st.markdown("#### 📌 내가 선택한 근거")
        st.markdown('<div class="arg-evidence">', unsafe_allow_html=True)
        for sid in sel:
            art = next((x for x in ARTICLES if x["id"] == sid), None)
            if art:
                st.markdown(f"""
                <div style="margin-bottom:6px;font-size:14px;color:#7c2d12;font-weight:600;">
                    • "{art['evidence']}"
                    <span style="font-weight:400;color:#9a3412;"> — {art['source']}</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 출처 정리
        st.markdown("#### 📋 출처 자동 정리")
        citation_lines = []
        for sid in sel:
            art = next((x for x in ARTICLES if x["id"] == sid), None)
            if art:
                citation_lines.append(
                    f"[출처] {art['source']}, {art['date']}\n"
                    f"참고 자료: {art['title']}\n"
                    f"주소: {art['url']}"
                )
        citation_text = "\n\n".join(citation_lines)
        st.markdown(f'<div class="citation-box">{citation_text}</div>', unsafe_allow_html=True)
        st.code(citation_text, language=None)

        if st.button("➡️ 2단계로 가기!", key="btn_to_step2"):
            st.session_state.step = 1
            st.rerun()


def _render_news_card(article: dict):
    sid = article["id"]
    is_selected = sid in st.session_state.selected_articles
    border_style = "border: 2px solid #0ea5e9;" if is_selected else "border: 1.5px solid #e2e8f0;"
    side_badge = {"찬성": "🟢 찬성 측 근거", "반대": "🔴 반대 측 근거", "조건부": "🟡 조건부 근거"}.get(article["side"], "")

    st.markdown(f"""
    <div class="news-card" style="{border_style}">
        <div class="news-source">📰 {article['source']} · {article['date']} &nbsp; <span style="background:#f1f5f9;padding:2px 8px;border-radius:99px;font-size:11px;">{side_badge}</span></div>
        <div class="news-title">{article['title']}</div>
        <div class="news-summary">{article['summary']}</div>
        <div class="evidence-box">
            <div class="evidence-label">✅ 근거로 쓸 수 있는 문장</div>
            <div class="evidence-text">"{article['evidence']}"</div>
            <div class="evidence-why">💡 이 문장은 <b>{article['source']}</b>의 <b>{article['evidence_type']}</b>이기 때문에 믿을 수 있는 근거예요!</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    btn_label = "✅ 선택됨!" if is_selected else "📌 근거로 사용하기"
    if st.button(btn_label, key=f"sel_art_{sid}"):
        if is_selected:
            st.session_state.selected_articles.remove(sid)
        else:
            st.session_state.selected_articles.append(sid)
        st.rerun()


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

    # 상대 주장 표시
    is_pro = "필요" in st.session_state.claim or "건설" in st.session_state.claim or "찬성" in st.session_state.claim
    opposite = (
        "해상풍력 발전단지 건설은 어민의 생존권과 해양 생태계를 파괴하므로 중단해야 한다."
        if is_pro else
        "기후 위기를 막으려면 해상풍력 발전단지 건설을 반드시 추진해야 한다."
    )

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
    system = """당신은 초등학교 6학년 토론 선생님입니다.
반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요.
{
  "question": "상대방이 왜 그렇게 생각했을지 추측하는 질문 (쉬운 말, 1문장)",
  "rebuttalHint": "어떻게 반론하면 좋을지 힌트 (2문장, 쉬운 말)",
  "strongerPoint": "내 주장을 더 강하게 만들 수 있는 방법 (1문장)"
}"""

    with st.spinner("🤔 AI가 반론 전략을 분석 중이에요..."):
        result = call_gemini(
            system,
            f"상대방 주장: {opposite}\n내 주장: {st.session_state.claim}\n내 이유: {st.session_state.reason}",
        )

    if result.startswith("__NO_KEY__"):
        render_no_key_warning()
        return

    try:
        clean = re.sub(r"```json|```", "", result).strip()
        parsed = json.loads(clean)
    except Exception:
        parsed = {
            "question": "상대방은 왜 그런 주장을 했을까요? 어떤 걱정이 있었을까요?",
            "rebuttalHint": "상대방 주장의 약점을 찾아봐요. 우리 편 기사에서 반론 근거를 찾을 수 있어요.",
            "strongerPoint": "구체적인 통계나 전문가 의견을 넣으면 더 강한 주장이 돼요.",
        }
    st.session_state.ai_rebuttal = parsed


def _render_rebuttal_result():
    ana = st.session_state.ai_rebuttal

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background:#eff6ff;border-radius:14px;padding:14px;border:1.5px solid #bae6fd;">
            <div style="font-size:12px;font-weight:800;color:#1d4ed8;margin-bottom:6px;">🤔 생각해볼 질문</div>
            <div style="font-size:14px;color:#1e40af;line-height:1.6;">{ana['question']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:#f0fdf4;border-radius:14px;padding:14px;border:1.5px solid #86efac;">
            <div style="font-size:12px;font-weight:800;color:#166534;margin-bottom:6px;">💡 반론 힌트</div>
            <div style="font-size:14px;color:#14532d;line-height:1.6;">{ana['rebuttalHint']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#fef9c3;border-radius:14px;padding:12px 16px;border:1.5px solid #fde047;margin-top:10px;">
        <div style="font-size:12px;font-weight:800;color:#854d0e;margin-bottom:4px;">⚡ 내 주장 강화 포인트</div>
        <div style="font-size:14px;color:#78350f;line-height:1.6;">{ana['strongerPoint']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**✍️ 내가 쓸 반론**")
    rebuttal = st.text_area(
        "반론",
        value=st.session_state.rebuttal,
        placeholder="반론을 직접 써봐요!",
        height=100,
        label_visibility="collapsed",
        key="input_rebuttal",
    )
    st.session_state.rebuttal = rebuttal

    st.markdown("#### 📰 반론 근거 자료")
    for a in ARTICLES:
        _render_news_card(a)

    if st.button("➡️ 3단계로 가기!", key="btn_to_step3"):
        st.session_state.step = 2
        st.rerun()


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

    render_arg_card("💬 내 최종 주장", "arg-claim", "💬", st.session_state.claim)
    render_arg_card("🌿 이유", "arg-reason", "🌿", st.session_state.reason)

    st.markdown("#### 📌 가장 강한 근거를 골라봐요! (여러 개 선택 가능)")
    for a in ARTICLES:
        checked = a["id"] in st.session_state.selected_evidence
        label = f"{'✅' if checked else '⬜'} [{a['source']}] \"{a['evidence'][:50]}...\""
        if st.checkbox(label, value=checked, key=f"ev_{a['id']}"):
            if a["id"] not in st.session_state.selected_evidence:
                st.session_state.selected_evidence.append(a["id"])
        else:
            if a["id"] in st.session_state.selected_evidence:
                st.session_state.selected_evidence.remove(a["id"])

    can_gen = len(st.session_state.selected_evidence) > 0
    if st.button("✍️ 최종 발표문 만들기!", disabled=not can_gen, key="btn_speech"):
        _run_speech()

    if st.session_state.final_speech:
        _render_final_speech()


def _run_speech():
    evidence_texts = []
    for eid in st.session_state.selected_evidence:
        art = next((x for x in ARTICLES if x["id"] == eid), None)
        if art:
            evidence_texts.append(f"- {art['evidence']} (출처: {art['source']})")

    system = """당신은 초등학교 6학년 토론 선생님입니다.
학생의 주장, 이유, 근거를 바탕으로 발표문을 작성해주세요.
- 초등학생이 실제로 말할 수 있는 자연스러운 문체
- 3단락 구성: 주장 → 이유+근거 → 결론
- 각 단락 2~3문장, 전체 250자 이내
- 어려운 말 사용 금지
- 친근하고 당당한 말투"""

    with st.spinner("✍️ AI가 발표문을 작성 중이에요..."):
        result = call_gemini(
            system,
            f"주장: {st.session_state.claim}\n이유: {st.session_state.reason}\n근거:\n" + "\n".join(evidence_texts),
        )

    if result.startswith("__NO_KEY__"):
        render_no_key_warning()
        return

    st.session_state.final_speech = result if not result.startswith("__ERROR__") else "발표문 생성 중 오류가 발생했어요. 다시 시도해 주세요."


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
        <div style="font-size:1.1rem;font-weight:900;color:#854d0e;margin:4px 0;">토론 준비 완료!</div>
        <div style="font-size:0.85rem;color:#92400e;">주장, 이유, 근거를 모두 갖춘 훌륭한 토론자예요!</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 처음부터 다시 하기", key="btn_restart"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ════════════════════════════════════════════════════════════
# 메인 실행
# ════════════════════════════════════════════════════════════
def main():
    init_session()
    render_header()
    render_progress(st.session_state.step)

    # API 키 확인
    if not st.secrets.get("GEMINI_API_KEY", ""):
        render_no_key_warning()

    # 단계별 렌더링
    if st.session_state.step == 0:
        step1()
    elif st.session_state.step == 1:
        step2()
    elif st.session_state.step == 2:
        step3()

    # 안내 박스
    st.markdown("""
    <div class="info-box">
        💡 <b>주장</b>은 내 생각 · <b>이유</b>는 왜 그렇게 생각하는지 · <b>근거</b>는 이유를 뒷받침하는 객관적 자료예요!
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
