# MS본부 뉴스레터 시스템 - 최종 요약

## 📊 시스템 현황 (v2.0)

### 핵심 지표
- **총 RSS 소스**: 107개 (전문 IT 매체)
- **카테고리**: 8개 (Display, ID, PC, Audio_AV, AI_Cloud, Tech_Industry, Korea_IT, Global_Media)
- **AI 요약**: Gemini 2.0 Flash (무료, 1,500회/일)
- **평균 수집 뉴스**: 26개 (주말), 50-100개 (평일 예상)
- **실행 시간**: 약 2-3분

### 주요 기능
1. **키워드 필터링**: 카테고리별 맞춤 키워드로 정확한 뉴스 수집
2. **브랜드 우선순위**: Display 카테고리에서 LG, 삼성 등 주요 브랜드 우선 노출
3. **AI 요약**: 실제 기사 본문을 3-4줄로 한국어 요약
4. **자동 타임아웃**: 응답 느린 RSS 소스 자동 스킵 (15초)
5. **Outlook 호환**: 복사/붙여넣기 가능한 HTML 생성

---

## 🗂️ 카테고리별 RSS 소스

### 1. Display (14개)
**전문 매체**: FlatpanelsHD, DisplayDaily, OLED-info, TFTCentral, RTINGS, HDTVTest, PC Monitors  
**AV**: AVForums, WhatHiFi  
**종합**: CNET, The Verge, Engadget, Digital Trends

### 2. ID (11개)
**LED**: MicroLED-info, OLED-info, LEDinside  
**사이니지**: Digital Signage Today, Sixteen:Nine, AV Network, Commercial Integrator, DisplayDaily  
**제조사**: 삼성 뉴스룸, LG Newsroom

### 3. PC (14개)
**하드웨어**: Tom's Hardware, AnandTech, NotebookCheck, PCMag, TechPowerUp, Guru3D, Phoronix  
**제조사**: Intel, AMD, Qualcomm, NVIDIA  
**종합**: Digital Trends, Gizmodo, Ars Technica

### 4. Audio_AV (8개)
**오디오**: AVForums, WhatHiFi, SoundGuys, Headfonics, Audio Science Review  
**종합**: CNET, The Verge, Engadget

### 5. AI_Cloud (15개)
**AI 기업**: Google AI, Microsoft AI, OpenAI, Meta AI, Anthropic  
**클라우드**: AWS Blog, Azure Blog  
**AI 전문**: VentureBeat, MarkTechPost, AI News  
**기술**: IEEE Spectrum, TechCrunch, The Verge, MIT Tech Review

### 6. Tech_Industry (15개)
**기술**: TechCrunch, The Verge, CNET, Engadget, ZDNet, Wired, Computerworld, InfoWorld  
**비즈니스**: Reuters, Bloomberg, CNBC, AP News, Nikkei Asia, Business Insider, Axios

### 7. Korea_IT (17개)
**IT 전문**: AI타임스, 지디넷코리아, 디지털타임스, 전자신문, ITWorld Korea  
**스타트업**: 바이라인네트워크, 플래텀, 벤처스퀘어  
**포털**: 네이버 헤드라인, 네이버 IT/과학  
**경제**: 한국경제, 매일경제, 연합뉴스, 비즈니스포스트, 딜사이트  
**기업**: 삼성 뉴스룸

### 8. Global_Media (13개)
**주요 언론**: NYTimes, Washington Post, Financial Times, CNBC, BBC, The Guardian  
**아시아**: Xinhua, Global Times, South China Morning Post  
**기술**: Ars Technica, Gizmodo, Digital Trends, Mashable

---

## 🚀 사용 방법

### 자동 실행 (권장)
```bash
source venv/bin/activate
python main.py --auto
```

### 수동 큐레이션
```bash
source venv/bin/activate
python main.py
```

### HTML 파일 사용
1. `newsletter_YYYYMMDD.html` 브라우저로 열기
2. Ctrl+A (전체 선택) → Ctrl+C (복사)
3. Outlook 새 메일 본문에 Ctrl+V (붙여넣기)

---

## ⚙️ 주요 설정 파일

### config.yaml
- 107개 RSS 소스 정의
- 카테고리별 키워드 설정
- 브랜드 우선순위 (Display)
- AI 요약 설정

### .env
```bash
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.0-flash
AI_SUMMARY_PROVIDER=gemini
USE_AI_SUMMARY=true
```

### main.py
- RSS 수집 로직
- 키워드 필터링
- AI 요약 생성
- HTML 템플릿 렌더링

---

## 📈 성능 비교

| 지표 | v1.0 | v2.0 | 개선율 |
|------|------|------|--------|
| RSS 소스 | 61개 | 107개 | +75% |
| 뉴스 수집 | 15개 | 26개 | +73% |
| AI 요약 정확도 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | - |
| 안정성 | 가끔 멈춤 | 자동 복구 | - |

---

## 🔧 문제 해결

### 뉴스 수집이 적음
- 주말에는 많은 매체가 업데이트 안 함
- 평일 실행 권장

### RSS 타임아웃
- 자동으로 15초 후 스킵
- 로그에서 확인 가능

### AI 요약 오류
- .env 파일의 API 키 확인
- Gemini API 무료 한도: 1,500회/일

---

## 📞 지원

- **문서**: README.md, CHANGELOG.md
- **설정**: config.yaml, .env
- **로그**: logs/ 디렉토리
- **아카이브**: archive/ 디렉토리

---

**작성일**: 2026-01-04  
**버전**: v2.0  
**상태**: 운영 준비 완료 ✅
