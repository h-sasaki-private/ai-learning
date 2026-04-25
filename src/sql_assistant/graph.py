from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from typing import TypedDict
from src.sql_assistant.database import get_schema, run_query
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")

# 1．Stateの定義
class SQLAssistantState(TypedDict):
    question: str
    sql: str
    query_result: str
    answer: str
    error_count: int

# 2．Nodeの定義
def generate_sql_node(state: SQLAssistantState) -> SQLAssistantState:
    """自然言語からSQLを生成するノード"""
    print(f"[generate_sql] error_count: {state['error_count']}")
    response = llm.invoke([
        HumanMessage(content=f"""以下のデータベーススキーマを参考に、質問に答えるSQLを生成してください
                     SQLの見返してください。説明は不要です。
                     
                     スキーマ：
                     {get_schema()}

質問： {state['question']}

前回のエラー（あれば）: {state['query_result']}
""")
    ])
    sql = response.content.strip()
    # コードブロックが含まれる場合は除去
    sql = sql.replace("```sql", "").replace("```", "").strip()
    print(f"[generate_sql] 生成SQL: {sql}")
    return {**state, "sql": sql}

def execute_sql_node(state: SQLAssistantState) -> SQLAssistantState:
    """SQLを実行するノード"""
    result = run_query(state["sql"])
    print(f"[execute_sql] 結果: {result}")
    return {**state, "query_result": result}

def generate_answer_node(state: SQLAssistantState) -> SQLAssistantState:
    """クエリ結果を自然言語で回答するノード"""
    response = llm.invoke([
        HumanMessage(content=f"""以下のSQLクエリの結果を元に、質問に対して自然な日本語で回答"してください。
                     
                    質問： {state['question']}
                    SQLクエリ： {state['sql']}
                    クエリ結果: {state['query_result']}
        """)
    ])
    return {**state, "answer": response.content}

def shoule_retry(state: SQLAssistantState) -> str:
    """SQLエラーの場合はリトライ、成功なら回答生成へ"""
    if "SQLエラー" in state["query_result"] and state["error_count"] < 2:
        return "retry"
    return "answer"

# 3．Graphの組み立て
def build_graph():
    graph_builder = StateGraph(SQLAssistantState)

    graph_builder.add_node("generate_sql", generate_sql_node)
    graph_builder.add_node("execute_sql", execute_sql_node)
    graph_builder.add_node("generate_answer", generate_answer_node)

    graph_builder.set_entry_point("generate_sql")
    graph_builder.add_edge("generate_sql", "execute_sql")
    graph_builder.add_conditional_edges(
        "execute_sql",
        shoule_retry,
        {
            "retry": "generate_sql", # エラーならSQL再生成
            "answer": "generate_answer", # 成功なら回答生成
        }
    )
    graph_builder.add_edge("generate_answer", END)

    return graph_builder.compile()