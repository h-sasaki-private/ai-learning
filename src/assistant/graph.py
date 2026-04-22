from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from typing import TypedDict
from src.assistant.rag import build_rag_chain
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
rag_chain, retriever = build_rag_chain()

#1．Stateの定義
class AssistantState(TypedDict):
    question: str
    answer: str
    is_sufficient: bool
    retry_count: int

#2．Nodeの定義
def retrieve_and_answer_node(state: AssistantState) -> AssistantState:
    """RAGで検索して回答を生成するノード"""
    print(f"[retrive_and_answer] retry_count: {state['retry_count']}")
    answer = rag_chain.invoke(state["question"])
    return {
        **state,
        "answer": answer,
        "retry_count": state["retry_count"] + 1,
    }

def evaluate_node(state: AssistantState) -> AssistantState:
    """回答が十分か評価するノード"""
    response = llm.invoke([
        HumanMessage(content=f"""以下の回答は質問に対して十分ですか？
「十分」か「不十分」の一言だけ答えてください。
                     
                    質問: {state["question"]}
                    回答： {state["answer"]}""")
    ])
    is_sufficient = "不十分" not in response.content
    print(f"[evalutate] is_sufficient: {is_sufficient}")
    return {**state, "is_sufficient": is_sufficient}

def should_retry(state: AssistantState) -> str:
    """条件分岐：リトライするか終了するか"""
    if state["retry_count"] >+ 2:
        return "end"
    if not state["is_sufficient"]:
        return "retry"
    return "end"

# 3．Graphの組み立て
def build_graph():
    graph_builder = StateGraph(AssistantState)

    graph_builder.add_node("retrieve_and_answer", retrieve_and_answer_node)
    graph_builder.add_node("evaluate", evaluate_node)

    graph_builder.set_entry_point("retrieve_and_answer")
    graph_builder.add_edge("retrieve_and_answer", "evaluate")
    graph_builder.add_conditional_edges(
        "evaluate",
        should_retry,
        {
            "retry": "retrieve_and_answer",
            "end": END,
        }
    )

    return graph_builder.compile()