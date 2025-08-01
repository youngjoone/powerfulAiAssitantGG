# 로컬 설정 가이드

이 프로젝트를 로컬 환경에서 실행하기 위한 완전한 설정 가이드입니다.

## 1. 시스템 요구사항

- Python 3.11 이상
- Git (프로젝트 다운로드용)
- OpenAI API 계정
- Google AI Studio 계정

## 2. 프로젝트 다운로드 및 설정

```bash
# 프로젝트 클론 (또는 ZIP 다운로드)
git clone <repository-url>
cd dual-ai-assistant

# Python 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 필요한 패키지 설치
pip install openai google-genai click rich python-dotenv
```

## 3. API 키 발급

### OpenAI API Key
1. https://platform.openai.com 방문
2. 계정 생성 또는 로그인
3. 왼쪽 메뉴에서 "API Keys" 선택
4. "Create new secret key" 클릭
5. 생성된 키를 복사 (한 번만 표시됨)
6. **주의**: 결제 정보 등록 필요 (사용량 기반 과금)

### Gemini API Key
1. https://aistudio.google.com 방문
2. Google 계정으로 로그인
3. "Get API Key" 버튼 클릭
4. API 키 생성 및 복사
5. **장점**: 기본 사용량 무료

## 4. 환경변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 편집기로 열기
nano .env
# 또는
code .env
```

### .env 파일 내용:
```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-여기에_실제_OpenAI_키_입력

# Google Gemini API Configuration  
GEMINI_API_KEY=AIzaSy여기에_실제_Gemini_키_입력

# Optional: Model Configuration (기본값 사용 가능)
OPENAI_MODEL=gpt-4o
GEMINI_MODEL=gemini-2.5-flash

# Optional: Request Configuration
MAX_TOKENS=1000
TEMPERATURE=0.7
REQUEST_TIMEOUT=30

# Optional: Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=ai_assistant.log
```

## 5. 실행 및 테스트

### 기본 사용법
```bash
# 단일 질문
python main.py "파이썬에서 딕셔너리를 설명해줘"

# 대화형 모드
python main.py --interactive

# 도움말 보기
python main.py --help
```

### 코드 생성 모드 (새 기능!)
```bash
# 코드 생성 모드
python main.py --code "Flask 웹 서버를 만들어줘"

# 특정 파일 분석 후 코드 생성
python main.py --code --files main.py "이 파일에 에러 처리를 추가해줘"

# 대화형 코드 생성 모드
python main.py --interactive --code

# 특정 프로젝트 경로 지정
python main.py --project-path /path/to/your/project --code "README.md를 만들어줘"
```

## 6. 파일 구조

로컬에 필요한 모든 파일:
```
dual-ai-assistant/
├── main.py              # CLI 메인 인터페이스
├── ai_assistant.py      # AI 어시스턴트 핵심 로직
├── file_manager.py      # 파일 시스템 관리
├── config.py           # 설정 관리
├── .env                # API 키 설정 (직접 생성)
├── .env.example        # 설정 템플릿
├── LOCAL_SETUP.md      # 이 가이드
└── README.md           # 프로젝트 설명
```

## 7. 사용 예시

### 기본 AI 대화
```bash
python main.py "머신러닝과 딥러닝의 차이점을 설명해줘"
```

### 코드 생성
```bash
# 새 파일 생성
python main.py --code "사용자 인증을 위한 Python 클래스를 만들어줘"

# 기존 파일 개선
python main.py --code --files app.py "이 파일에 로깅 기능을 추가해줘"
```

### 프로젝트 분석
```bash
# 대화형 모드에서 'show files' 명령어로 프로젝트 구조 확인
python main.py --interactive --code
> show files
```

## 8. 문제 해결

### API 키 오류
```
Error: API keys not configured properly
```
- `.env` 파일이 있는지 확인
- API 키가 올바르게 입력되었는지 확인
- 따옴표 없이 키만 입력했는지 확인

### 모듈 오류
```
ModuleNotFoundError: No module named 'openai'
```
- 가상환경이 활성화되었는지 확인
- `pip install openai google-genai click rich python-dotenv` 재실행

### 파일 권한 오류
- 프로젝트 디렉토리에 쓰기 권한이 있는지 확인
- 관리자 권한으로 실행하지 말고 사용자 권한으로 실행

## 9. 고급 기능

### 파이프라인 아키텍처
1. **ChatGPT (1단계)**: 사용자 요청 분석 및 기본 응답
2. **Gemini (2단계)**: 상세한 구현 및 기술적 설명

### 파일 관리 기능
- 프로젝트 구조 자동 스캔
- 파일 내용 읽기 및 분석
- 새 파일 생성 및 기존 파일 수정
- Git 정보 인식

이제 로컬에서 프로젝트의 파일들을 직접 분석하고 수정할 수 있는 강력한 AI 어시스턴트를 사용할 수 있습니다!