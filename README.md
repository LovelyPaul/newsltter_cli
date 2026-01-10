# Daily Tech News Curator (DTNC)

MS본부 뉴스레터 자동 생성 시스템

## 📋 개요

매일 지정된 카테고리(Display, ID, PC, Audio_AV, AI_Cloud, Tech_Industry, Korea_IT, Global_Media)의 최신 뉴스를 자동으로 수집하고, AI 요약을 통해 Outlook 발송용 HTML 뉴스레터를 생성하는 시스템입니다.

### 주요 기능

- ✅ **당일 뉴스 자동 수집** (107개 전문 RSS 소스)
- ✅ **AI 기반 요약** (Gemini 2.0 Flash, GPT, Claude 지원)
- ✅ **키워드 필터링** (카테고리별 맞춤 필터링)
- ✅ **브랜드 우선순위** (Display 카테고리: LG, 삼성, 소니 등)
- ✅ **중복 제거 및 스코어링** (키워드 매칭)
- ✅ **수동 큐레이션** (CLI 대화형 인터페이스)
- ✅ **Outlook 호환 HTML** (복사/붙여넣기 가능)
- ✅ **자동 실행 모드** (스케줄러 연동)
- ✅ **RSS 타임아웃 처리** (안정성 보장)
- ✅ **아카이빙 및 로깅**

---

## 🚀 빠른 시작

### 1. 환경 설정

**Python 3.8 이상 필요**

```bash
# 패키지 설치
pip install -r requirements.txt

# 환경 변수 파일 생성
cp .env.example .env
```

### 2. API 키 설정 (선택사항)

AI 요약 기능을 사용하려면 `.env` 파일에 API 키를 설정하세요.

**추천: Google Gemini (무료)**

```bash
# .env 파일 편집
AI_SUMMARY_PROVIDER=gemini
GEMINI_API_KEY=your-api-key-here
USE_AI_SUMMARY=true
```

자세한 내용은 [docs/API_KEY_SETUP.txt](docs/API_KEY_SETUP.txt) 참고

### 3. 첫 실행

```bash
# 수동 큐레이션 모드 (권장)
python main.py

# 자동 모드 (큐레이션 스킵)
python main.py --auto

# 테스트 모드 (설정 확인만)
python main.py --test
```

### 4. HTML 파일 사용

1. 생성된 `newsletter_YYYYMMDD.html` 파일을 브라우저로 열기
2. **Ctrl+A** (전체 선택) → **Ctrl+C** (복사)
3. Outlook 새 메일 본문에 **Ctrl+V** (붙여넣기)
4. 수신자 입력 후 발송

---

## 📁 프로젝트 구조

```
newsletter/
├── config.yaml          # 카테고리, 키워드, RSS 소스 설정
├── template.html        # Outlook용 HTML 템플릿
├── main.py              # 메인 실행 파일
├── requirements.txt     # Python 패키지 목록
├── .env.example         # 환경 변수 템플릿
├── .env                 # 환경 변수 (직접 생성, Git 제외)
├── .gitignore           # Git 제외 목록
├── README.md            # 이 파일
├── docs/                # 문서 폴더
│   ├── PRD.txt          # 제품 요구사항 정의서
│   ├── techstack.txt    # 기술 스택 설명
│   ├── userflow.txt     # 사용자 플로우
│   └── API_KEY_SETUP.txt # API 키 설정 가이드
├── logs/                # 로그 파일 (자동 생성)
└── archive/             # 아카이브 (자동 생성)
```

---

## ⚙️ 설정 가이드

### config.yaml 주요 설정

```yaml
# 카테고리별 키워드 및 RSS 소스 설정
categories:
  Display:
    keywords:
      - "TV"
      - "OLED"
      - "모니터"
      - "디스플레이"
    priority_brands:  # 우선순위 브랜드 (가중치 +20)
      - "LG"
      - "삼성"
      - "Samsung"
      - "소니"
      - "Sony"
    max_items: 10
    rss_sources:
      - url: "https://www.flatpanelshd.com/rss.php"
        name: "FlatpanelsHD"
      - url: "https://tftcentral.co.uk/feed"
        name: "TFTCentral"
      # ... 총 14개 소스

  ID:
    keywords:
      - "LED"
      - "사이니지"
      - "전자칠판"
      - "signage"
    max_items: 10
    rss_sources:
      - url: "https://www.microled-info.com/rss.xml"
        name: "MicroLED-info"
      # ... 총 11개 소스

# AI 요약 설정
ai_summary:
  enabled: true
  provider: "gemini"  # gemini, openai, claude, none
  max_summary_length: 350

# 스코어링 가중치
weights:
  title_match: 10        # 제목에 키워드 포함 시
  brand_priority: 20     # 우선순위 브랜드 (Display)
  source_priority: 5     # 특정 소스 가중치

# 자동화 설정
automation:
  auto_mode: false
  skip_weekends: false
  skip_holidays: true
```

### .env 주요 설정

