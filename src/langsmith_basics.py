from langchain_anthropic import ChatAnthropic
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# LangSmithはenv変数を読み込むだけで自動でトレースが有効になる
# LANGCHAIN_TRACING_V2=true をセットしているので追加コードは不要

# --- RAGの準備（rag_basics.pyと同じ）---
embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-small"
)

documents = [
    Document(page_content="有給休暇は年間20日付与されます。入社6ヶ月後から取得可能です。"),
    Document(page_content="リモートワークは週3日まで可能です。申請は前日までに行ってください。"),
    Document(page_content="経費精算はMoneyForwardで行います。領収書は30日以内に提出してください。"),
    Document(page_content="健康診断は毎年6月に実施されます。受診は全社員必須です。"),
    Document(page_content="通勤交通費は月額上限3万円まで支給されます。"),
]

vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")

prompt = ChatPromptTemplate.from_messages([
    ("system", """以下のコンテキストを参考に質問に答えてください。
     コンテキストに情報がない場合は「情報が見つかりませんでした」と答えてください。
     
     コンテキスト：
     {context}"""),
     ("human", "{question}"),
])

def format_docs(docs):
    return "\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# --- 複数の質問を投げてトレースを確認 ---
questions = [
    "リモートワークは何日までできますか？",
    "有給休暇は何日もらえますか？",
    "経費精算の期限はいつですか？",
    "社員旅行はいつですか？",
]

for q in questions:
    print(f"\n質問: {q}")
    result = rag_chain.invoke(q)
    print(f"回答: {result}")