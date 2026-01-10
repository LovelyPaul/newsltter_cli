# 변경 이력 (Changelog)

## v2.0 (2026-01-04)

### 주요 변경사항

#### RSS 소스 대폭 확장
- **이전**: 61개 RSS 소스
- **현재**: 107개 RSS 소스 (46개 추가, 75% 증가)
- **효과**: 뉴스 수집량 15개 → 26개 (73% 증가)

#### 키워드 필터링 시스템 도입
- Google News RSS 의존성 완전 제거
- 카테고리별 키워드 기반 필터링 도입
- 실제 RSS 본문 내용을 기반으로 AI 요약 생성

**이전 문제점**:
- Google News RSS는 제목만 제공 (본문 없음)
- AI가 제목만으로 요약 생성 → 부정확

**해결책**:
- 전문 IT 매체 RSS 직접 연동
- RSS description/content 필드에서 실제 본문 수집
- 정확한 AI 요약 생성 가능

#### 브랜드 우선순위 가중치
- Display 카테고리에 priority_brands 필드 추가
- LG, 삼성, 소니, 하이센스, TCL 뉴스에 +20점 가중치
- 중요 브랜드 뉴스가 상위에 노출

#### RSS 타임아웃 처리
- 문제: AMD Blog 등 일부 RSS 피드가 응답 느림 → 프로세스 멈춤
- 해결: socket.setdefaulttimeout(15) 설정
- 15초 내 응답 없으면 자동 스킵
- 안정성 대폭 향상

#### 카테고리 재구성 (8개)
1. **Display** (14개 RSS): TV, 모니터, 디스플레이 전문
2. **ID** (11개 RSS): LED, 사이니지, 전자칠판 전문
3. **PC** (14개 RSS): PC 하드웨어, 제조사 블로그
4. **Audio_AV** (8개 RSS): 오디오, 스피커, 헤드폰
5. **AI_Cloud** (15개 RSS): AI, 클라우드, 머신러닝
6. **Tech_Industry** (15개 RSS): 기술 산업, 스타트업, 반도체
7. **Korea_IT** (17개 RSS): 한국 IT 뉴스, 스타트업
8. **Global_Media** (13개 RSS): 글로벌 기술 뉴스

#### AI 모델 업데이트
- Gemini 2.5 Pro → Gemini 2.0 Flash로 변경
- 더 빠른 응답 속도
- 무료 API 할당량 충분 (1,500회/일)

### 성능 개선

| 항목 | 이전 | 현재 | 개선율 |
|------|------|------|--------|
| RSS 소스 | 61개 | 107개 | +75% |
| 뉴스 수집 (주말) | 15개 | 26개 | +73% |
| 실행 시간 | ~90초 | ~170초 | - |
| 안정성 | 타임아웃 발생 | 자동 처리 | +100% |

### 기술적 변경

#### main.py
```python
# 추가된 기능
import socket
socket.setdefaulttimeout(15)  # RSS 타임아웃 15초

# 변경된 함수
def fetch_news_by_category():
    # Google News 제거
    # RSS 소스만 사용
    # 키워드 필터링 추가

def calculate_scores():
    # priority_brands 가중치 추가
    # brand_weight = 20
```

#### config.yaml
```yaml
# 추가된 설정
categories:
  Display:
    keywords: [...]  # 새로 추가
    priority_brands: [...]  # 새로 추가
    rss_sources: [...]  # 대폭 확장

weights:
  brand_priority: 20  # 새로 추가
```

### 버그 수정
- ✅ RSS 타임아웃으로 프로세스 멈춤 현상 해결
- ✅ KeyError 'query' 오류 수정 (query 필드 optional 처리)
- ✅ AI 요약 품질 개선 (제목 → 본문 기반)

### 알려진 이슈
- AMD Blog RSS가 간헐적으로 타임아웃 (15초 후 자동 스킵)
- 지디넷코리아 RSS 연결 오류 발생 (Connection reset by peer)
- 주말에는 많은 RSS 피드가 업데이트 안 됨

---

## v1.0 (2026-01-03)

### 초기 릴리스
- Google News RSS 기반 뉴스 수집
- AI 요약 (Gemini, GPT, Claude 지원)
- Outlook 호환 HTML 생성
- 수동 큐레이션 CLI
- 자동 실행 모드
- 아카이빙 및 로깅
