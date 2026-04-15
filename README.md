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

### 2026-04-15 LangChain基礎

#### やったこと
- LCEL（LangChain Expression Language）でチェーンを組む
- PromptTemplate で変数付きプロンプトを作る
- StrOutputParser で文字列として受け取る
- JsonOutputParser でdict形式として受け取る

#### 学んだこと
- LangChainはLLMを使ったアプリを作るためのフレームワーク。APIの呼び出し・プロンプト管理・出力整形・RAG・エージェントをまとめて提供している
- LCELは `prompt | llm | parser` のパイプライン構造。Unixのパイプと同じ発想
- JSONはデータのフォーマット（文字列）、dictはPythonのデータ型。JsonOutputParserがJSON文字列をdictに変換してくれる

#### 設計判断
- OutputParserをStrとJsonで使い分ける → 文字列で返すだけでいいときはStr、FastAPIのレスポンスに使うときはJson
- `chain.invoke()` に渡す辞書を変えるだけで違う質問ができる → テンプレートを再利用できる

#### 感想
JSONの扱い方は他の言語と近いなと感じた。連想配列で受け取ってやり取りする感じなど。チェーンを組むのはパイプラインだと思えばわかりやすい気がするが、実際に自分で書くとなった際にうまくできるかは不安

#### 次にやること
- LangChain応用（Memory・会話履歴）