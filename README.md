## 設計判断ログ

### 2026-04-13 Claude API 初接続

#### なぜこの構成を選んだか
- anthropic SDKを直接使う（LangChain未使用）
- 理由：まずAPIの素の挙動を理解するため。抽象化されたフレームワークより先に生のAPIを触っておくと、後でLangChainを使ったときに「何をラップしているか」が分かる

#### 使ったもの
- anthropic==0.94.1
- python-dotenv（.envからキー読み込み）

#### 次にやること
- streamingレスポンスを試す
- function callingを試す

## 学習ログ

### 2026-04-14 Pythonモダン構文

#### やったこと
- 型ヒント（Type Hints）
- dataclass
- 非同期処理（async/await）

#### 学んだこと
- 型ヒントは実行時にエラーを出すわけではなく、可読性と補完のための宣言
- dataclassは「データを入れるだけのクラス」を楽に書くための仕組み。`__init__` が自動生成される
- 非同期処理で3つのAPI呼び出しを同時に実行すると、3秒→1秒になった

#### 設計判断
- `str | None` で返り値がNoneになりうることを明示 → 呼び出し側がNoneチェックを意識できる
- dataclassのタイポはすぐエラーで気づける → 辞書より安全

#### 次にやること
- LangChain基礎（LCEL・PromptTemplate・OutputParser）