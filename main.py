#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Tech News Curator (DTNC)
MS본부 뉴스레터 자동 생성 시스템

작성일: 2026-01-04
"""

import yaml
import feedparser
import difflib
import os
import sys
import urllib.parse
import logging
import argparse
import json
import re
import time
import requests
import socket
from datetime import datetime, date
from dateutil import parser as date_parser
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

# RSS 피드 파싱 시 타임아웃 설정 (초)
socket.setdefaulttimeout(15)

# 환경 변수 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv가 설치되지 않았습니다. 환경 변수를 시스템에서 로드합니다.")

# AI 라이브러리 (선택사항)
AI_AVAILABLE = {
    'gemini': False,
    'openai': False,
    'claude': False
}

try:
    import google.generativeai as genai
    AI_AVAILABLE['gemini'] = True
except ImportError:
    pass

try:
    from openai import OpenAI
    AI_AVAILABLE['openai'] = True
except ImportError:
    pass

try:
    from anthropic import Anthropic
    AI_AVAILABLE['claude'] = True
except ImportError:
    pass


# =================================================================
# 로깅 설정
# =================================================================
def setup_logging(config: dict) -> logging.Logger:
    """로깅 설정"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_format = log_config.get('log_format', '[%(asctime)s] [%(levelname)s] %(message)s')
    date_format = log_config.get('date_format', '%Y-%m-%d %H:%M:%S')

    # 로거 생성
    logger = logging.getLogger('DTNC')
    logger.setLevel(log_level)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러
    if log_config.get('log_to_file', True):
        log_dir = Path(log_config.get('log_dir', 'logs'))
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"newsletter_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)

    return logger


# =================================================================
# 설정 로드
# =================================================================
def load_config() -> dict:
    """config.yaml 파일 로드"""
    config_file = Path('config.yaml')
    if not config_file.exists():
        print(f"❌ [ERROR] config.yaml 파일을 찾을 수 없습니다.")
        print(f"   경로: {config_file.absolute()}")
        sys.exit(1)

    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# =================================================================
# 공휴일/주말 체크
# =================================================================
def should_skip_today(config: dict, logger: logging.Logger) -> bool:
    """주말/공휴일 체크"""
    automation = config.get('automation', {})
    today = date.today()

    # 주말 체크
    if automation.get('skip_weekends', True):
        if today.weekday() >= 5:  # 토요일(5), 일요일(6)
            logger.info("오늘은 주말입니다. 프로그램을 종료합니다.")
            return True

    # 공휴일 체크 (workalendar 설치 시)
    if automation.get('skip_holidays', True):
        try:
            from workalendar.asia import SouthKorea
            cal = SouthKorea()
            if cal.is_holiday(today):
                logger.info("오늘은 공휴일입니다. 프로그램을 종료합니다.")
                return True
        except ImportError:
            pass

    return False


