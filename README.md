# H.E.A.L. 프로젝트 탐구 질문 만들기 앱

어부사시사를 읽고 AI와 대화하며 탐구 질문을 생성하는 Streamlit 웹앱입니다.

## 파일 구조

```
heal_streamlit/
├── app.py                  # 메인 앱
├── requirements.txt        # 패키지 목록
├── .streamlit/
│   └── config.toml         # 테마 설정
└── README.md
```

## Streamlit Cloud 배포 방법 (무료)

### 1단계: GitHub 저장소 만들기
1. [github.com](https://github.com) 접속 → 로그인
2. 우상단 **+** → **New repository**
3. 저장소 이름: `heal-app` (예시)
4. **Public** 선택 → **Create repository**

### 2단계: 파일 업로드
GitHub 저장소에 아래 파일들을 업로드:
- `app.py`
- `requirements.txt`
- `.streamlit/config.toml` (폴더째로 업로드)

### 3단계: Streamlit Cloud 배포
1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인
3. **New app** 클릭
4. 저장소 선택 → Main file path: `app.py`
5. **Deploy** 클릭 → 2~3분 후 URL 생성

### 4단계: API 키 설정 (Secrets)
Streamlit Cloud에서 API 키를 안전하게 관리하려면:
1. 앱 대시보드 → **Settings** → **Secrets**
2. 아래 내용 입력:
```toml
ANTHROPIC_API_KEY = "sk-ant-api03-..."
```
3. `app.py`의 API 키 입력 부분을 수정:
```python
# 기존: api_key = st.text_input(...)
# 변경: api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
```

## 로컬 실행 방법

```bash
pip install streamlit anthropic
streamlit run app.py
```
브라우저에서 `http://localhost:8501` 접속

## 기능

- **4개 영역**: 1영역(봄·나) / 2영역(여름·우리) / 3영역(가을·자연) / 4영역(겨울·세계)
- **단계별 안내**: 활동 순서 + 시작 문장 제공
- **AI 대화**: Claude Sonnet으로 탐구 질문 생성 유도
- **질문 기록**: 유형별 탐구 질문 저장
- **최종 질문**: 핵심 탐구 질문 1개 작성
- **파일 저장**: 대화 기록 + 질문 텍스트 파일 다운로드

## 수업 활용법

```
1. 어부사시사 해당 계절 시 낭독 (5분)
2. 해당 영역 탭 선택
3. 시작 문장 복사 → 채팅창에 붙여넣기
4. AI와 자유 대화 (15분)
5. 탐구 질문 기록 + 최종 질문 완성 (5분)
6. 파일 저장 후 선생님께 제출
```
