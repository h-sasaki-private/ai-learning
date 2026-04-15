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

### 2026-04-15 LangChain Memory・RAG基礎実装

#### やったこと
- LangChainのMemory（会話履歴の管理）
- ChromaDB（ベクトルDB）にドキュメントを保存
- HuggingFace Embeddingでローカルベクトル変換
- RAGチェーンを組み立てて質問応答

#### 学んだこと
- LLMは本来記憶を持たない。会話履歴をリクエストに毎回含めることで「覚えている」ように見せる
- ベクトルDBは意味の近さで検索する。通常のDBのキーワード検索とは根本的に仕組みが違う
- EmbeddingはAnthropicは提供していない。LLMはClaude・EmbeddingはOpenAI（今回はHuggingFace）という組み合わせが一般的
- RAGでコンテキストを渡すことでハルシネーションを防げる。ドキュメントにない情報は「見つかりませんでした」と答えさせられる
- LangChainは各LLMプロバイダー専用パッケージ（langchain-anthropic等）があるが、LCELの書き方は共通。llmの定義1行を変えるだけでモデルを切り替えられる
- HumanMessage/AIMessageは会話履歴を「誰の発言か」区別するクラス。内部ではrole: user/assistantに変換される
- `"""` はPythonの複数行文字列。長いプロンプトを書くときに使う
- `f""` はf文字列。`{}` の中に変数や式を埋め込める（PHPの `"{$name}"` に相当）
- Pythonの辞書はPHPの連想配列・JavaScriptのオブジェクト・JavaのMapと同じ概念
- `RunnablePassthrough()` は入力をそのまま次に渡す。質問文字列をプロンプトの `{question}` にそのまま渡すために使う

#### 疑問と回答
- Q: langchain_anthropicはAnthropic専用？他のLLM専用もある？
  → A: 各社専用パッケージがある（langchain-openai, langchain-google-genaiなど）。ただしLCELの書き方は共通なのでモデル切り替えが1行でできる
- Q: ChromaDBと通常のDBの違いは？
  → A: 通常DBはキーワード一致検索、ChromaDBは意味の近さ（ベクトル類似度）で検索する
- Q: EmbeddingにOpenAIを使う理由は？Anthropicではできない？
  → A: AnthropicはEmbedding APIを提供していない。今回はコスト削減のためHuggingFaceのローカルモデルを採用
- Q: `MessagesPlaceholder` は何をしている？
  → A: プロンプトの中に会話履歴を差し込む場所を定義している。invoke()時にhistoryリストがここに展開される

#### 設計判断
- OpenAIのEmbeddingの代わりにHuggingFaceのローカルモデル（multilingual-e5-small）を採用
  - 理由：コスト0・日本語対応・副業案件でも使われる構成
  - トレードオフ：初回モデルダウンロードが必要・OpenAIより若干精度が落ちるケースもある
- `k=2` で上位2件を取得
  - 理由：今回のドキュメント数が少ないため。本番では5〜10件が一般的

#### 次にやること
- FastAPIでRAGをAPI化（POST /chat エンドポイント）