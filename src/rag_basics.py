from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")

# 1．Embeddingモデルの定義（テキスト　→ ベクトルに変換する）
embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-small"
)

# 2．サンプルドキュメント（社内FAQを想定）
documents = [
    Document(page_content="有給休暇は年間20日付与されます。入社6ヶ月後から取得可能です。"),
    Document(page_content="リモートワークは週3日まで可能です。申請は前日までに行ってください。"),
    Document(page_content="経費精算はMoneyForwardで行います。領収書は30日以内に提出してください。"),
    Document(page_content="健康診断は毎年6月に実施されます。受診は全社員必須です。"),
    Document(page_content="通勤交通費は月額上限3万円まで支給されます。"),
]

# 3．ChromaDBにドキュメントを保存
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
)

# print("ドキュメントを保存しました")
# print(f"保村件数： {vectorstore._collection.count()}")

# 4．検索してみる
retriever = vectorstore.as_retriever(search_kwargs={"k": 2}) # 上位２件を取得
# query = "リモートワークのルールを教えてください"
# docs = retriever.invoke(query)

# print(f"\n検索クエリ: {query}")
# print("---")
# for doc in docs:
#     print(doc.page_content)
#     print("---")

# 5．RAGチェーンを組み立てる
prompt = ChatPromptTemplate.from_messages([
    ("system", """以下のコンテキストを参考に質問に答えてください。
コンテキストに情報がない場合は「情報が見つかりませんでした」と答えてください。

コンテキスト:
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

# 6．質問してみる
questions = [
    "リモートワークは何日までできますか？",
    "有給休暇は何日もらえますか？",
    "社員旅行はいつですか？",  # ← ドキュメントにない情報
]

for q in questions:
    print(f"\n質問: {q}")
    print(f"回答: {rag_chain.invoke(q)}")
    print("---")