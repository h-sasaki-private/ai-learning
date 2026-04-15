from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# １．LLM（モデル）の定義
llm = ChatAnthropic(model="claude-haiku-4-5-20251001")

# 2．プロンプトテンプレートの定義
prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたは{language}の専門家です。簡潔に答えてください。"),
    ("human", "{question}"),
])

# 3．OutputParser（出力を文字列に変換）
parser = StrOutputParser()

#  4．チェーンを組み立てる
chain = prompt | llm | parser

# 5．実行
# result = chain.invoke({
#     "language": "Python",
#     "question": "型ヒントを使うメリットを一言で教えてください。"
# })

# print(result)

# 6．複数の質問をまとめて実行
# questions = [
#     {"language": "Python", "question": "非同期処理を一言で説明してください"},
#     {"language": "SQL", "question": "インデックスを一言で説明してください"},
#     {"language": "React", "question": "useStateを一言で説明してください"},
# ]

# for q in questions:
#     result = chain.invoke(q)
#     print(f"[{q['language']}] {result}")
#     print("---")

# JSON形式で返すチェーン
json_prompt = PromptTemplate.from_template("""
以下の技術用語をJSON形式で説明してください。

技術用語: {term}

以下のJSON形式で返してください:
{{
    "term": "用語名",
    "summary": "一言説明",
    "use_case": "具体的な使用例"
}}

JSONのみ返してください。
""")

json_parser = JsonOutputParser()
json_chain = json_prompt | llm | json_parser

result = json_chain.invoke({"term": "RAG"})
print(result)
print(type(result)) # 型を確認
print(result["summary"]) # 辞書としてアクセスできる