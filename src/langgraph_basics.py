from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage,AIMessage
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")

# 1． Stateの定義（グラフ全体で共有するデータ）
class State(TypedDict):
    messages: list
    question: str
    answer: str
    
# 2．Nodeの定義（各処理のステップ）
def think_node(state: State) -> State:
    """質問を分析して回答方針を考えるノード"""
    question = state["question"]
    response = llm.invoke([
        HumanMessage(content=f"以下の質問に答えるための方針を一言で述べてください。質問:{question}")
    ])
    print(f"[answer] {response.content}")
    return { **state, "messages": state["messages"] + [response]}

def answer_node(state: State) -> State:
    """実際に回答を生成するノード"""
    question = state["question"]
    response = llm.invoke([
        HumanMessage(content=f"以下の質問に丁寧に答えてください。 質問:{question}")
    ])
    print(f"[answer] {response.content}")
    return {**state, "answer": response.content}

# 3．Graphの組み立て
graph_builder = StateGraph(State)

# ノードを追加
graph_builder.add_node("think", think_node)
graph_builder.add_node("answer", answer_node)

# エッジを追加（流れを定義）
graph_builder.set_entry_point("think")
graph_builder.add_edge("think", "answer")
graph_builder.add_edge("answer", END)

# グラフをコンパイル
graph = graph_builder.compile()

# 4．実行
# result = graph.invoke({
#     "messages": [],
#     "question": "Pythonの非同期処理とは何ですか？",
#     "answer": "",
# })

# print("\n=== 最終回答 ===")
# print(result["answer"])


# 5．条件分岐のあるグラフ
class State2(TypedDict):
    question: str
    answer: str
    retry_count: int

def generate_node(state: State2)-> State2:
    """回答を生成するノード"""
    response = llm.invoke([
        HumanMessage(content=f"以下の質問に答えてください。質問:{state['question']}")
    ])
    print(f"[generate] retry_count: {state['retry_count']}")
    return {
        **state, 
        "answer": response.content,
        "retry_count": state["retry_count"] + 1,
    }

def check_node(state: State2) -> State2:
    """解答が純文化判断するノード"""
    response = llm.invoke([
        HumanMessage(content=f"""以下の回答は十分ですか？「十分」か「不十分」の一個だけ答えてください。回答 
                     ：{state['answer']}""")
    ])
    print(f"[check] {response.content}")
    return {**state, "answer": state["answer"]}

def should_retry(state: State2) -> str:
    """条件分岐の関数:次にどのノードに行くか返す"""
    if state["retry_count"] >= 2:
        return "end" # ２回以上リトライしたら終了
    response = llm.invoke([
        HumanMessage(content=f"""以下の回答は十分ですか？「十分」か「不十分」の一個だけ答えてください。回答 
                     ：{state['answer']}""")
    ])
    if "不十分" in response.content:
        return "retry"
    return "end"

# グラフの組み立て
graph_builder2 = StateGraph(State2)
graph_builder2.add_node("generate", generate_node)
graph_builder2.add_node("check", check_node)

graph_builder2.set_entry_point("generate")
graph_builder2.add_edge("generate", "check")

# 条件分岐のエッジ
graph_builder2.add_conditional_edges(
    "check",
    should_retry,
    {
        "retry": "generate", # 不十分ならgenerateに戻る
        "end": END,
    }
)

graph2 = graph_builder2.compile()

result2 = graph2.invoke({
    "question": "量子コンピュータとは何ですか？",
    "answer": "",
    "retry_count": 0,
})

print("\n=== 最終回答 ===")
print(result2["answer"])