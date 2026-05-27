import streamlit as st
import anthropic
from datetime import datetime

# ── 페이지 설정 ──────────────────────────────────────────
st.set_page_config(
    page_title="H.E.A.L. 탐구 질문 만들기",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 영역 데이터 ──────────────────────────────────────────
AREAS = {
    "H": {
        "emoji": "🌸",
        "num": "1영역",
        "title": "청산에 살어리랏다",
        "season": "봄(春) · 나에게 묻다",
        "goal": "생태 감수성",
        "stage": "H단계 1차시",
        "theme": "나와 자연의 관계",
        "color": "#2E75B6",
        "bg": "#DEEAF1",
        "poem": (
            "청산에 살어리랏다 청산에 살어리랏다\n"
            "머루랑 다래랑 먹고 청산에 살어리랏다\n"
            "얄리얄리 얄랑성 얄라리 얄라"
        ),
        "starter": (
            "안녕! 나는 완도에 사는 6학년이야.\n"
            "방금 어부사시사 춘사를 읽었어.\n"
            "\"청산에 살어리랏다\"라는 구절이 인상적이었는데,\n"
            "윤선도가 자연을 왜 그렇게 좋아했는지 아직 잘 모르겠어.\n"
            "내가 자연과 나의 관계에 대해 스스로 생각할 수 있도록\n"
            "답을 알려주지 말고, 나에게 질문만 던져줘.\n"
            "준비됐어? 시작할게."
        ),
        "system": (
            "너는 완도 초등학교 6학년 학생의 생태 탐구를 돕는 AI야.\n"
            "학생이 방금 어부사시사 춘사(봄)를 읽었어.\n\n"
            "이 대화의 목표: 학생이 자연과 나의 관계를 스스로 발견하여 생태 감수성을 기른다.\n\n"
            "규칙:\n"
            "- 절대 직접적인 답을 알려주지 마. 학생이 스스로 생각하도록 질문만 해.\n"
            "- 한 번에 질문 1~2개만. 짧고 열린 질문으로.\n"
            "- 완도 바다, 갯벌, 잘피 숲, 어부 등 완도의 실제 자연 맥락을 활용해.\n"
            "- 학생의 일상 경험과 어부사시사를 연결하도록 유도해.\n"
            "- 따뜻하고 친근한 말투로, '~야', '~어?' 형태로 편하게 말해줘.\n"
            "- 대화가 5~6번 오가면 자연스럽게 마무리하며:\n"
            "  '이 대화에서 가장 궁금해진 게 뭐야? 그걸 탐구 질문으로 만들어봐.' 라고 안내해줘."
        ),
        "steps": [
            ("1", "춘사 한 소절 소리 내어 읽기", "모르는 단어가 있어도 괜찮아요"),
            ("2", "아래 시작 문장을 복사해서 채팅에 입력하기", "그대로 붙여넣고 전송!"),
            ("3", "AI 질문에 내 생각으로 솔직하게 대답하기", "맞고 틀리고가 없어요"),
            ("4", "대화를 마치고 탐구 질문 1개 직접 완성하기", "가장 궁금한 것을 골라요"),
        ],
        "qtypes": ["단순 질문", "탐구 질문", "연결 질문", "확장 질문"],
        "example": "예) 400년 전 완도 바다와 지금 바다는 왜 다를까?",
    },
    "E": {
        "emoji": "☀️",
        "num": "2영역",
        "title": "지국총 어사와",
        "season": "여름(夏) · 함께 듣다",
        "goal": "공동체 의식",
        "stage": "H단계 1차시",
        "theme": "나와 공동체의 관계",
        "color": "#375623",
        "bg": "#E2EFDA",
        "poem": (
            "지국총 지국총 어사와\n"
            "닻 들어라 닻 들어라\n"
            "어부의 노 소리에 우리도 함께 젓는다\n"
            "얄리얄리 얄랑성 얄라리 얄라"
        ),
        "starter": (
            "안녕! 나는 완도에 사는 6학년이야.\n"
            "방금 어부사시사 하사를 읽었어.\n"
            "어부들이 함께 '지국총'이라고 외치며 노를 젓는 장면이 인상적이었어.\n"
            "우리 공동체와 바다의 관계에 대해 내가 스스로 탐구할 수 있도록\n"
            "답을 알려주지 말고, 나에게 질문만 던져줘.\n"
            "준비됐어? 시작할게."
        ),
        "system": (
            "너는 완도 초등학교 6학년 학생의 생태 탐구를 돕는 AI야.\n"
            "학생이 방금 어부사시사 하사(여름)를 읽었어.\n\n"
            "이 대화의 목표: 학생이 지역 공동체와 바다의 관계를 이해하여 공동체 의식을 기른다.\n\n"
            "규칙:\n"
            "- 절대 직접적인 답을 알려주지 마. 학생이 스스로 생각하도록 질문만 해.\n"
            "- 한 번에 질문 1~2개만. 짧고 열린 질문으로.\n"
            "- 완도 어민 공동체, 어촌계, 세대 간 바다 경험 차이 맥락을 활용해.\n"
            "- 학생의 가족·마을 어른들의 바다 이야기와 어부사시사를 연결하도록 유도해.\n"
            "- 따뜻하고 친근한 말투로, '~야', '~어?' 형태로 편하게 말해줘.\n"
            "- 대화가 5~6번 오가면 자연스럽게 마무리하며:\n"
            "  '공동체와 바다에 대해 가장 탐구하고 싶은 질문을 1개 만들어봐.' 라고 안내해줘."
        ),
        "steps": [
            ("1", "하사 한 소절 소리 내어 읽기", "'지국총' 소리를 함께 내봐도 좋아요"),
            ("2", "아래 시작 문장을 복사해서 채팅에 입력하기", "그대로 붙여넣고 전송!"),
            ("3", "가족·마을의 바다 이야기 떠올리며 대답하기", "어르신들의 이야기도 생각해봐요"),
            ("4", "공동체와 바다에 관한 탐구 질문 1개 완성하기", "함께 해결하고 싶은 질문을 만들어요"),
        ],
        "qtypes": ["사실 질문", "관계 질문", "갈등 질문", "실천 질문"],
        "example": "예) 어르신의 바다 경험과 내 바다 경험이 어떻게 다를까?",
    },
    "A": {
        "emoji": "🍂",
        "num": "3영역",
        "title": "수국의 청광",
        "season": "가을(秋) · 바다에 묻다",
        "goal": "생태적 실천력",
        "stage": "H단계 1차시",
        "theme": "나와 자연 문제의 관계",
        "color": "#833C00",
        "bg": "#FCE4D6",
        "poem": (
            "수국의 청광이 긔 더욱 반갑도다\n"
            "가을 바다의 맑은 빛이 참으로 반갑구나\n"
            "얄리얄리 얄랑성 얄라리 얄라"
        ),
        "starter": (
            "안녕! 나는 완도에 사는 6학년이야.\n"
            "방금 어부사시사 추사를 읽었어.\n"
            "가을 바다가 얼마나 풍요롭고 맑았는지 느껴졌는데,\n"
            "지금 우리 완도 바다는 많이 달라진 것 같아.\n"
            "내가 이 문제에 대해 스스로 탐구할 수 있도록\n"
            "답을 알려주지 말고, 나에게 질문만 던져줘.\n"
            "준비됐어? 시작할게."
        ),
        "system": (
            "너는 완도 초등학교 6학년 학생의 생태 탐구를 돕는 AI야.\n"
            "학생이 방금 어부사시사 추사(가을)를 읽었어.\n\n"
            "이 대화의 목표: 학생이 생태 위기를 인식하고 실천 방향을 탐구하여 생태적 실천력을 기른다.\n\n"
            "규칙:\n"
            "- 절대 직접적인 답을 알려주지 마. 학생이 스스로 생각하도록 질문만 해.\n"
            "- 한 번에 질문 1~2개만. 짧고 열린 질문으로.\n"
            "- 해양 쓰레기, 수온 변화, 잘피 숲 소멸, 어획량 감소 등 완도 실제 생태 문제 맥락 활용.\n"
            "- 고전 속 풍요로운 바다와 현재 바다의 차이를 학생 스스로 연결하도록 유도해.\n"
            "- 따뜻하고 친근한 말투로, '~야', '~어?' 형태로 편하게 말해줘.\n"
            "- 대화가 5~6번 오가면 자연스럽게 마무리하며:\n"
            "  '내가 실제로 할 수 있는 것과 관련된 탐구 질문을 1개 만들어봐.' 라고 안내해줘."
        ),
        "steps": [
            ("1", "추사 한 소절 소리 내어 읽기", "가을 바다의 맑은 빛을 상상해봐요"),
            ("2", "아래 시작 문장을 복사해서 채팅에 입력하기", "그대로 붙여넣고 전송!"),
            ("3", "지금 완도 바다와 시 속 바다를 비교하며 대답하기", "내가 직접 본 바다를 떠올려봐요"),
            ("4", "내가 할 수 있는 실천에 관한 탐구 질문 1개 완성하기", "작은 것부터 생각해도 좋아요"),
        ],
        "qtypes": ["문제 질문", "원인 질문", "실천 질문", "아이디어 질문"],
        "example": "예) 완도 바다 쓰레기를 줄이기 위해 내가 할 수 있는 게 뭘까?",
    },
    "L": {
        "emoji": "❄️",
        "num": "4영역",
        "title": "천지가 가득하여",
        "season": "겨울(冬) · 세계를 품다",
        "goal": "세계시민성",
        "stage": "H단계 1차시",
        "theme": "나와 세계의 관계",
        "color": "#4C3163",
        "bg": "#EAE0F0",
        "poem": (
            "천지가 가득하여 흰 눈이 3~4 자\n"
            "온 세상이 흰 눈으로 가득 차 있구나\n"
            "얄리얄리 얄랑성 얄라리 얄라"
        ),
        "starter": (
            "안녕! 나는 완도에 사는 6학년이야.\n"
            "방금 어부사시사 동사를 읽었어.\n"
            "겨울 바다를 묵묵히 지킨 어부의 마음이 느껴졌어.\n"
            "우리 완도의 이야기를 세계와 나누는 것에 대해\n"
            "내가 스스로 생각할 수 있도록\n"
            "답을 알려주지 말고, 나에게 질문만 던져줘.\n"
            "준비됐어? 시작할게."
        ),
        "system": (
            "너는 완도 초등학교 6학년 학생의 생태 탐구를 돕는 AI야.\n"
            "학생이 방금 어부사시사 동사(겨울)를 읽었어.\n\n"
            "이 대화의 목표: 학생이 완도 생태 이야기를 세계와 연결하여 세계시민성을 기른다.\n\n"
            "규칙:\n"
            "- 절대 직접적인 답을 알려주지 마. 학생이 스스로 생각하도록 질문만 해.\n"
            "- 한 번에 질문 1~2개만. 짧고 열린 질문으로.\n"
            "- 기후위기, 해수면 상승, 세계 해안 생태 위기 등 글로벌 맥락을 자연스럽게 활용해.\n"
            "- 완도의 경험이 세계와 어떻게 연결될 수 있는지 학생 스스로 찾도록 유도해.\n"
            "- 따뜻하고 친근한 말투로, '~야', '~어?' 형태로 편하게 말해줘.\n"
            "- 대화가 5~6번 오가면 자연스럽게 마무리하며:\n"
            "  '세계 시민으로서 탐구하고 싶은 질문을 1개 만들어봐.' 라고 안내해줘."
        ),
        "steps": [
            ("1", "동사 한 소절 소리 내어 읽기", "겨울 바다의 고요함을 느껴봐요"),
            ("2", "아래 시작 문장을 복사해서 채팅에 입력하기", "그대로 붙여넣고 전송!"),
            ("3", "완도와 세계의 연결에 대해 생각하며 대답하기", "다른 나라 바다 이야기와도 연결해봐요"),
            ("4", "세계시민으로서 탐구 질문 1개 완성하기", "완도에서 세계로 나아가는 질문을 만들어요"),
        ],
        "qtypes": ["연결 질문", "세계 질문", "비교 질문", "실천 질문"],
        "example": "예) 완도 어부들의 지혜를 세계 사람들과 어떻게 나눌 수 있을까?",
    },
}

# ── 세션 상태 초기화 ─────────────────────────────────────
def init_state():
    for key in AREAS:
        if f"chat_{key}" not in st.session_state:
            st.session_state[f"chat_{key}"] = []
        if f"questions_{key}" not in st.session_state:
            st.session_state[f"questions_{key}"] = []
        if f"final_q_{key}" not in st.session_state:
            st.session_state[f"final_q_{key}"] = ""
    if "current_area" not in st.session_state:
        st.session_state.current_area = "H"

init_state()

# ── CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 헤더 숨기기 */
#MainMenu, footer, header { visibility: hidden; }

/* 사이드바 */
[data-testid="stSidebar"] {
    background: #1C1A18;
}
[data-testid="stSidebar"] * { color: #E8E4DF !important; }
[data-testid="stSidebar"] .stSelectbox label { color: #9B9591 !important; font-size: 12px; }

/* 채팅 말풍선 */
.user-msg {
    display: flex; justify-content: flex-end; margin: 6px 0;
}
.user-bubble {
    background: #2E75B6; color: #fff;
    padding: 10px 15px; border-radius: 18px 4px 18px 18px;
    max-width: 78%; font-size: 14px; line-height: 1.65;
    word-break: break-word;
}
.ai-msg {
    display: flex; justify-content: flex-start; margin: 6px 0; gap: 8px;
}
.ai-avatar {
    width: 28px; height: 28px; border-radius: 50%;
    background: #F0EDE8; border: 1px solid #E0DDD8;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; flex-shrink: 0; margin-top: 2px;
}
.ai-bubble {
    background: #F7F5F0; color: #1C1A18;
    padding: 10px 15px; border-radius: 4px 18px 18px 18px;
    max-width: 78%; font-size: 14px; line-height: 1.65;
    border: 1px solid #E0DDD8; word-break: break-word;
}

/* 시 텍스트 */
.poem-box {
    background: #F7F5F0;
    border-radius: 12px;
    padding: 16px 20px;
    font-family: 'Nanum Myeongjo', serif;
    font-size: 15px; line-height: 2;
    color: #1C1A18;
    border-left: 4px solid currentColor;
    margin: 8px 0;
}

/* 단계 카드 */
.step-row {
    display: flex; gap: 10px; align-items: flex-start;
    padding: 8px 0; border-bottom: 1px solid #F0EDE8;
}
.step-dot {
    width: 24px; height: 24px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.step-text { font-size: 13.5px; line-height: 1.5; }
.step-tip { font-size: 11px; color: #9B9591; font-style: italic; margin-top: 2px; }

/* 배너 */
.area-banner {
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
    color: white;
}
.banner-season { font-size: 12px; opacity: .85; margin-bottom: 4px; letter-spacing: .06em; }
.banner-title { font-family: 'Nanum Myeongjo', serif; font-size: 24px; font-weight: 700; margin-bottom: 4px; }
.banner-sub { font-size: 13px; opacity: .8; }
.banner-badge {
    display: inline-block; margin-top: 10px;
    background: rgba(255,255,255,.2); color: white;
    font-size: 11px; padding: 3px 12px; border-radius: 20px;
}

/* 질문 아이템 */
.q-item {
    display: flex; align-items: flex-start; gap: 8px;
    padding: 10px 14px; border-radius: 10px;
    border: 1px solid #E0DDD8; background: #F7F5F0;
    font-size: 13px; margin-bottom: 6px;
}
.q-badge {
    font-size: 10px; font-weight: 500; padding: 2px 8px;
    border-radius: 10px; white-space: nowrap; flex-shrink: 0;
}

/* 최종 질문 박스 */
.final-box {
    background: white; border-radius: 12px;
    border: 1.5px solid #E0DDD8; padding: 16px 20px;
}
.final-label {
    font-size: 11px; color: #9B9591;
    text-transform: uppercase; letter-spacing: .08em;
    margin-bottom: 8px; display: block;
}

/* 시작 문장 박스 */
.starter-box {
    background: #F7F5F0; border-radius: 10px;
    padding: 14px 16px; font-size: 13px; color: #4A4642;
    line-height: 1.75; white-space: pre-line;
    border-left: 3px solid currentColor; margin: 8px 0 12px;
}

/* Streamlit 버튼 커스텀 */
.stButton > button {
    border-radius: 8px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 13px !important;
}

/* 채팅 컨테이너 높이 */
.chat-container {
    max-height: 400px; overflow-y: auto;
    padding: 8px 4px;
}
</style>
""", unsafe_allow_html=True)


# ── 사이드바 ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 H.E.A.L.")
    st.markdown("**탐구 질문 만들기**")
    st.markdown("---")

    # API 키 입력
    st.markdown("**Anthropic API 키**")
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="sk-ant-api03-...",
        label_visibility="collapsed",
        key="api_key_input",
    )
    if api_key:
        st.success("✓ API 키 입력됨", icon=None)
    else:
        st.info("API 키를 입력하면 AI와 대화할 수 있어요", icon=None)

    st.markdown("---")

    # 영역 선택
    st.markdown("**영역 선택**")
    for k, v in AREAS.items():
        label = f"{v['emoji']} {v['num']} {v['title']}"
        active = st.session_state.current_area == k
        if st.button(
            label,
            key=f"tab_{k}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            st.session_state.current_area = k
            st.rerun()

    st.markdown("---")

    # 현재 영역 기록 현황
    cur = st.session_state.current_area
    q_count = len(st.session_state[f"questions_{cur}"])
    chat_count = len([m for m in st.session_state[f"chat_{cur}"] if m["role"] == "user"])
    col1, col2 = st.columns(2)
    with col1:
        st.metric("대화 횟수", chat_count)
    with col2:
        st.metric("기록한 질문", q_count)

    st.markdown("---")
    st.markdown(
        '<div style="font-size:11px;color:#6B6560;line-height:1.6">'
        '어부사시사(漁父四時詞)<br>'
        '윤선도(尹善道, 1587~1671)<br>'
        '조선시대 완도 보길도에서 창작'
        '</div>',
        unsafe_allow_html=True,
    )


# ── 메인 영역 ────────────────────────────────────────────
cur = st.session_state.current_area
area = AREAS[cur]
color = area["color"]
bg = area["bg"]

# 배너
st.markdown(
    f'<div class="area-banner" style="background:linear-gradient(135deg,{color}CC,{color})">'
    f'<div class="banner-season">{area["emoji"]} {area["season"]}</div>'
    f'<div class="banner-title">{area["title"]}</div>'
    f'<div class="banner-sub">{area["num"]} · {area["stage"]} · 목표: {area["goal"]}</div>'
    f'<span class="banner-badge">탐구 주제: {area["theme"]}</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── 2단 레이아웃: 안내 | 채팅 ──────────────────────────
col_left, col_right = st.columns([1, 1.1], gap="medium")

# ── 왼쪽: 활동 안내 ─────────────────────────────────────
with col_left:
    # 시 텍스트
    with st.expander("📖 어부사시사 시 구절 보기", expanded=False):
        st.markdown(
            f'<div class="poem-box" style="border-left-color:{color}">{area["poem"]}</div>',
            unsafe_allow_html=True,
        )

    # 활동 순서
    st.markdown("**활동 순서**")
    steps_html = ""
    for num, text, tip in area["steps"]:
        steps_html += (
            f'<div class="step-row">'
            f'<div class="step-dot" style="background:{color}">{num}</div>'
            f'<div><div class="step-text">{text}</div>'
            f'<div class="step-tip">{tip}</div></div>'
            f'</div>'
        )
    st.markdown(steps_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 시작 문장
    st.markdown("**시작 문장** — 아래 문장을 복사해서 채팅에 붙여넣기")
    st.markdown(
        f'<div class="starter-box" style="border-left-color:{color}">{area["starter"]}</div>',
        unsafe_allow_html=True,
    )
    if st.button("📋 시작 문장 복사하기", key=f"copy_{cur}", use_container_width=True):
        st.code(area["starter"], language=None)
        st.info("위 텍스트를 선택해서 복사한 뒤 채팅창에 붙여넣어 주세요!", icon="💡")


# ── 오른쪽: AI 채팅 ─────────────────────────────────────
with col_right:
    st.markdown("**AI와 대화하기**")

    # 채팅 메시지 표시
    chat_html = '<div class="chat-container">'
    chat_msgs = st.session_state[f"chat_{cur}"]

    if not chat_msgs:
        chat_html += (
            '<div style="text-align:center;padding:40px 0;color:#9B9591;font-size:13px">'
            '<div style="font-size:32px;margin-bottom:8px">💬</div>'
            '시작 문장을 복사해서 아래에 붙여넣어 보세요</div>'
        )
    else:
        for msg in chat_msgs:
            if msg["role"] == "user":
                chat_html += (
                    f'<div class="user-msg">'
                    f'<div class="user-bubble" style="background:{color}">{msg["content"].replace(chr(10),"<br>")}</div>'
                    f'</div>'
                )
            else:
                chat_html += (
                    f'<div class="ai-msg">'
                    f'<div class="ai-avatar">🤖</div>'
                    f'<div class="ai-bubble">{msg["content"].replace(chr(10),"<br>")}</div>'
                    f'</div>'
                )
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # 입력창
    user_input = st.chat_input(
        "AI 질문에 내 생각을 써봐요 (Enter = 전송)",
        key=f"chat_input_{cur}",
    )

    # 대화 초기화 버튼
    if st.button("🗑 대화 초기화", key=f"clear_{cur}", type="secondary"):
        st.session_state[f"chat_{cur}"] = []
        st.rerun()

    # 메시지 전송 처리
    if user_input:
        if not api_key:
            st.error("왼쪽 사이드바에서 API 키를 먼저 입력해주세요!")
        else:
            # 사용자 메시지 추가
            st.session_state[f"chat_{cur}"].append(
                {"role": "user", "content": user_input}
            )

            # Claude API 호출
            try:
                client = anthropic.Anthropic(api_key=api_key)
                messages = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state[f"chat_{cur}"]
                ]
                with st.spinner("AI가 생각하는 중..."):
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=800,
                        system=area["system"],
                        messages=messages,
                    )
                reply = response.content[0].text
                st.session_state[f"chat_{cur}"].append(
                    {"role": "assistant", "content": reply}
                )
            except anthropic.AuthenticationError:
                st.error("API 키가 올바르지 않아요. 사이드바에서 다시 확인해주세요.")
                st.session_state[f"chat_{cur}"].pop()
            except Exception as e:
                st.error(f"연결 오류가 발생했어요: {str(e)}")
                st.session_state[f"chat_{cur}"].pop()

            st.rerun()


# ── 탐구 질문 기록 ───────────────────────────────────────
st.markdown("---")
st.markdown("### 📝 탐구 질문 기록")

q_col1, q_col2 = st.columns([3, 1])
with q_col1:
    new_q_text = st.text_input(
        "질문 입력",
        placeholder="대화 중 떠오른 질문을 적어봐요",
        label_visibility="collapsed",
        key=f"q_input_{cur}",
    )
with q_col2:
    q_type = st.selectbox(
        "유형",
        area["qtypes"],
        label_visibility="collapsed",
        key=f"q_type_{cur}",
    )

if st.button("➕ 질문 추가", key=f"add_q_{cur}", use_container_width=False):
    if new_q_text.strip():
        st.session_state[f"questions_{cur}"].append(
            {"type": q_type, "text": new_q_text.strip()}
        )
        st.rerun()
    else:
        st.warning("질문을 입력해주세요!")

# 질문 목록 표시
q_list = st.session_state[f"questions_{cur}"]
if q_list:
    for i, q in enumerate(q_list):
        q_col_a, q_col_b = st.columns([11, 1])
        with q_col_a:
            st.markdown(
                f'<div class="q-item">'
                f'<span class="q-badge" style="background:{bg};color:{color}">{q["type"]}</span>'
                f'<span style="flex:1">{q["text"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with q_col_b:
            if st.button("✕", key=f"del_q_{cur}_{i}", help="삭제"):
                st.session_state[f"questions_{cur}"].pop(i)
                st.rerun()
else:
    st.markdown(
        '<div style="text-align:center;padding:16px;color:#9B9591;font-size:13px">'
        'AI와 대화하면서 떠오른 질문을 기록해봐요</div>',
        unsafe_allow_html=True,
    )


# ── 최종 탐구 질문 ──────────────────────────────────────
st.markdown("---")
st.markdown("### ⭐ 최종 탐구 질문")
st.caption(f"이 영역 전체 수업에서 탐구하고 싶은 핵심 질문 1개 | {area['example']}")

final_q = st.text_area(
    "최종 탐구 질문",
    value=st.session_state[f"final_q_{cur}"],
    placeholder=f"이 영역에서 가장 탐구하고 싶은 질문 1개를 써봐요\n{area['example']}",
    height=90,
    label_visibility="collapsed",
    key=f"final_q_input_{cur}",
)
st.session_state[f"final_q_{cur}"] = final_q


# ── 저장 버튼 ────────────────────────────────────────────
st.markdown("---")
save_col1, save_col2 = st.columns([3, 1])

def make_record_text():
    now = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
    q_list = st.session_state[f"questions_{cur}"]
    f_q = st.session_state[f"final_q_{cur}"]
    msgs = st.session_state[f"chat_{cur}"]

    lines = [
        "H.E.A.L. 프로젝트 탐구 질문 기록",
        "=" * 48,
        f"영역: {area['num']} {area['title']}",
        f"계절: {area['season']}",
        f"탐구 목표: {area['goal']} | 탐구 주제: {area['theme']}",
        f"저장 시각: {now}",
        "=" * 48,
        "",
    ]

    if q_list:
        lines.append(f"[ 탐구 질문 목록 ({len(q_list)}개) ]")
        for i, q in enumerate(q_list, 1):
            lines.append(f"  {i}. [{q['type']}] {q['text']}")
        lines.append("")

    if f_q:
        lines.append("[ ⭐ 최종 탐구 질문 ]")
        lines.append(f"  {f_q}")
        lines.append("")

    user_msgs = [m for m in msgs if m["role"] == "user"]
    if msgs:
        lines.append(f"[ AI 대화 기록 ({len(user_msgs)}회) ]")
        for m in msgs:
            speaker = "나" if m["role"] == "user" else "AI"
            lines.append(f"\n{speaker}: {m['content']}")
        lines.append("")

    return "\n".join(lines)


with save_col1:
    record_text = make_record_text()
    today = datetime.now().strftime("%Y%m%d")
    filename = f"HEAL_{area['num'].replace('영역','')}_탐구질문_{today}.txt"

    st.download_button(
        label="💾 기록 파일로 저장하기",
        data=record_text.encode("utf-8"),
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
        type="primary",
    )

with save_col2:
    if st.button("🗑 전체 초기화", key=f"clear_all_{cur}", use_container_width=True):
        st.session_state[f"chat_{cur}"] = []
        st.session_state[f"questions_{cur}"] = []
        st.session_state[f"final_q_{cur}"] = ""
        st.rerun()
