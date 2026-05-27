# 🌊 H.E.A.L 프로젝트 — AI 토론 도우미

초등학교 6학년 사회·국어 융합 수업용 AI 토론 도우미입니다.

**토론 주제:** 기후 위기를 막기 위해 해상풍력 발전단지 건설은 반드시 필요하다

---

## 🚀 Streamlit Cloud 배포 방법

### 1단계 — GitHub에 올리기
```
heal_app/
├── app.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
└── README.md
```

### 2단계 — Streamlit Cloud 설정
1. [share.streamlit.io](https://share.streamlit.io) 접속
2. **New app** → GitHub 저장소 연결
3. Main file path: `app.py`
4. **Deploy!**

### 3단계 — API 키 입력 (⚠️ 중요)
배포 후 앱 우측 하단 **⋮ → Settings → Secrets** 클릭 후 아래 입력:
```toml
GEMINI_API_KEY = "AIza..."
```
저장하면 앱이 자동 재시작됩니다.

---

## 💻 로컬 실행 방법

```bash
pip install -r requirements.txt

# API 키 설정
mkdir -p .streamlit
echo 'GEMINI_API_KEY = "AIza..."' > .streamlit/secrets.toml

# 실행
streamlit run app.py
```

---

## 📚 참고 기사 (앱 내 근거 자료)

| 출처 | 날짜 | 핵심 내용 |
|------|------|-----------|
| LG헬로비전 | 2024.09.03 | 완도 금일도 주민 어선 100척 해상 반대 시위 |
| 오마이뉴스 | 2025.05.16 | 조업공간 91.3% 중복, 해풍법 보상 규정 미비 |
| KBC | 2025.03.16 | 해상경계 분쟁, 어장→해상풍력으로 확대 |
| 조선비즈 | 2026.02.27 | 하나은행·남동발전 MOU 체결, 연내 착공 임박 |

---

## 🎯 학습 목표

- **주장 / 이유 / 근거**의 차이를 이해한다
- 근거는 객관적 자료(통계, 전문가 의견, 공식 발표)임을 안다
- 실제 뉴스 기사를 읽고 근거로 활용하는 능력을 기른다
