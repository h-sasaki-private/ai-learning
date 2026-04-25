from fastapi import FastAPI
from pydantic import BaseModel
from src.sql_assistant.graph import build_graph
from src.sql_assistant.database import create_database
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SQL生成AIツール")

#起動時にDBとグラフを初期化
create_database()
graph = build_graph()

# リクエスト・レスポンスの型定義
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    sql: str
    query_result: str
    answer: str

# エンドポイント
@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    result = graph.invoke({
        "question": request.question,
        "sql": "",
        "query_result": "",
        "answer": "",
        "error_count": 0,
    })
    return QueryResponse(
        question=result["question"],
        sql=result["sql"],
        query_result=result["query_result"],
        answer=result["answer"],
    )

@app.get("/health")
def health():
    return {"status": "ok"}