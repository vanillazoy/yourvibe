# yourvibe_app.py
# ------------------------------------------------------------
# 개선된 버전: 플레이리스트 커버 이미지 + 분위기 표현 UI 추가
# ------------------------------------------------------------

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx, os
from jinja2 import Template
from collections import defaultdict

app = FastAPI()

# 정적 파일 (이미지 업로드 저장용)
if not os.path.exists("static"): os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 데이터 저장 (메모리)
rooms = defaultdict(lambda: {"playlist": [], "cover": None, "title": "Your Vibe"})

MOODS = ["😊 기분좋음","📚 공부","🏃 운동","🌃 밤","🌧️ 잔잔","🔥 신남","💭 몽환","💖 달달"]

# HTML 템플릿
HTML = Template(r"""
<!doctype html>
<meta charset="utf-8" />
<title>{{ room.title }} — demo</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 900px; margin: 32px auto; line-height: 1.6; }
  header { text-align: center; margin-bottom: 20px; }
  .cover { width: 200px; height: 200px; object-fit: cover; border-radius: 12px; box-shadow: 0 0 10px rgba(0,0,0,0.2); }
  .tagbox { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 8px; }
  .card { border: 1px solid #ddd; border-radius: 10px; padding: 12px; margin: 8px 0; }
  button { cursor: pointer; padding: 8px 12px; border-radius: 8px; border: 1px solid #ccc; background: #fff; }
  button:hover { background: #f5f5f5; }
  input[type="text"] { padding: 10px 12px; border-radius: 8px; border: 1px solid #ccc; min-width: 260px; }
  ol { padding-left: 20px; }
</style>
<header>
  <h1>{{ room.title }}</h1>
  {% if room.cover %}
    <img src="{{ room.cover }}" class="cover" alt="cover" />
  {% else %}
    <div style="width:200px;height:200px;border:2px dashed #ccc;border-radius:12px;display:flex;align-items:center;justify-content:center;">No Cover</div>
  {% endif %}
  <form action="/room/{{ room_id }}/set_cover" method="post" enctype="multipart/form-data" style="margin-top:10px;">
    <input type="file" name="file" accept="image/*" required>
    <button type="submit">커버 업로드</button>
  </form>
</header>

<h2>1) 분위기 태그 고르기</h2>
<div class="tagbox">
  {% for mood in moods %}
    <label class="card"><input type="checkbox" name="mood" value="{{ mood }}" /> {{ mood }}</label>
  {% endfor %}
</div>

<h2>2) 곡 검색 → 추가</h2>
<form onsubmit="search(); return false;">
  <input id="q" placeholder="곡/키워드 (예: lofi, iu, study)" />
  <button>검색</button>
</form>
<div id="results"></div>

<h2>3) 플레이리스트 보기</h2>
<label>필터:
  <select id="filterMood" onchange="load()">
    <option value="">(전체)</option>
    {% for mood in moods %}<option value="{{ mood }}">{{ mood }}</option>{% endfor %}
  </select>
</label>
<ol id="pl"></ol>

<script>
const ROOM_ID = {{ room_id | tojson }};
function getSelectedMoods(){
  return Array.from(document.querySelectorAll('input[name="mood"]:checked')).map(b=>b.value);
}
async function search(){
  const q=document.getElementById('q').value.trim(); if(!q) return;
  const res=await fetch('/search?q='+encodeURIComponent(q));
  const data=await res.json();
  const div=document.getElementById('results'); div.innerHTML='';
  data.forEach(item=>{
    const c=document.createElement('div'); c.className='card';
    const p=document.createElement('p'); p.textContent=`${item.title} - ${item.artist}`;
    const btn=document.createElement('button'); btn.textContent='이 곡 추가';
    btn.onclick=async()=>{
      await fetch(`/api/${ROOM_ID}/add`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...item,moods:getSelectedMoods()})});
      load();
    };
    c.appendChild(p); c.appendChild(btn); div.appendChild(c);
  });
}
async function load(){
  const mood=document.getElementById('filterMood').value;
  const res=await fetch(`/api/${ROOM_ID}/playlist?mood=${encodeURIComponent(mood)}`);
  const data=await res.json();
  const ol=document.getElementById('pl'); ol.innerHTML='';
  data.playlist.forEach(t=>{
    const li=document.createElement('li');
    li.textContent=`${t.title} - ${t.artist}${t.moods.length?' ['+t.moods.join(', ')+']':''}`;
    ol.appendChild(li);
  });
}
load();
</script>
""")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/room/demo")

@app.get("/room/{room_id}", response_class=HTMLResponse)
def room_page(room_id:str):
    return HTML.render(room=rooms[room_id], room_id=room_id, moods=MOODS)

@app.post("/room/{room_id}/set_cover")
async def set_cover(room_id:str, file: UploadFile = File(...)):
    filepath = f"static/{room_id}_cover.png"
    with open(filepath, "wb") as f:
        f.write(await file.read())
    rooms[room_id]["cover"] = f"/static/{room_id}_cover.png"
    return RedirectResponse(f"/room/{room_id}", status_code=303)

@app.get("/search")
def search(q:str):
    r=httpx.get("https://itunes.apple.com/search",params={"term":q,"media":"music","limit":5},timeout=10)
    items=r.json().get("results",[])
    return [{"title":x.get("trackName"),"artist":x.get("artistName")} for x in items if x.get("trackName")]

@app.post("/api/{room_id}/add")
async def add_track(room_id:str, req:Request):
    data=await req.json()
    rooms[room_id]["playlist"].append({"title":data.get("title"),"artist":data.get("artist"),"moods":data.get("moods",[])})
    return {"ok":True}

@app.get("/api/{room_id}/playlist")
def get_playlist(room_id:str, mood:str=""):
    pl=rooms[room_id]["playlist"]
    if mood:
        pl=[t for t in pl if mood in t.get("moods",[])]
    return {"playlist":pl}

# 실행: uvicorn yourvibe_app:app --reload --port 8000
