from fastapi import FastAPI
from pydantic import BaseModel
from src.assistant.graph import build_graph
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="社内FAQ AIアシスタント")

# グラフの初期化（起動時に１回だけ実行）
graph = build_graph()

# リクエスト・レスポンスの型定義
class ChatRequest(BaseModel):
    question: str

class ChatReponse(BaseModel):
    answer: str
    retry_count: int

# エンドポイント
@app.post("/chat", response_model=ChatReponse)
def chat(request: ChatRequest):
    result = graph.invoke({
        "question": request.question,
        "answer": "",
        "is_sufficient": False,
        "retry_count": 0,
    })
    return ChatReponse(
        answer=result["answer"],
        retry_count=result["retry_count"],
    )

@app.get("/health")
def health():
    return {"status": "ok"}