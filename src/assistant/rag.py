from langchain_anthropic import ChatAnthropic
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

def build_rag_chain():
    """RAGチェーンを構築して返す"""

    # 1．ドキュメントの読み込み
    loader = TextLoader("docs/faq.md", encoding="utf-8")
    documents = loader.load()

    #2．チャンク分割
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20,
    )
    chunks = splitter.split_documents(documents)
    print(f"チャンク数: {len(chunks)}")

    #3．Embeddingsとベクトルストア
    embeddings = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-small"
    )
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    #4．LLMとプロンプト
    llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
    prompt = ChatPromptTemplate.from_messages([
        ("system", """あなたは社内FAQアシスタントです。
        以下のコンテキストを参考に質問に答えてください。
        コンテキストに情報がない場合は「その情報は見つかりませんでした。人事部門にお問い合わせください。」と答えてください。

        コンテキスト:
        {context}"""),
        ("human", "{question}"),
    ])

    #5．RAGチェーン
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain,retriever

def format_docs(docs):
    return "\n".join(doc.page_content for doc in docs)