```bash
# AI 서비스 선택
AI_SUMMARY_PROVIDER=gemini
USE_AI_SUMMARY=true

# Gemini API (무료)
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.0-flash  # 최신 고속 모델
GEMINI_MAX_TOKENS=300
GEMINI_TEMPERATURE=0.3

# OpenAI GPT (유료)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# 회사 프록시 (필요 시)
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
```

---

## 🎯 사용 시나리오

### 시나리오 1: 매일 수동 큐레이션

```bash
# 1. 뉴스 수집 및 큐레이션
python main.py

# 2. CLI에서 각 카테고리별 뉴스 검토
# - d 5: 5번 뉴스 삭제
# - m 3 0: 3번 뉴스를 맨 위로 이동
# - q: 다음 카테고리로

# 3. HTML 생성 완료
# 4. Outlook으로 복사/붙여넣기
```

### 시나리오 2: 자동 실행 (스케줄러)

**Windows 작업 스케줄러**

```
프로그램: C:\Python39\python.exe
인수: main.py --auto
시작 위치: C:\path\to\newsletter
트리거: 매일 오전 8시
```

**macOS/Linux cron**

```bash
# crontab -e
0 8 * * 1-5 cd /path/to/newsletter && /usr/bin/python3 main.py --auto
```

### 시나리오 3: 긴급 뉴스 추가

```bash
# 1. config.yaml에 임시 카테고리 추가
# 2. python main.py 실행
# 3. 기존 카테고리는 'q'로 빠르게 스킵
# 4. 긴급 카테고리만 집중 큐레이션
```

---

## 📊 RSS 소스 현황 (총 107개)

### Display (14개)
- **전문 매체**: FlatpanelsHD, DisplayDaily, OLED-info, TFTCentral, RTINGS, HDTVTest, PC Monitors
- **AV 전문**: AVForums, WhatHiFi
- **종합 IT**: CNET, The Verge, Engadget, Digital Trends

### ID (11개)
- **LED 전문**: MicroLED-info, OLED-info, LEDinside
- **사이니지**: DisplayDaily, Digital Signage Today, Sixteen:Nine, AV Network, Commercial Integrator
- **제조사**: 삼성 뉴스룸, LG Newsroom

### PC (14개)
- **하드웨어**: Tom's Hardware, AnandTech, NotebookCheck, PCMag, TechPowerUp, Guru3D, Phoronix
- **제조사**: Intel Blog, AMD Blog, Qualcomm Blog, NVIDIA Blog
- **종합**: Digital Trends, Gizmodo, Ars Technica

### Audio_AV (8개)
- **오디오 전문**: AVForums, WhatHiFi, SoundGuys, Headfonics, Audio Science Review
- **종합**: CNET, The Verge, Engadget

### AI_Cloud (15개)
- **AI 기업**: Google AI Blog, Microsoft AI Blog, OpenAI Blog, Meta AI Blog, Anthropic News
- **클라우드**: AWS Blog, Azure Blog
- **AI 전문**: VentureBeat, MarkTechPost, AI News
- **기술**: IEEE Spectrum, TechCrunch, The Verge, MIT Technology Review

### Tech_Industry (15개)
- **기술 매체**: TechCrunch, The Verge, CNET, Engadget, ZDNet, Wired, Computerworld, InfoWorld
- **비즈니스**: Reuters, Bloomberg, CNBC, AP News, Nikkei Asia, Business Insider, Axios

### Korea_IT (17개)
- **IT 전문**: AI타임스, 지디넷코리아, 디지털타임스, 전자신문, ITWorld Korea
- **스타트업**: 바이라인네트워크, 플래텀, 벤처스퀘어
- **포털**: 네이버 헤드라인, 네이버 IT/과학
- **경제**: 한국경제, 매일경제, 연합뉴스, 비즈니스포스트, 딜사이트
- **기업**: 삼성 뉴스룸

### Global_Media (13개)
- **주요 언론**: NYTimes, Washington Post, Financial Times, CNBC, BBC, The Guardian
- **아시아**: Xinhua, Global Times, South China Morning Post
- **기술**: Ars Technica, Gizmodo, Digital Trends, Mashable

---

## 🔧 고급 사용법

### 카테고리 추가

`config.yaml` 편집:

```yaml
categories:
  NewCategory:
    keywords:
      - "키워드1"
      - "키워드2"
    max_items: 10
    rss_sources:
      - url: "https://example.com/rss"
        name: "예시 매체"
```

### RSS 소스 추가

기존 카테고리에 RSS 소스 추가:

```yaml
categories:
  Display:
    rss_sources:
      - url: "https://new-source.com/rss"
        name: "새 매체"
      # ... 기존 소스들
```

### 브랜드 우선순위 설정

Display 카테고리에서 특정 브랜드 우선:

```yaml
categories:
  Display:
    priority_brands:
      - "LG"
      - "삼성"
      - "Samsung"
      - "소니"
      - "Sony"
      - "하이센스"
      - "Hisense"
      - "TCL"
```

### 제외 키워드 설정

```yaml
exclude_keywords:
  - "광고"
  - "이벤트"
  - "프로모션"
```

---

## 📊 AI 요약 서비스 비교

