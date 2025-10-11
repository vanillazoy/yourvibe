# 🎧 YourVibe  
**나만의 감성 플레이리스트 공간 (FastAPI + Tailwind UI)**  

---

## 🌈 프로젝트 개요
> **YourVibe**는 사용자가 직접 감성 플레이리스트를 만들고,  
> 각자만의 음악 취향과 분위기를 카드 형태로 표현할 수 있는 개인형 음악 공간입니다.  

AI 큐레이터 기능을 통해 플레이리스트 기반의 추천도 받을 수 있습니다.  
(현재는 데모용, 추후 OpenAI API 연동 예정)

---

## 🏗️ 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | 🐍 **FastAPI**, Python 3.11 |
| Frontend (템플릿) | 🎨 **TailwindCSS**, HTML (Jinja2) |
| Database | 📁 JSON 파일 (`rooms.json`) |
| Design | 💎 Glassmorphism + 감성 다크모드 |
| AI | 🤖 (예정) OpenAI API 기반 음악 추천 기능 |

---

## 📂 폴더 구조

```plaintext
yourvibe/
│
├── yourvibe_app.py          # FastAPI 메인 서버
├── rooms.json               # 사용자별 방 데이터 저장
├── runtime.txt              # (Railway 등 배포 환경용)
├── requirements.txt         # 의존성 패키지
│
├── templates/               # Jinja2 템플릿 폴더
│   ├── login.html
│   ├── rooms.html
│   ├── room_detail.html
│   └── new_room.html
│
└── static/                  # 업로드된 커버 이미지 저장 폴더
```

---

## ⚙️ 설치 및 실행 방법

### 1️⃣ 가상환경 생성 및 실행
```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
.venv\Scripts\activate     # Windows
```

### 2️⃣ 패키지 설치
```bash
pip install -r requirements.txt
```

### 3️⃣ 서버 실행
```bash
uvicorn yourvibe_app:app --reload --port 8000
```

➡️ 브라우저에서  
**http://127.0.0.1:8000/login** 접속

---

## 🖼️ UI 구성

### 🎧 로그인 페이지  
- 감성적인 **글래스모피즘 카드 UI**
- 사용자 이름만 입력해 간단 로그인  
- 쿠키 기반 사용자 구분  

---

### 🏠 홈 (나의 플레이리스트 방 목록)
- 업로드한 **커버 이미지 기반 카드 레이아웃**
- 감성형 그라데이션 + 투명 효과  
- 방 제목 / 태그 표시  
- “＋ 새 방 만들기” 버튼으로 생성  

---

### 🎵 상세 페이지 (Room Detail)
- 커버 이미지 + 제목 + 설명  
- 추가된 곡 목록 표시  
- “🤖 AI 추천받기” 버튼 클릭 시 데모 추천 표시  
- 삭제 / 수정 기능 포함  

---

### 🪞 새 방 생성
- 제목 / 태그 / 커버 이미지 업로드  
- JSON 데이터 자동 저장  

---

## 🤖 AI 추천 기능 (데모)

현재는 간단한 예시 데이터 반환 방식입니다.  
실제 버전에서는 OpenAI API를 이용해  
사용자 플레이리스트 기반 추천곡 생성 예정입니다.

```python
@app.post("/api/{room_id}/recommend")
async def recommend_tracks(room_id: str):
    demo = [
        "Lauv - Paris in the Rain",
        "HONNE - Day 1 ◑",
        "The 1975 - Somebody Else",
        "keshi - blue",
        "Joji - Ew"
    ]
    return {"recommendations": demo}
```

---

## 💾 데이터 구조 (`rooms.json`)

```json
{
  "username": {
    "rooms": {
      "id1234": {
        "title": "Night Vibe",
        "tag": "감성적인 밤, 조용한 노래들",
        "cover": "/static/username_id1234_cover.png",
        "playlist": [
          {"title": "Lauv - Modern Loneliness", "artist": "Lauv"}
        ]
      }
    }
  }
}
```

---

## 🧭 기능 요약

| 기능 | 설명 |
|------|------|
| 🔐 로그인 | 쿠키 기반, 사용자 이름만으로 로그인 |
| 🏠 방 관리 | 생성 / 수정 / 삭제 / 커버 이미지 업로드 |
| 🎧 플레이리스트 | iTunes API로 곡 검색 후 추가 |
| 💾 데이터 | 모든 방 데이터는 `rooms.json`에 자동 저장 |
| 🎨 UI | Tailwind 기반 감성형 카드 디자인 |
| 🤖 AI 추천 | 데모용 추천 리스트, 추후 OpenAI API 연동 예정 |

---

## 💡 향후 계획

- [ ] OpenAI API 연결 (실시간 음악 추천)  
- [ ] 사용자 프로필 커스터마이징 (사진 / 소개글)  
- [ ] 방 공유 / 좋아요 기능  
- [ ] 음악 프리뷰 재생 기능 (MusicKit API)  
- [ ] “Express Myself” 전용 감정 기반 큐레이션

---

## 📸 디자인 무드  

> 🎵 감성 다크모드 + 글래스 블러 + 카드형 UI  
> “express myself” — 나를 음악으로 표현하다

| 페이지 | 설명 |
|--------|------|
| 로그인 | 글래스 카드 + 라운드 프로필 프레임 |
| 홈 | 감성 커버 카드 3열 레이아웃 |
| 상세 | 플레이리스트 + AI 추천 버튼 |
| 새 방 | 업로드형 폼 (이미지 / 제목 / 태그) |

---

## 🧠 참고

- [FastAPI Docs](https://fastapi.tiangolo.com)  
- [TailwindCSS](https://tailwindcss.com)  
- [OpenAI API](https://platform.openai.com/docs)  
- [iTunes Search API](https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/)

---

## 🩵 제작자

**Flowiny (vanillazoy)**  
> 감성과 기술의 경계를 탐색하는 개발자  
> “음악으로 사람의 무드를 연결하는 플랫폼을 만든다”

---

💫 _Your vibe, your space. — 감성을 표현하는 나만의 음악 공간._


# ✅ Git Push 전 필수 점검 및 안전 순서

# 1️⃣ 현재 상태 확인
git status

# 2️⃣ macOS 시스템 파일 무시 (.DS_Store)
echo ".DS_Store" >> .gitignore
git rm --cached .DS_Store 2>/dev/null || true

# 3️⃣ node_modules, .env 무시 설정
echo "node_modules/" >> .gitignore
echo ".env" >> .gitignore

# 4️⃣ 변경사항 스테이징 (node_modules 제외)
git add .gitignore templates yourvibe_app.py frontend package.json package-lock.json

# 5️⃣ 커밋
git commit -m "🎨 Update UI templates & frontend (React + Tailwind setup)"

# 6️⃣ 원격(main) 최신 내용 반영 (충돌 방지)
git pull origin main --rebase

# ⚠️ conflict(충돌)이 발생하면: 충돌 해결 후 아래 명령 실행
# git rebase --continue

# 7️⃣ 깃허브로 푸쉬
git push origin main

# 8️⃣ 결과 확인
# GitHub > yourvibe 레포 > main 브랜치
# ✅ templates / frontend / yourvibe_app.py / package.json 올라왔는지 확인
# 🚫 node_modules / .env / .DS_Store 파일이 보이지 않으면 성공

