# Crew API 사용 가이드

## 📋 Project 모델 구조

### 기본 필드
- `title`: 프로젝트 제목
- `description`: 프로젝트 설명
- `deadline`: 모집 마감일
- `start_date`: 프로젝트 시작일
- `end_date`: 프로젝트 종료일
- `status`: 모집 상태 ('recruiting', 'completed')
- `count`: 조회수

### ManyToMany 관계
- `positions`: 모집 포지션들 (Position 모델과 연결)
- `languages`: 사용 언어들 (Language 모델과 연결)
- `skill_tools`: 기술 스택들 (Stack 모델과 연결)

## 🔧 API 사용법

### 1. 프로젝트 생성

```json
POST /api/projects/
{
    "title": "웹 서비스 개발 프로젝트",
    "description": "React와 Django를 사용한 웹 서비스 개발",
    "deadline": "2024-08-01T00:00:00Z",
    "start_date": "2024-08-05T00:00:00Z",
    "end_date": "2024-10-31T00:00:00Z",
    "is_estimated_period": "3개월",
    "position_ids": [1, 2],  // 백엔드, 프론트엔드
    "language_ids": [1, 2],  // Python, JavaScript
    "skill_tool_ids": [1, 2, 3]  // Django, React, PostgreSQL
}
```

### 2. 프로젝트 조회 응답

```json
{
    "id": 1,
    "title": "웹 서비스 개발 프로젝트",
    "description": "React와 Django를 사용한 웹 서비스 개발",
    "deadline": "2024-08-01T00:00:00Z",
    "start_date": "2024-08-05T00:00:00Z",
    "end_date": "2024-10-31T00:00:00Z",
    "is_estimated_period": "3개월",
    "count": 15,
    "status": "recruiting",
    "project_positions": [
        {
            "position": 1,
            "position_name": "백엔드",
            "count": 2
        },
        {
            "position": 2,
            "position_name": "프론트엔드",
            "count": 1
        }
    ],
    "project_languages": [
        {
            "language": 1,
            "language_name": "Python"
        },
        {
            "language": 2,
            "language_name": "JavaScript"
        }
    ],
    "project_skill_tools": [
        {
            "skill_tool": 1,
            "skill_tool_name": "Django"
        },
        {
            "skill_tool": 2,
            "skill_tool_name": "React"
        }
    ],
    "created_at": "2024-07-06T06:00:00Z",
    "updated_at": "2024-07-06T06:00:00Z"
}
```

### 3. 필터링 옵션

```
GET /api/projects/?status=recruiting&positions=1,2&languages=1&skill_tools=1,2&ordering=popular
```

**필터 파라미터:**
- `status`: 모집 상태 ('recruiting', 'completed')
- `positions`: 포지션 ID 리스트 (AND 조건)
- `languages`: 언어 ID 리스트 (AND 조건)
- `skill_tools`: 기술스택 ID 리스트 (AND 조건)
- `ordering`: 정렬 ('popular' 또는 기본값은 최신순)

## 🗄️ 데이터베이스 테이블 구조

### 중간 테이블들
1. **project_position**
   - project_id (FK)
   - position_id (FK)
   - count (필요 인원수)

2. **project_language**
   - project_id (FK)
   - language_id (FK)

3. **project_skill_tool**
   - project_id (FK)
   - skill_tool_id (FK)

## 🚀 다음 단계

1. 데이터베이스 마이그레이션 실행:
   ```bash
   python manage.py migrate
   ```

2. 테스트 데이터 생성:
   - Position, Language, Stack 데이터 먼저 생성
   - 프로젝트 생성 시 해당 ID들 사용

3. API 테스트:
   - Swagger UI: `/docs/`
   - 각 엔드포인트별 테스트 수행 