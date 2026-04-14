# ===========================
# 1. 型ヒント (Type Hints)
# ===========================

# 型ヒントなし（古いスタイル）
def greet_old(name):
    return "こんにちは、" + name

# 型ヒントあり（モダンスタイル）
def greet(name: str) -> str:
    return f"こんにちは、{name}"

# リスト・辞書にも型をつけられる
def summarize(texts: list[str]) -> dict[str, int]:
    return {text: len(text) for text in texts}

# Optional:Noneになりうる値
def find_user(user_id: int) -> str | None:
    users = {1:"Hayato", 2: "Taro"}
    return users.get(user_id) # 見つからなければNoneを返す


# ===========================
# 2. dataclass
# ===========================
from dataclasses import dataclass

@dataclass
class ChatMessage:
    role: str
    content: str

@dataclass 
class ChatResponse:
    message: ChatMessage
    model: str
    tokens_used: int


# ===========================
# 3. 非同期処理（async/await）
# ===========================
import asyncio

async def fetch_response(question: str) -> str:
    # 実際はここでAPIを叩く。今は擬似的に待機
    await asyncio.sleep(1) # １秒待つ（API呼び出しのシミュレーション）
    return f"「{question}」への回答です"

async def main():
    import time
    start = time.time()
    # ３つの質問を同時に投げる
    questions = ["質問１", "質問２", "質問３"]
    tasks = [fetch_response(q) for q in questions]
    results = await asyncio.gather(*tasks)
    for result in results:
        print(result)

    print(f"実行時間：{time.time() - start:.2f}秒")

if __name__ == "__main__":
    print(greet("Hayato"))
    print(summarize(["hello", "world", "python"]))
    print(find_user(1))
    print(find_user(99))

    msg = ChatMessage(role="user", content="こんにちは")
    print(msg)
    print(msg.role)
    print(msg.content)

    res = ChatResponse(
        message=msg,
        model="claude-haiku-4-5-20251001",
        tokens_used=10
    )
    print(res)

    asyncio.run(main())