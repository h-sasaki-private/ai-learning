from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")

# 1．Toolの定義（@toolでコレーたをつけるだけ）
@tool
def calculate(expression: str) -> str:
    """数式を計算します。例：'2 + 3 * 4'"""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"起算エラー： {e}"
    
@tool
def get_sales_data(product: str) -> str:
    """商品の売り上げデータを取得します。"""
    # 実際はDBから取得するが、今回はダミーデータ
    sales_data = {
        "りんご": {"sales": 150, "revenue": 75000},
        "みかん": {"sales": 200, "revenue": 60000},
        "ぶどう": {"sales": 80, "revenue": 96000},
    }
    if product in sales_data:
        data = sales_data[product]
        return f"{product}の売上: {data['sales']}個, 売上金額: {data['revenue']}円"
    return f"{product}のデータが見つかりませんでした"

@tool
def run_sql(query: str) -> str:
    """SQLクエリを実行して結果を返します。
    使用例：run_sql("SELECT SUM(revenue) FROM sales")
    salesテーブルにはrevenue（売上金額）カラムがあります。
    """
    print(f"[run_sql] 実行クエリ: {query}")
    # 実際はDBに接続するが、今回はダミー
    dummy_results = {
        "SELECT * FROM products WHERE category = 'fruit'":
            "id=1, name=りんご, price=500\nid=2, name=みかん, price=300\nid=3, name=ぶどう, price=1200",
        "SELECT SUM(revenue) FROM sales":
            "SUM(revenue) = 231000",
    }
    for key in dummy_results:
        if "sum(revenue)" in query.lower():
            return dummy_results["SELECT SUM(revenue) FROM sales"]
        if key.lower() in query.lower():
            return dummy_results[key]
        return "クエリを実行しました。結果: 0件"
    
# 2．エージェントの作成
tools = [calculate, get_sales_data, run_sql]
agent = create_react_agent(llm, tools)

# 3．実行
questions = [
    "りんごとみかんの売上個数の合計を計算してください",
    "全商品の売上金額の合計をSQLで取得してください",
]

for question in questions:
    print(f"\n質問: {question}")
    result = agent.invoke({"messages": [("human", question)]})
    print(f"回答: {result['messages'][-1].content}")
    print("---")