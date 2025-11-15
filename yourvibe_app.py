# yourvibe_app.py
# ------------------------------------------------------------
# 로그인 + 사용자별 방 관리 + JSON 저장 + 방 수정/삭제 + UI 템플릿 + AI 추천
# ------------------------------------------------------------

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import json
import httpx
from uuid import uuid4

from dotenv import load_dotenv
load_dotenv()

from ai_recommend import get_recommended_songs  # mood 기반 추천 (별도 파일 사용)
from openai import OpenAI

# ------------------------------------------------------------
# 🔧 FastAPI 앱 생성
# ------------------------------------------------------------
app = FastAPI()

# ------------------------------------------------------------
# 🤖 (공통) OpenAI 클라이언트 생성 함수
#   - 모듈 import 시점에 바로 OpenAI() 만들지 않고
#     실제 요청이 들어왔을 때만 생성해서 환경변수 문제로 서버가 죽지 않게 함
# ------------------------------------------------------------
def get_openai_client():
    """
    OPENAI_API_KEY 환경변수를 사용하여 OpenAI 클라이언트를 생성.
    키가 없으면 None을 반환.
    """
    try:
        client = OpenAI()  # OPENAI_API_KEY 필요
        return client
    except Exception as e:
        print("OpenAI client init error:", e)
        return None

# ------------------------------------------------------------
# 🤖 감정(mood) 기반 간단 추천 API (/api/recommend)
#   - 프론트에서 mood만 보내서 3곡 추천받는 용도
# ------------------------------------------------------------
@app.post("/api/recommend")
async def api_recommend(mood: str = Form(...)):
    """
    프론트에서 mood를 보내면 AI가 추천곡 3개를 돌려주는 엔드포인트
    (ai_recommend.get_recommended_songs 사용)
    """
    try:
        songs = get_recommended_songs(mood)
        return JSONResponse({"recommended_songs": songs})
    except Exception as e:
        print("AI recommend error (mood):", e)
        return JSONResponse(
            {"error": "AI 추천에 실패했어요. 잠시 후 다시 시도해 주세요."},
            status_code=500,
        )

# ------------------------------------------------------------
# 📦 JSON 파일 저장/불러오기 로직
# ------------------------------------------------------------
DB_PATH = "rooms.json"


def load_rooms():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_rooms():
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(rooms, f, ensure_ascii=False, indent=2)


rooms = load_rooms()

# ------------------------------------------------------------
# 🧭 유틸 함수
# ------------------------------------------------------------
def get_username(request: Request):
    return request.cookies.get("username")


def get_user_rooms(username: str):
    if username not in rooms:
        rooms[username] = {"rooms": {}}
    return rooms[username]["rooms"]

# ------------------------------------------------------------
# 📁 정적 파일 & 템플릿
# ------------------------------------------------------------
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ------------------------------------------------------------
# 🚪 로그인 / 로그아웃
# ------------------------------------------------------------
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, username: str = Form(...)):
    response = RedirectResponse("/rooms", status_code=303)
    response.set_cookie(key="username", value=username)
    if username not in rooms:
        rooms[username] = {"rooms": {}}
        save_rooms()
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("username")
    return response

# ------------------------------------------------------------
# 🏠 방 목록 페이지
# ------------------------------------------------------------
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/rooms")


@app.get("/rooms", response_class=HTMLResponse)
def list_rooms(request: Request):
    username = get_username(request)
    if not username:
        return RedirectResponse("/login", status_code=303)
    user_rooms = get_user_rooms(username)
    return templates.TemplateResponse(
        "rooms.html",
        {
            "request": request,
            "username": username,
            "rooms": user_rooms,
        },
    )

# ------------------------------------------------------------
# ➕ 새 방 생성
# ------------------------------------------------------------
@app.get("/new", response_class=HTMLResponse)
def new_room_page(request: Request):
    username = get_username(request)
    if not username:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("new_room.html", {"request": request})


@app.post("/create")
async def create_room(
    request: Request,
    title: str = Form(...),
    tag: str = Form(...),
    cover: UploadFile = File(...),
):
    username = get_username(request)
    if not username:
        return RedirectResponse("/login", status_code=303)
    user_rooms = get_user_rooms(username)

    room_id = str(uuid4())[:8]
    filepath = f"static/{username}_{room_id}_cover.png"
    with open(filepath, "wb") as f:
        f.write(await cover.read())

    user_rooms[room_id] = {
        "title": title,
        "cover": f"/{filepath}",
        "tag": tag,
        "playlist": [],
    }
    save_rooms()
    return RedirectResponse(f"/room/{room_id}", status_code=303)

