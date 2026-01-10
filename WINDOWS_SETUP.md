# Windows 환경 설정 가이드

## ✅ Windows 호환성

이 뉴스레터 시스템은 **Windows 10/11**에서 정상 작동합니다.

---

## 📋 사전 요구사항

### 1. Python 설치
- **Python 3.8 이상** 필요 (Python 3.13 권장)
- 다운로드: https://www.python.org/downloads/

**설치 시 주의사항:**
```
✅ "Add Python to PATH" 체크박스 반드시 선택!
```

### 2. 설치 확인
```cmd
python --version
pip --version
```

---

## 🚀 설치 방법 (Windows)

### 1. 프로젝트 폴더로 이동
```cmd
cd C:\Users\YourName\newsletter
```

### 2. 가상환경 생성
```cmd
python -m venv venv
```

### 3. 가상환경 활성화
```cmd
venv\Scripts\activate
```

활성화되면 프롬프트에 `(venv)` 표시됨:
```
(venv) C:\Users\YourName\newsletter>
```

### 4. 패키지 설치
```cmd
pip install -r requirements.txt
```

### 5. 환경 변수 설정
```cmd
copy .env.example .env
notepad .env
```

`.env` 파일에 API 키 입력:
```
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.0-flash
AI_SUMMARY_PROVIDER=gemini
USE_AI_SUMMARY=true
```

---

## 🎯 실행 방법

### 자동 모드
```cmd
venv\Scripts\activate
python main.py --auto
```

### 수동 큐레이션 모드
```cmd
venv\Scripts\activate
python main.py
```

---

## 🔧 Windows 특정 이슈 해결

### 1. 한글 깨짐 문제
**원인**: Windows 콘솔 인코딩 문제

**해결**:
```cmd
chcp 65001
```

또는 PowerShell 사용:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### 2. 가상환경 활성화 오류
**오류 메시지**: 
```
이 시스템에서 스크립트를 실행할 수 없으므로...
```

**해결** (관리자 권한 PowerShell):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. SSL 인증서 오류
**원인**: 회사 방화벽/프록시

**해결** (`.env` 파일에 추가):
```
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
```

### 4. 경로 구분자 문제
**Python 코드는 자동 처리됨**:
- macOS/Linux: `/`
- Windows: `\`
- Python `pathlib` 사용으로 자동 변환됨 ✅

---

## 📅 Windows 작업 스케줄러 설정

### 매일 오전 8시 자동 실행

1. **작업 스케줄러** 실행
   - Win + R → `taskschd.msc` 입력

2. **작업 만들기**
   - 우측 "작업 만들기" 클릭

3. **일반 탭**
   - 이름: `MS본부 뉴스레터`
   - 설명: `매일 오전 8시 뉴스레터 자동 생성`
   - ✅ 사용자가 로그온할 때만 실행
   - ✅ 가장 높은 수준의 권한으로 실행

4. **트리거 탭**
   - 새로 만들기 클릭
   - 작업 시작: `일정에 따라`
   - 설정: 매일
   - 시작: `오전 8:00`
   - ✅ 사용

5. **동작 탭**
   - 새로 만들기 클릭
   - 동작: `프로그램 시작`
   - 프로그램/스크립트:
     ```
     C:\Users\YourName\newsletter\venv\Scripts\python.exe
     ```
   - 인수 추가:
     ```
     main.py --auto
     ```
   - 시작 위치:
     ```
     C:\Users\YourName\newsletter
     ```

6. **조건 탭**
   - ☐ 컴퓨터의 AC 전원이 켜저 있는 경우에만 작업 시작
   - ✅ 예약된 시작 시간을 놓친 경우 즉시 작업 실행

7. **설정 탭**
   - ✅ 요청 시 작업 실행 허용
   - ✅ 작업이 실패하면 다시 시작 간격: `1분`

---

## 🖥️ PowerShell 스크립트 (선택사항)

더 편리한 실행을 위해 `run_newsletter.ps1` 생성:

```powershell
# run_newsletter.ps1
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 가상환경 활성화
.\venv\Scripts\Activate.ps1

# 뉴스레터 생성
python main.py --auto

# 결과 확인
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 뉴스레터 생성 완료!" -ForegroundColor Green
    
    # Outlook으로 파일 열기 (선택사항)
    $htmlFile = Get-ChildItem -Filter "newsletter_*.html" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($htmlFile) {
        Start-Process $htmlFile.FullName
    }
} else {
    Write-Host "❌ 뉴스레터 생성 실패" -ForegroundColor Red
}

# 가상환경 비활성화
deactivate
```

**실행 방법**:
```powershell
.\run_newsletter.ps1
```

---

## 🔍 경로 차이점

### macOS/Linux (현재 개발 환경)
```bash
/Users/paul/edu/Company/newsletter/
venv/bin/activate
```

### Windows
```cmd
C:\Users\YourName\newsletter\
venv\Scripts\activate
```

**Python 코드는 동일하게 작동** ✅
- `pathlib.Path` 사용으로 자동 변환
- `os.path.join()` 사용으로 호환성 보장

---

## 📊 테스트 체크리스트

Windows 환경에서 테스트:

```cmd
☐ 1. Python 설치 확인
     python --version

☐ 2. 가상환경 생성
     python -m venv venv

☐ 3. 가상환경 활성화
     venv\Scripts\activate

☐ 4. 패키지 설치
     pip install -r requirements.txt

☐ 5. .env 파일 생성
     copy .env.example .env

☐ 6. API 키 설정
     notepad .env

☐ 7. 테스트 실행
     python main.py --auto

☐ 8. HTML 파일 생성 확인
     dir newsletter_*.html

☐ 9. Outlook에서 열기
     newsletter_YYYYMMDD.html 더블클릭

☐ 10. 복사/붙여넣기 테스트
      Ctrl+A → Ctrl+C → Outlook 붙여넣기
```

---

## ⚠️ 알려진 Windows 이슈

### 1. 한글 파일명 문제
- ✅ 해결됨: UTF-8 인코딩 사용

### 2. 경로 길이 제한 (260자)
- Windows 10 1607 이상에서는 해제 가능
- 레지스트리: `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem`
  - `LongPathsEnabled` = 1

### 3. 바이러스 백신 경고
- 일부 백신이 `feedparser` 차단 가능
- 예외 처리 추가 필요

---

## 🎯 권장 환경

### 최적 환경
- Windows 10/11 (64-bit)
- Python 3.13
- PowerShell 7
- Visual Studio Code (선택)

### 최소 환경
- Windows 10 (1903 이상)
- Python 3.8+
- CMD 또는 PowerShell 5.1

---

## 📞 지원

Windows 환경에서 문제 발생 시:

1. 로그 확인
   ```cmd
   type logs\newsletter_YYYYMMDD.log
   ```

2. 환경 변수 확인
   ```cmd
   echo %PATH%
   ```

3. Python 경로 확인
   ```cmd
   where python
   ```

---

**작성일**: 2026-01-05  
**버전**: v2.0  
**상태**: Windows 호환 확인 완료 ✅
