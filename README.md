# 🛠️ Fixlog Backend

Fixlog의 백엔드 레포지토리입니다.  
Django, PostgreSQL, Docker Compose, Nginx, Uvicorn 기반으로 개발되었으며, 자동화/무중단 배포, TDD, Logger, 공통 에러 처리 등 실무 환경을 최대한 반영합니다.

---

## 🚀 프로젝트 소개

- **목표**  
  개발자 문제 해결/기록 커뮤니티(Fixlog) 서비스의 API 및 핵심 비즈니스 로직 구현

- **주요 기능**
  - RESTful API (회원, 피드, 댓글, 프로젝트 등)
  - JWT 인증, 소셜 로그인 지원(확장 예정)
  - 공통 예외 및 커스텀 오류 코드 적용
  - TDD(테스트 우선 개발), 통합/단위 테스트
  - 실시간 처리/알림(향후 Redis, WebSocket 도입)
  - 로깅, 트래픽 모니터링, 배포 자동화

---

## 📦 기술 스택

| 분류       | 사용 기술                                      |
| ---------- | --------------------------------------------- |
| Framework  | Django                                        |
| DB         | PostgreSQL                                    |
| Server     | Docker Compose, Nginx, Uvicorn                |
| Test       | pytest, Django Test                           |
| Cache      | Redis                                         |
| 배포/자동화 | Github Actions, Docker Hub, 무중단 배포 스크립트 |
| 기타       | Logger, custom_exception, Kanban(우선순위 관리) |

---


## ⚙️ 환경설정 & 실행

1. **환경 변수 설정**  
   `.env` 파일을 프로젝트 루트에 작성

2. **로컬 개발 실행**
    ```bash
    docker-compose up --build
    ```

3. **DB 마이그레이션**
    ```bash
    docker-compose exec backend python manage.py migrate
    ```

4. **테스트 실행(TDD 필수)**
    ```bash
    docker-compose exec backend pytest
    ```

---

## 🚀 배포

- **자동화**: GitHub Actions → Docker Hub → 서버 자동 배포
- **무중단**: nginx + Uvicorn + reload (blue-green, zero-downtime)
- 배포 관련 스크립트와 설정은 `/deploy/` 및 도커파일 참고

---

## 📝 커밋 & PR 컨벤션

### 1. 커밋 메시지 규칙  
`#태그 : 내용` 형식 (한글, 간단명료하게)

| 태그      | 의미                       |
| --------- | -------------------------- |
| #add      | 새 기능 추가               |
| #fix      | 코드 단순 수정             |
| #test     | 테스트 코드 작성/수정      |
| #bug      | 버그 수정 (shit, error!)   |
| #remove   | 코드/파일 삭제             |
| #refact   | 코드 리팩토링              |
| #docs     | 문서/주석 추가, 수정       |
| #merge    | 브랜치 병합                |
| #deploy   | 배포 관련 커밋             |
| #style    | 코드 스타일 변경           |

> 예시:  
> `#add : 회원가입 API 추가`  
> `#bug : JWT 인증 오류 수정`

### 2. PR 규칙  
- PR 제목에 날짜 포함 (`YYYY-MM-DD`)
- **PR 템플릿** 사용  
- 상세 설명은 **간결+자세**하게  
- 두 명 이상 승인 후 머지  
- **코드리뷰 필수**: 스타일, 중복 코드 등 꼼꼼히 확인

---

## 📚 개발 규칙

- **Logger 필수 사용**  
  - 예외/에러는 logger로 기록  
  - 운영 환경 로깅 세팅(예: Sentry, ELK 등 확장 가능)

- **TDD 원칙**  
  - 테스트 코드 없이 PR/머지 불가  
  - 실패하는 테스트 케이스부터 작성 → 기능 구현

- **공통 에러 처리**  
  - `config/custom_exception.py`에 오류 코드/메시지 통일  
  - 모든 View/Service에서 예외 통합 사용

- **Redis 도입**  
  - 세션, 캐시, (실시간 기능 예정) 활용

- **우선순위 & 일정 관리**  
  - **칸반보드** 필수 사용 (Trello, Github Projects 등)
  - 할 일 목록화, 우선순위 명시 후 진행

---

## 💡 기타 참고사항

- 코드/기능 변경 시 반드시 테스트/리뷰 후 반영
- DB 구조/모델 변경 시 ERD, 마이그레이션 논의 필수
- 공식문서(README, 주석) 작성/유지
- 오류 메시지/코드는 반드시 **custom_exception.py**에 통일 관리

---

## 📢 문의 및 기여

- 개발팀 채널 및 이슈 게시판 이용  
- 코드 기여 전 README/컨벤션 숙지  
- 궁금한 점은 팀 내/이슈로 자유롭게 질문