# ------------------------------------------------------------
# 🎵 방 상세 보기
# ------------------------------------------------------------
@app.get("/room/{room_id}", response_class=HTMLResponse)
def room_page(request: Request, room_id: str):
    username = get_username(request)
    if not username:
        return RedirectResponse("/login", status_code=303)
    user_rooms = get_user_rooms(username)
    room = user_rooms.get(room_id)
    if not room:
        return HTMLResponse("<h1>❌ 존재하지 않는 방</h1>", status_code=404)
    return templates.TemplateResponse(
        "room_detail.html",
        {
            "request": request,
            "room_id": room_id,
            "room": room,
        },
    )

# ------------------------------------------------------------
# ✏️ 방 제목 수정
# ------------------------------------------------------------
@app.post("/room/{room_id}/rename")
async def rename_room(request: Request, room_id: str, new_title: str = Form(...)):
    username = get_username(request)
    if not username:
        return RedirectResponse("/login", status_code=303)
    user_rooms = get_user_rooms(username)
    if room_id in user_rooms:
        user_rooms[room_id]["title"] = new_title
        save_rooms()
    return RedirectResponse(f"/room/{room_id}", status_code=303)

# ------------------------------------------------------------
# 🗑 방 삭제
# ------------------------------------------------------------
@app.post("/room/{room_id}/delete")
async def delete_room(request: Request, room_id: str):
    username = get_username(request)
    if not username:
        return RedirectResponse("/login", status_code=303)
    user_rooms = get_user_rooms(username)
    if room_id in user_rooms:
        del user_rooms[room_id]
        save_rooms()
    return RedirectResponse("/rooms", status_code=303)

# ------------------------------------------------------------
# 🔍 음악 검색 (iTunes API)
# ------------------------------------------------------------
@app.get("/search")
def search(q: str):
    r = httpx.get(
        "https://itunes.apple.com/search",
        params={"term": q, "media": "music", "limit": 5},
        timeout=10,
    )
    items = r.json().get("results", [])
    return [
        {"title": x.get("trackName"), "artist": x.get("artistName")}
        for x in items
        if x.get("trackName")
    ]

# ------------------------------------------------------------
# ➕ 곡 추가
# ------------------------------------------------------------
@app.post("/api/{room_id}/add")
async def add_track(request: Request, room_id: str):
    username = get_username(request)
    if not username:
        return RedirectResponse("/login", status_code=303)
    user_rooms = get_user_rooms(username)
    data = await request.json()
    track = {
        "title": data.get("title"),
        "artist": data.get("artist"),
        "moods": data.get("moods", []),
    }
    user_rooms[room_id]["playlist"].append(track)
    save_rooms()
    return {"ok": True}

# ------------------------------------------------------------
# 🤖 AI 큐레이터 추천 기능 (방 기반 추천)
#   - 방 안의 플레이리스트를 기반으로 비슷한 곡 5개 추천
#   - JSON 형식으로만 응답 받기
# ------------------------------------------------------------
@app.post("/api/{room_id}/recommend")
async def recommend_tracks(request: Request, room_id: str):
    username = get_username(request)
    if not username:
        return JSONResponse({"error": "로그인이 필요합니다."}, status_code=401)

    user_rooms = get_user_rooms(username)
    room = user_rooms.get(room_id)
    if not room:
        return JSONResponse({"error": "방을 찾을 수 없습니다."}, status_code=404)

    tracks = room.get("playlist", [])
    if not tracks:
        return JSONResponse({"error": "플레이리스트에 곡이 없어요."}, status_code=400)

    track_titles = [f"{t['title']} - {t['artist']}" for t in tracks]

    prompt = f"""
아래 곡들과 비슷한 감성의 음악 5곡을 추천해줘.
반드시 아래 JSON 형태로만 답해줘. 다른 말은 쓰지 마.

{{
  "recommended_songs": [
    {{"title": "곡 제목", "artist": "아티스트"}},
    ...
  ]
}}

기준 곡 리스트: {", ".join(track_titles)}
"""

    client = get_openai_client()
    if client is None:
        return JSONResponse(
            {"error": "OpenAI 설정(OPENAI_API_KEY)이 올바르지 않아요."},
            status_code=500,
        )

    try:
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt  # response_format 제거!
        )

        # 🔥 Responses API는 아래 형태로 텍스트 반환함
        raw = resp.output[0].content[0].text
        print("AI raw:", raw)

        data = json.loads(raw)  # 우리가 직접 JSON 파싱

        if "recommended_songs" not in data:
            return JSONResponse(
                {"error": "AI 응답 형식(JSON)이 올바르지 않아요."},
                status_code=500
            )

        return JSONResponse(data)

    except Exception as e:
        import traceback
        print("AI recommend error (room):", e)
        traceback.print_exc()
        return JSONResponse(
            {"error": f"AI 오류: {e}"},
            status_code=500
        )
