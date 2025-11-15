# ai_recommend.py
import os
import json
from openai import OpenAI


def get_recommended_songs(mood: str):
    """
    간단한 mood 기반 AI 추천 함수.
    OpenAI 클라이언트는 이 함수 안에서 생성한다.
    환경변수 OPENAI_API_KEY가 없으면 바로 에러를 던진다.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY 환경변수가 없습니다!")
        raise RuntimeError("OpenAI 설정(OPENAI_API_KEY)이 올바르지 않아요.")

    # 🔥 API 키를 명시적으로 설정해서 절대 실패하지 않도록 처리
    client = OpenAI(api_key=api_key)

    prompt = f"""
    '{mood}' 분위기에 어울리는 노래 3곡을 JSON 형태로 추천해줘.

    출력 형식(정확히 이렇게만):
    {{
        "recommended_songs": [
            {{"title": "곡 제목", "artist": "가수"}},
            {{"title": "곡 제목", "artist": "가수"}},
            {{"title": "곡 제목", "artist": "가수"}}
        ]
    }}

    추가 설명, 말, 장황한 텍스트를 절대 넣지 마.
    """

    # 🔥 responses API (JSON 포맷 강제 가능)
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        response_format={"type": "json_object"}
    )

    # 응답 내용 추출
    raw_json = resp.output[0].content[0].text

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        print("❌ JSON 파싱 에러:")
        print(raw_json)
        raise RuntimeError("AI 응답을 JSON으로 읽을 수 없어요.")

    return data.get("recommended_songs", [])
