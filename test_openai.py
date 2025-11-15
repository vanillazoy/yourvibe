from openai import OpenAI

client = OpenAI()  # OPENAI_API_KEY 환경변수에서 키를 읽어옴

resp = client.responses.create(
    model="gpt-4.1-mini",
    input="추천할 노래 3개만 JSON으로 알려줘."
)

print(resp.output[0].content[0].text)
