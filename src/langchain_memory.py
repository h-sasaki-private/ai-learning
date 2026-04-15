from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
parser = StrOutputParser()

prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたは親切なアシスタントです。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

chain = prompt | llm | parser

# 会話履歴を手動で管理
history = []

def chat(question: str) -> str:
    result = chain.invoke({
        "history": history,
        "question": question,
    })
    # 履歴に追加
    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=result))
    return result

# 会話してみる
print(chat("私の名前はHayatoです"))
print("---")
print(chat("私の名前を覚えていますか？"))
print("---")
print(chat("私の名前を使って俳句を作ってください"))