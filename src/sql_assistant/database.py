import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = "data/sales.db"

def create_database():
    """SQLiteのDBを作成してダミーデータを投入する"""
    import os
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # テーブル作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARI KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price INTEGER NOT NULL
        )        
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            revenue INTEGER NOT NULL,
            sale_date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # 商品データ
    products = [
        (1, "りんご", "果物", 500),
        (2, "みかん", "果物", 300),
        (3, "ぶどう", "果物", 1200),
        (4, "にんじん", "野菜", 200),
        (5, "じゃがいも", "野菜", 150),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)",
        products
    )

    ## 売上データ（過去３ヶ月分）
    random.seed(42)
    sales = []
    for i in range(100):
        product_id = random.randint(1, 5)
        quantity = random.randint(1, 20)
        price = products[product_id - 1][3]
        revenue = quantity * price
        days_ago = random.randint(0, 90)
        sales_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        sales.append((i + 1, product_id, quantity, revenue, sales_date))

    cursor.executemany(
        "INSERT OR IGNORE INTO sales VALUES(?, ?, ?, ?, ?)",
        sales
    ) 

    conn.commit()
    conn.close()
    print("DBを作成しました")

def get_schema() -> str:
    """テーブルのスキーマ情報を返す"""
    return """
テーブル： products
- id: INTEGER（主キー）
- name: TEXT（商品名）
- category: TEXT（カテゴリ：果物/野菜）
ーprice: INTEGER（単価）

テーブル： sales
- id: INTEGER（主キー）
- product_id: INTEGER（外部キー -> products.id）
- quantity: INTEGER（販売数量）
- revenue: INTEGER（売上金額）
-sale_date: TEXT（販売日 YYYY-MM-DD形式）
"""

def run_query(sql: str) -> str:
    """SQLを実行して結果を文字列で返す"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        if not rows:
            return "結果が０件でした"
        
        # 結果を文字列に変換
        result = ", ".join(columns) + "\n"
        for row in rows:
            result += ",".join(str(v) for v in row) + "\n"
        return result
    
    except Exception as e:
        return f"SQLエラー：{e}"
    
if __name__ == "__main__":
    create_database()