| 서비스 | 무료 한도 | 품질 | 속도 | 추천 |
|--------|-----------|------|------|------|
| **Gemini Flash** | 1,500회/일 | ⭐⭐⭐⭐ | 빠름 | ✅ 권장 |
| GPT-4o-mini | - | ⭐⭐⭐⭐⭐ | 보통 | 고품질 필요 시 |
| Claude Haiku | - | ⭐⭐⭐⭐ | 빠름 | 대안 |
| RSS 기본 | 무제한 | ⭐⭐⭐ | 매우 빠름 | API 키 없을 때 |

**비용 (뉴스레터 1회 발행)**
- Gemini: 무료
- GPT-4o-mini: ~$0.01 (약 10원)
- GPT-4o: ~$0.10 (약 100원)

---

## 🐛 트러블슈팅

### 뉴스가 수집되지 않음

**원인**: 주말이거나 RSS 피드가 업데이트 안 됨

**해결**:
- 주말에는 많은 매체가 업데이트하지 않으므로 평일에 실행 권장
- 107개 RSS 소스 중 일부만 오늘 날짜 뉴스를 제공
- 키워드 필터링이 너무 엄격한지 확인

### RSS 타임아웃 오류

**원인**: 일부 RSS 피드가 응답 느림

**해결**:
- 자동으로 15초 타임아웃 처리됨
- 문제 있는 소스는 경고 로그에 표시되고 자동 스킵
- 예: `[WARNING] RSS 소스 오류 (AMD Blog): The read operation timed out`

### Outlook 레이아웃 깨짐

**원인**: 브라우저 호환성

**해결**:
- Chrome 또는 Edge 사용
- 전체 선택 후 복사 (Ctrl+A → Ctrl+C)

### API 키 오류

**원인**: 환경 변수 미설정

**해결**:
```bash
# .env 파일 확인
cat .env

# API 키 앞뒤 공백 제거
GEMINI_API_KEY=AIzaSy...  # ✅ 올바름
GEMINI_API_KEY= AIzaSy... # ❌ 공백 있음
```

### 프록시 연결 실패

**원인**: 회사 방화벽

**해결**:
```bash
# .env 파일에 추가
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
```

---

## 📚 문서

- **[PRD.txt](docs/PRD.txt)**: 제품 요구사항 정의서
- **[techstack.txt](docs/techstack.txt)**: 기술 스택 설명
- **[userflow.txt](docs/userflow.txt)**: 사용자 플로우
- **[API_KEY_SETUP.txt](docs/API_KEY_SETUP.txt)**: API 키 발급 가이드

---

## 🔒 보안 주의사항

1. **.env 파일 절대 Git 커밋 금지**
   ```bash
   # .gitignore에 자동 포함됨
   .env
   .env.local
   ```

2. **API 키 유출 시 즉시 재발급**
   - [Google Gemini Console](https://aistudio.google.com/app/apikey)
   - [OpenAI API Keys](https://platform.openai.com/api-keys)

3. **로그 파일 정기 삭제**
   ```bash
   # 30일 이상 된 로그 삭제
   find logs/ -name "*.log" -mtime +30 -delete
   ```

---

## 🤝 기여

이슈 및 개선 사항은 프로젝트 관리자에게 문의하세요.

---

## 📄 라이선스

이 프로젝트는 사내 사용을 목적으로 합니다.

---

## ✨ FAQ

**Q: Gemini와 GPT 중 무엇을 선택해야 하나요?**
A: 무료로 시작하려면 Gemini, 최고 품질이 필요하면 GPT-4o-mini를 권장합니다.

**Q: 뉴스가 너무 많이 수집돼요.**
A: `config.yaml`에서 `max_items` 값을 줄이거나, `exclude_keywords`를 추가하세요.

**Q: 주말에도 실행하고 싶어요.**
A: `config.yaml`에서 `skip_weekends: false`로 변경하세요.

**Q: 자동 모드에서도 일부만 수동 검토하고 싶어요.**
A: 현재는 전체 자동/전체 수동만 지원합니다. 추후 하이브리드 모드 추가 예정입니다.

---

## 📞 지원

- **기술 문서**: `docs/` 폴더 참고
- **API 키 설정**: `docs/API_KEY_SETUP.txt`
- **버그 리포트**: 프로젝트 관리자에게 문의

---

## 📝 업데이트 이력

### v2.0 (2026-01-04)
- ✅ RSS 소스 대폭 확장 (61개 → 107개)
- ✅ 키워드 기반 필터링 시스템 도입
- ✅ 브랜드 우선순위 가중치 추가 (Display 카테고리)
- ✅ RSS 타임아웃 처리 (15초)
- ✅ Google News 의존성 제거
- ✅ 카테고리 재구성 (8개 카테고리)
- ✅ Gemini 2.0 Flash 모델 지원
- ✅ 안정성 및 성능 개선

### v1.0 (2026-01-03)
- 초기 버전 출시
- Google News RSS 기반 뉴스 수집
- AI 요약 기능 (Gemini, GPT, Claude)
- Outlook 호환 HTML 생성

---

**Happy Newsletter Curating! 🎉**
