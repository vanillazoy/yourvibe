# yourvibe_app.py
# ------------------------------------------------------------
# 로그인 + 사용자별 방 관리 + JSON 저장 + 방 수정/삭제 + UI 템플릿
# ------------------------------------------------------------

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, json, httpx
from uuid import uuid4

app = FastAPI()

# -------------------------------
# 📦 JSON 파일 저장/불러오기 로직
# -------------------------------
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

# -------------------------------
# 🧭 유틸 함수
# -------------------------------
def get_username(request: Request):
    return request.cookies.get("username")

def get_user_rooms(username: str):
    if username not in rooms:
        rooms[username] = {"rooms": {}}
    return rooms[username]["rooms"]

# -------------------------------
# 📁 정적 파일 & 템플릿
# -------------------------------
if not os.path.exists("static"): os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# -------------------------------
# 🚪 로그인 / 로그아웃
# -------------------------------
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

# -------------------------------
# 🏠 방 목록 페이지
# -------------------------------
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/rooms")

@app.get("/rooms", response_class=HTMLResponse)
def list_rooms(request: Request):
    username = get_username(request)
    if not username:
        return RedirectResponse("/login", status_code=303)
    user_rooms = get_user_rooms(username)
    return templates.TemplateResponse("rooms.html", {
        "request": request,
        "username": username,
        "rooms": user_rooms
    })

# -------------------------------
# ➕ 새 방 생성
# -------------------------------
@app.get("/new", response_class=HTMLResponse)
def new_room_page(request: Request):
    username = get_username(request)
    if not username:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("new_room.html", {"request": request})

@app.post("/create")
async def create_room(request: Request, title: str = Form(...), tag: str = Form(...), cover: UploadFile = File(...)):
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
        "playlist": []
    }
    save_rooms()
    return RedirectResponse(f"/room/{room_id}", status_code=303)

# -------------------------------
# 🎵 방 상세 보기
# -------------------------------
@app.get("/room/{room_id}", response_class=HTMLResponse)
def room_page(request: Request, room_id: str):
    username = get_username(request)
    if not username:
        return RedirectResponse("/login", status_code=303)
    user_rooms = get_user_rooms(username)
    room = user_rooms.get(room_id)
    if not room:
        return HTMLResponse("<h1>❌ 존재하지 않는 방</h1>", status_code=404)
    return templates.TemplateResponse("room_detail.html", {
        "request": request,
        "room_id": room_id,
        "room": room
    })

# -------------------------------
# ✏️ 방 제목 수정
# -------------------------------
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

# -------------------------------
# 🗑 방 삭제
# -------------------------------
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

# -------------------------------
# 🔍 음악 검색
# -------------------------------
@app.get("/search")
def search(q: str):
    r = httpx.get("https://itunes.apple.com/search", params={"term": q, "media": "music", "limit": 5}, timeout=10)
    items = r.json().get("results", [])
    return [{"title": x.get("trackName"), "artist": x.get("artistName")} for x in items if x.get("trackName")]

# -------------------------------
# ➕ 곡 추가
# -------------------------------
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
        "moods": data.get("moods", [])
    }
    user_rooms[room_id]["playlist"].append(track)
    save_rooms()
    return {"ok": True}