# =================================================================
# AI 요약 생성
# =================================================================
class AISummarizer:
    """AI 기반 뉴스 요약 생성"""

    def __init__(self, config: dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.ai_config = config.get('ai_summary', {})
        self.provider = os.getenv('AI_SUMMARY_PROVIDER', self.ai_config.get('provider', 'none'))
        self.enabled = os.getenv('USE_AI_SUMMARY', str(self.ai_config.get('enabled', False))).lower() == 'true'

        if self.enabled and self.provider != 'none':
            self._initialize_client()

    def _initialize_client(self):
        """AI 클라이언트 초기화"""
        if self.provider == 'gemini' and AI_AVAILABLE['gemini']:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
                self.client = genai.GenerativeModel(model_name)
                self.logger.info(f"✓ Gemini AI 초기화 완료 (모델: {model_name})")
            else:
                self.logger.warning("GEMINI_API_KEY가 설정되지 않았습니다.")
                self.enabled = False

        elif self.provider == 'openai' and AI_AVAILABLE['openai']:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.logger.info(f"✓ OpenAI GPT 초기화 완료")
            else:
                self.logger.warning("OPENAI_API_KEY가 설정되지 않았습니다.")
                self.enabled = False

        elif self.provider == 'claude' and AI_AVAILABLE['claude']:
            api_key = os.getenv('CLAUDE_API_KEY')
            if api_key:
                self.client = Anthropic(api_key=api_key)
                self.logger.info(f"✓ Claude AI 초기화 완료")
            else:
                self.logger.warning("CLAUDE_API_KEY가 설정되지 않았습니다.")
                self.enabled = False
        else:
            self.logger.info("AI 요약 기능이 비활성화되어 있습니다.")
            self.enabled = False

    def summarize(self, title: str, description: str) -> str:
        """뉴스 요약 생성"""
        if not self.enabled:
            return self._fallback_summary(description)

        try:
            prompt = self.ai_config.get('prompt_template', '').format(
                title=title,
                description=description[:1200]  # 최대 1200자로 증가
            )

            if self.provider == 'gemini':
                # API 할당량 문제 방지를 위한 지연
                # gemini-1.5-flash: 15 RPM (분당 15개)
                time.sleep(1.5)  # 1.5초 지연으로 안전하게 설정
                response = self.client.generate_content(prompt)
                summary = response.text.strip()

            elif self.provider == 'openai':
                model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
                max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '200'))

                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
                )
                summary = response.choices[0].message.content.strip()

            elif self.provider == 'claude':
                model = os.getenv('CLAUDE_MODEL', 'claude-3-haiku-20240307')
                max_tokens = int(os.getenv('CLAUDE_MAX_TOKENS', '200'))

                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                summary = response.content[0].text.strip()

            # 길이 제한
            max_length = self.ai_config.get('max_summary_length', 200)
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."

            return summary

        except Exception as e:
            self.logger.warning(f"AI 요약 실패: {str(e)}")
            if self.ai_config.get('fallback_to_rss', True):
                return self._fallback_summary(description)
            return "요약을 생성할 수 없습니다."

    def translate_title(self, title: str) -> str:
        """영문 제목을 한글로 번역"""
        if not self.enabled:
            return title

        try:
            prompt = f"다음 영문 뉴스 제목을 간결한 한글로 번역해주세요. 번역만 출력하고 다른 설명은 하지 마세요:\n\n{title}"

            if self.provider == 'gemini':
                time.sleep(1.5)
                response = self.client.generate_content(prompt)
                return response.text.strip()

            elif self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()

            elif self.provider == 'claude':
                response = self.client.messages.create(
                    model=os.getenv('CLAUDE_MODEL', 'claude-3-haiku-20240307'),
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()

            return title

        except Exception as e:
            self.logger.debug(f"제목 번역 실패: {str(e)}")
            return title

    def _fallback_summary(self, description: str) -> str:
        """RSS description을 간단히 정리"""
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', description)
        text = text.strip()

        # 빈 텍스트 처리
        if not text or len(text) < 10:
            return "요약 정보가 없습니다."

        # 최대 길이 설정 (2-3줄 분량)
        max_length = self.ai_config.get('max_summary_length', 350)

        # 문장 단위로 자르기 (더 자연스러운 요약)
        sentences = text.replace('。', '.').split('.')
        result = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # 현재 결과에 문장 추가 시 최대 길이 초과 체크
            if len(result) + len(sentence) + 2 > max_length:
                if result:  # 이미 일부 문장이 있으면 중단
                    break
                else:  # 첫 문장이 너무 길면 잘라서 사용
                    result = sentence[:max_length] + "..."
                    break

            result += sentence + ". "

        result = result.strip()

        # 결과가 너무 짧으면 원본 텍스트 사용
        if len(result) < 50:
            result = text[:max_length] + "..." if len(text) > max_length else text

        return result if result else "요약 정보가 없습니다."


# =================================================================
# 텍스트 정리
# =================================================================
def clean_text(text: str) -> str:
    """HTML 태그 제거 및 텍스트 정리"""
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    return text.strip()


# =================================================================
# 기사 본문 가져오기 (웹 스크래핑)
# =================================================================
def fetch_article_content(url: str, logger: logging.Logger) -> str:
    """
    뉴스 URL에서 실제 기사 본문 추출
    Google News RSS는 본문이 없으므로 직접 웹페이지에서 가져옴
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # 기사 본문 추출 시도 (다양한 태그 패턴)
        # 대부분의 뉴스 사이트는 article, .article-body, #article-body 등을 사용
        content = ""

        # 패턴 1: <article> 태그
        article_tag = soup.find('article')
        if article_tag:
            # <script>, <style>, <aside> 태그 제거
            for tag in article_tag.find_all(['script', 'style', 'aside', 'nav', 'header', 'footer']):
                tag.decompose()
            content = article_tag.get_text(separator=' ', strip=True)

        # 패턴 2: 일반적인 본문 클래스/ID
        if not content:
            selectors = [
                'article-body', 'article_body', 'articleBody',
                'news-content', 'news_content', 'newsContent',
                'post-content', 'entry-content', 'content-body'
            ]
            for selector in selectors:
                elem = soup.find(class_=selector) or soup.find(id=selector)
                if elem:
                    for tag in elem.find_all(['script', 'style', 'aside', 'nav']):
                        tag.decompose()
                    content = elem.get_text(separator=' ', strip=True)
                    break

        # 패턴 3: <p> 태그들의 집합 (최후의 수단)
        if not content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                # 길이가 30자 이상인 <p> 태그만 수집
                valid_paras = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30]
                content = ' '.join(valid_paras[:10])  # 최대 10개 문단만

        # 텍스트 정리
        content = re.sub(r'\s+', ' ', content).strip()

        if len(content) < 100:
            logger.debug(f"기사 본문이 너무 짧음 (URL: {url[:50]}...)")
            return ""

        # 최대 2000자로 제한 (AI 입력용)
        return content[:2000]

    except requests.Timeout:
        logger.debug(f"기사 가져오기 타임아웃 (URL: {url[:50]}...)")
        return ""
    except Exception as e:
        logger.debug(f"기사 가져오기 실패: {str(e)[:50]}")
        return ""


# =================================================================
# 뉴스 수집
# =================================================================
def fetch_news_by_category(
    category: str,
    query: str,
    config: dict,
    logger: logging.Logger,
    summarizer: AISummarizer,
    target_date: date = None
) -> List[Dict]:
    """카테고리별 뉴스 수집 (RSS 피드 전용)"""
    logger.info(f">>> [{category}] 뉴스 수집 시작")

    news_list = []
    today = target_date if target_date else date.today()

    # 카테고리별 RSS 소스에서만 수집
    cat_config = config['categories'].get(category, {})
    rss_sources = cat_config.get('rss_sources', [])
    keywords = cat_config.get('keywords', [])

    if not rss_sources:
        logger.warning(f"    [{category}] RSS 소스가 설정되지 않았습니다")
        return news_list

    for rss_source in rss_sources:
        try:
            url = rss_source.get('url') if isinstance(rss_source, dict) else rss_source
            name = rss_source.get('name', url) if isinstance(rss_source, dict) else url

            feed = feedparser.parse(url)
            count_before = len(news_list)

            for entry in feed.entries:
                news_item = parse_feed_entry(entry, today, config, summarizer, logger, keywords, source_name=name)
                if news_item:
                    news_list.append(news_item)

            collected = len(news_list) - count_before
            logger.info(f"    {name}: {collected}개 수집")

        except Exception as e:
            logger.warning(f"    RSS 소스 오류 ({name}): {str(e)}")

    logger.info(f"    [{category}] 총 {len(news_list)}개 수집 완료")
    return news_list


def parse_feed_entry(
    entry,
    today: date,
    config: dict,
    summarizer: AISummarizer,
    logger: logging.Logger,
    keywords: List[str] = None,
    source_name: str = None
) -> Optional[Dict]:
    """RSS 엔트리 파싱"""
    try:
        # 날짜 필터링
        pub_date_dt = date_parser.parse(entry.published)
        if pub_date_dt.date() != today:
            return None
    except:
        return None

    # 제목 추출
    original_title = entry.title
    title = original_title

    # 제외 키워드 체크
    exclude_keywords = config.get('exclude_keywords', [])
    if any(bad in title for bad in exclude_keywords):
        return None

    # 카테고리 키워드 필터링 (keywords가 있는 경우만)
    if keywords:
        # 제목 또는 description에 키워드가 하나라도 포함되어 있는지 확인
        description = entry.get('description', entry.get('summary', ''))
        combined_text = (title + " " + clean_text(description)).lower()

        if not any(keyword.lower() in combined_text for keyword in keywords):
            return None

    # 기사 본문 가져오기
    # Google News RSS는 본문이 없으므로 URL에서 직접 가져옴
    description = entry.get('description', entry.get('summary', ''))

    # Google News URL은 리다이렉트 URL이므로 스크래핑 스킵
    # 대신 제목을 description으로 사용
    cleaned_desc = clean_text(description)
    if len(cleaned_desc) < 20:
        # description이 거의 없으면 제목 사용
        description = title

    # 영문 제목 번역 (한글이 포함되어 있지 않으면 번역)
    if source_name and not any('\uac00' <= c <= '\ud7a3' for c in original_title):
        # 한글이 없으면 영문 뉴스로 간주하고 번역
        try:
            translated_title = summarizer.translate_title(original_title)
            title = f"[{source_name}] {translated_title}"
        except:
            title = f"[{source_name}] {original_title}"
    elif source_name:
        # 한글 뉴스는 출처만 표시
        title = f"[{source_name}] {original_title}"

    # AI 요약 생성
    summary = summarizer.summarize(original_title, clean_text(description))

    return {
        'title': title,
        'original_title': original_title,
        'source': source_name,
        'link': entry.link,
        'summary': summary,
        'score': 0,
        'pub_date': pub_date_dt
    }


# =================================================================
# 중복 제거
# =================================================================
def remove_duplicates(news_list: List[Dict], logger: logging.Logger) -> List[Dict]:
    """제목 유사도 기반 중복 제거"""
    unique = []
    for news in news_list:
        is_dup = False
        for existing in unique:
            sim = difflib.SequenceMatcher(None, news['title'], existing['title']).ratio()
            if sim > 0.7:
                is_dup = True
                break
        if not is_dup:
            unique.append(news)

    if len(news_list) != len(unique):
        logger.info(f"    중복 제거: {len(news_list)}개 → {len(unique)}개")

    return unique


# =================================================================
# 스코어링
# =================================================================
def calculate_scores(news_list: List[Dict], query: str, config: dict, category: str = None) -> List[Dict]:
    """키워드 매칭 기반 스코어링 + 우선순위 브랜드 가중치"""
    keywords = query.replace(" OR ", " ").split() if query else []
    weight = config.get('weights', {}).get('title_match', 10)
    brand_weight = config.get('weights', {}).get('brand_priority', 20)

    # 카테고리별 우선순위 브랜드 가져오기
    priority_brands = []
    if category:
        cat_config = config.get('categories', {}).get(category, {})
        priority_brands = cat_config.get('priority_brands', [])

    for news in news_list:
        score = 0
        title_lower = news['title'].lower()

        # 키워드 매칭 점수
        for kw in keywords:
            if kw.lower() in title_lower:
                score += weight

        # 우선순위 브랜드 가중치
        if priority_brands:
            for brand in priority_brands:
                if brand.lower() in title_lower:
                    score += brand_weight
                    break  # 하나라도 매칭되면 가중치 추가

        news['score'] = score

    # 점수 내림차순 정렬
    return sorted(news_list, key=lambda x: x['score'], reverse=True)


# =================================================================
# 수동 큐레이션 (CLI)
# =================================================================
def curate_category(
    category: str,
    news_list: List[Dict],
    max_items: int,
    logger: logging.Logger
) -> List[Dict]:
    """대화형 CLI 큐레이션"""
    while True:
        # 화면 클리어
        os.system('cls' if os.name == 'nt' else 'clear')

        print(f"\n{'='*70}")
        print(f"[{category}] 큐레이션 (현재 {len(news_list)}개 / 목표 {max_items}개)")
        print('='*70)

        for idx, news in enumerate(news_list):
            title_display = news['title'][:60] + "..." if len(news['title']) > 60 else news['title']
            print(f" {idx:2d}. {title_display}")

        print('-'*70)
        print("명령어: d 번호(삭제) / m 번호 위치(이동) / q(다음 카테고리로)")
        print('-'*70)

        cmd = input("입력 >> ").strip().split()

        if not cmd:
            continue

        action = cmd[0].lower()

        if action == 'q':
            # 최종적으로 상위 max_items 개수만큼 자르기
            final_list = news_list[:max_items]
            logger.info(f"[{category}] 큐레이션 완료 (최종 {len(final_list)}개)")
            return final_list

        elif action == 'd' and len(cmd) > 1:
            try:
                idx = int(cmd[1])
                if 0 <= idx < len(news_list):
                    deleted = news_list.pop(idx)
                    print(f"✓ {idx}번 뉴스 삭제됨: \"{deleted['title'][:50]}...\"")
                else:
                    print("❌ 유효하지 않은 번호입니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
            input("\nEnter를 눌러 계속...")

        elif action == 'm' and len(cmd) > 2:
            try:
                src = int(cmd[1])
                dst = int(cmd[2])
                if 0 <= src < len(news_list) and 0 <= dst < len(news_list):
                    item = news_list.pop(src)
                    news_list.insert(dst, item)
                    print(f"✓ {src}번 뉴스를 {dst}번 위치로 이동")
                else:
                    print("❌ 유효하지 않은 번호입니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
            input("\nEnter를 눌러 계속...")


# =================================================================
# HTML 생성
# =================================================================
def generate_html(final_data: Dict, config: dict, logger: logging.Logger) -> str:
    """Jinja2 템플릿으로 HTML 생성"""
    env = Environment(loader=FileSystemLoader('.'))

    try:
        template = env.get_template('template.html')
    except Exception as e:
        logger.error(f"template.html 파일을 찾을 수 없습니다: {e}")
        sys.exit(1)

    html = template.render(
        title=config['newsletter_title'],
        intro=config['intro_text'],
        date=datetime.now().strftime("%Y년 %m월 %d일"),
        data=final_data
    )

    filename = f"newsletter_{datetime.now().strftime('%Y%m%d')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"✓ HTML 파일 생성: {filename}")
    return filename


# =================================================================
# 아카이빙
# =================================================================
def archive_newsletter(filename: str, config: dict, final_data: Dict, logger: logging.Logger):
    """뉴스레터 아카이빙"""
    archive_config = config.get('archive', {})
    if not archive_config.get('enabled', True):
        return

    archive_dir = Path(archive_config.get('archive_dir', 'archive'))

    # 연/월 폴더 생성
    now = datetime.now()
    year_month_dir = archive_dir / str(now.year) / f"{now.month:02d}"
    year_month_dir.mkdir(parents=True, exist_ok=True)

    # HTML 파일 복사
    import shutil
    archive_file = year_month_dir / filename
    shutil.copy(filename, archive_file)

    # 메타데이터 저장
    metadata = {
        'date': now.strftime('%Y-%m-%d %H:%M:%S'),
        'filename': filename,
        'categories': list(final_data.keys()),
        'total_news': sum(len(items) for items in final_data.values())
    }

    metadata_file = year_month_dir / f"metadata_{now.strftime('%Y%m%d')}.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    logger.info(f"✓ 아카이브 저장: {archive_file}")


# =================================================================
# 메인 실행
# =================================================================
def main():
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='Daily Tech News Curator')
    parser.add_argument('--auto', action='store_true', help='자동 모드 (수동 큐레이션 스킵)')
    parser.add_argument('--test', action='store_true', help='테스트 모드 (설정 확인만)')
    parser.add_argument('--date', type=str, help='수집 날짜 (YYYY-MM-DD 형식, 예: 2026-01-09)')
    args = parser.parse_args()

    # 설정 로드
    config = load_config()
    logger = setup_logging(config)

    logger.info("="*70)
    logger.info("Daily Tech News Curator - MS본부 뉴스레터 자동 생성")
    logger.info("="*70)

    # 날짜 파싱
    if args.date:
        try:
            from datetime import datetime
            args.target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
            logger.info(f">>> 사용자 지정 날짜: {args.target_date}")
        except ValueError:
            logger.error(f"잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력하세요 (예: 2026-01-09)")
            return
    else:
        args.target_date = None

    # 테스트 모드
    if args.test:
        logger.info(">>> [테스트 모드] 환경 변수 및 설정 확인")
        logger.info(f"✓ AI_SUMMARY_PROVIDER: {os.getenv('AI_SUMMARY_PROVIDER', 'none')}")
        logger.info(f"✓ AI 라이브러리 가용: {AI_AVAILABLE}")
        logger.info(f"✓ 카테고리 개수: {len(config['categories'])}")
        logger.info(">>> [테스트 완료] 모든 설정이 정상입니다.")
        return

    # 주말/공휴일 체크 (자동 모드에서만)
    if args.auto and should_skip_today(config, logger):
        sys.exit(0)

    # AI 요약기 초기화
    summarizer = AISummarizer(config, logger)

    # 자동 모드 안내
    if args.auto:
        logger.info(">>> [자동 모드] 수동 큐레이션을 생략합니다.")

    # 수집 날짜 결정 (--date 옵션이 있으면 해당 날짜, 없으면 오늘)
    if hasattr(args, 'target_date') and args.target_date:
        target_date = args.target_date
    else:
        target_date = date.today()

    logger.info(f">>> 뉴스 수집 시작 (날짜: {target_date})")

    final_data = {}

    # 카테고리별 순회
    for cat_name, cat_info in config['categories'].items():
        query = cat_info.get('query', '')  # query가 없으면 빈 문자열
        max_items = cat_info.get('max_items', 10)

        logger.info(f"\n--- 카테고리: {cat_name} ---")

        # 1. 수집
        raw_news = fetch_news_by_category(cat_name, query, config, logger, summarizer, target_date)

        if not raw_news:
            logger.warning(f"    [{cat_name}] 카테고리는 오늘 뉴스가 없습니다.")
            continue

        # 2. 중복 제거
        unique_news = remove_duplicates(raw_news, logger)

        # 3. 스코어링 (카테고리 전달하여 우선순위 브랜드 가중치 적용)
        scored_news = calculate_scores(unique_news, query, config, cat_name)

        # 4. 수동 큐레이션 (자동 모드가 아닐 때만)
        if args.auto:
            curated = scored_news[:max_items]
            logger.info(f"    [{cat_name}] 상위 {len(curated)}개 자동 선택")
        else:
            curated = curate_category(cat_name, scored_news, max_items, logger)

        if curated:
            final_data[cat_name] = curated

    # 5. HTML 생성
    if final_data:
        output_file = generate_html(final_data, config, logger)

        # 6. 아카이빙
        archive_newsletter(output_file, config, final_data, logger)

        logger.info("\n" + "="*70)
        logger.info(f"✅ [완료] '{output_file}' 파일이 생성되었습니다.")
        logger.info("="*70)
        logger.info("\n>>> [사용 방법]")
        logger.info("1. 파일을 브라우저로 엽니다 (Chrome/Edge 권장)")
        logger.info("2. Ctrl+A (전체 선택) → Ctrl+C (복사)")
        logger.info("3. Outlook 새 메일 본문에 Ctrl+V (붙여넣기)")
        logger.info("4. 수신자 입력 후 발송\n")
    else:
        logger.warning("\n>>> 생성할 뉴스가 없습니다.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n>>> 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ [오류 발생] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
