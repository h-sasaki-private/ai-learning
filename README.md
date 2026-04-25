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

### 2026-04-15 FastAPIでRAGをAPI化

#### やったこと
- FastAPI + uvicornでAPIサーバーを構築
- POST /chat エンドポイントを実装
- curlでリクエストを送ってJSONレスポンスを確認
- FastAPIの自動生成ドキュメント（/docs）を確認

#### 学んだこと
- FastAPIは「APIの設計図」を書くフレームワーク。uvicornが実際にサーバーとして起動する
- `@app.post("/chat")` はデコレータ。この関数をPOSTエンドポイントとして登録するという意味
- BaseModelはPydanticのクラス。dataclassと違い実行時にも型を検証する。APIの入力バリデーションに最適
- `uv run uvicorn src.api:app --reload` の `--reload` はコード変更時に自動再起動するオプション
- FastAPIは `/docs` にアクセスするだけでAPIドキュメントを自動生成してくれる

#### 疑問と回答
- Q: BaseModelとdataclassの違いは？
  → A: dataclassは型宣言のみ。BaseModelは実行時にも型を検証してくれる。JSON変換も自動でやってくれるのでAPIのリクエスト・レスポンス定義に最適
- Q: 実行コマンドが今までと違う理由は？
  → A: 今までは「スクリプトを1回実行して終わり」。今回は「リクエストを待ち続けるサーバーとして起動する」ので書き方が変わる

#### 設計判断
- `response_model=ChatResponse` をエンドポイントに指定
  - 理由：レスポンスの型を明示することでAPIドキュメントに自動反映される。クライアントとの仕様共有が楽になる
  - トレードオフ：型定義の手間が増えるが、大きいプロジェクトでは必須

#### 🎯 Month 1 マイルストーン達成！
ローカルで動くRAG APIサーバー（FastAPI + ChromaDB + HuggingFace Embedding）の完成

#### 次にやること
- Month 2：LangGraph基礎（StateGraph・Node・Edge）

### 2026-04-15 LangGraph基礎

#### やったこと
- StateGraph・Node・Edgeの基本構造を理解
- 2ノードのシンプルなグラフを実装（think → answer）
- 条件分岐・ループのあるグラフを実装（generate → check → 分岐）

#### 学んだこと
- LangChainは一本道のパイプライン。LangGraphは条件分岐・ループ・複数エージェントが絡み合う複雑なワークフローをグラフで表現できる
- State：グラフ全体で共有するデータ。各ノードがStateを受け取って更新して次のノードに渡す
- Node：実際の処理をする関数。Stateを受け取ってStateを返す
- Edge：ノード間のつながり。`add_edge` で固定の流れ、`add_conditional_edges` で条件分岐を定義する
- `should_retry` のような条件分岐関数は文字列を返す。その文字列と辞書のキーが対応して次のノードが決まる
- `retry_count` をStateで管理することで無限ループを防げる

#### 疑問と回答
- Q: retryしたときどのノードに戻るか？
  → A: `add_conditional_edges` の辞書で定義する。`"retry": "generate"` なら generateノードに戻る
- Q: retry_countが増えていなかった原因は？
  → A: `retry_cpunt` というタイポ。新しいキーとして保存されてしまい `retry_count` が更新されなかった。Stateのキー名は一字一句正確に書く必要がある

#### 設計判断
- `retry_count >= 2` で強制終了する条件を入れた
  - 理由：LLMの判断は不安定なので「不十分」が続いて無限ループになるリスクがある
  - トレードオフ：本当に不十分な回答でも2回で打ち切ってしまう

#### 次にやること
- Tool実装 + Function Calling（Web検索・SQL実行ツールをエージェントに持たせる）

### 2026-04-16 Tool実装 + Function Calling

#### やったこと
- `@tool` デコレータでToolを定義（calculate・get_sales_data・run_sql）
- `create_react_agent` でReActエージェントを作成
- エージェントが自律的にToolを選んで実行することを確認
- `print()` でToolに渡された引数をデバッグ

#### 学んだこと
- `@tool` をつけるだけで関数がToolになる。docstringがエージェントの判断材料になるので説明は具体的に書く
- ReActはReasoning（推論）とAction（行動）の繰り返し。「どのToolを使うか」をLLMが自律的に判断する
- エージェントが生成するSQLは毎回微妙に違う（`AS total_revenue` がついたりする）。ダミーデータとの完全一致に頼らず柔軟なマッチングが必要
- `print()` をToolの中に入れるとエージェントが何を実行しているか可視化できる

#### 疑問と回答
- Q: Toolを定義することでどんなことができるようになる？
  → 下記参照

#### Toolでできること（可能性）
LLM単体では「知識の範囲内でしか答えられない」が、Toolを持たせることで外部の情報・処理を使えるようになる。

| Tool例 | できること |
|---|---|
| Web検索Tool | 最新情報を取得して回答（ニュース・株価など） |
| SQL実行Tool | DBのデータをもとに回答（売上・在庫など） |
| API呼び出しTool | Slack通知・カレンダー登録・メール送信など |
| ファイル操作Tool | PDFを読む・CSVを集計・レポートを生成 |
| コード実行Tool | Pythonコードを書いて実行・グラフを生成 |
| RAG検索Tool | 社内ドキュメントを検索して回答 |

勇斗さんのSQL・BI知識と組み合わせると「自然言語でBIクエリを生成・実行・可視化まで自動でやるエージェント」が作れる。これがMonth 3の個人開発②（SQL生成AIツール）に直結する。

#### 設計判断
- docstringに使用例とテーブル構造を明記した
  - 理由：エージェントが正しいSQLを生成するための文脈を与えるため
  - トレードオフ：docstringが長くなるとトークン消費が増える
- `sum(revenue)` の部分一致でダミーデータをマッチングした
  - 理由：エージェントが生成するSQLは毎回微妙に違うため完全一致では動かない
  - 本番：実際のDB接続に置き換えれば問題なし

#### 次にやること
- LangSmithでデバッグ・評価

### 2026-04-21 LangSmithでデバッグ・評価

#### やったこと
- LangSmithのアカウント作成・APIキー発行
- .envにトレース設定を追加（LANGCHAIN_TRACING_V2=true）
- RAGチェーンのトレースをLangSmith UIで確認
- 処理の流れ・トークン消費量・検索されたドキュメントを可視化

#### 学んだこと
- LangSmithはenv変数をセットするだけで自動でトレースが有効になる。追加コードは不要
- トレースUIで「RunnableSequence → VectorStoreRetriever → ChatAnthropic」の階層構造が可視化される
- 経費精算の質問に対して有給休暇のドキュメントが混入していた → k=2で関係ないドキュメントが入るRAGの精度問題を発見できた
- LangSmithがないとこういう問題に気づけない。print()デバッグの限界

#### LangSmithでよく見る情報
- **Latency**：どのステップが遅いかボトルネック特定。ChatAnthropicがほぼ支配的
- **トークン消費量・コスト**：プロンプト最適化の指標。本番で1日1000回呼ばれるとコストが変わる
- **Retrieverの検索結果**：関係ないドキュメントが混入していないか確認。RAG精度改善の起点
- **LLMへの入力プロンプト全文**：「なぜこの回答になったか」を追う。プロンプト改善の起点
- **Feedback**：👍👎で回答を評価して蓄積。「精度改善しました」の根拠になる

#### 設計判断
- LANGCHAIN_PROJECT=ai-learning でプロジェクトを分けた
  - 理由：複数のプロジェクトのトレースが混在しないようにするため
  - 本番：クライアントごとにプロジェクトを分けると管理しやすい

#### 副業案件での使い方
クライアントから「たまに変な回答が返ってくる」と言われたとき：
1. LangSmithで該当トレースを探す
2. Retrieverで関係ないドキュメントが検索されていないか確認
3. kの値・Embeddingモデル・チャンクサイズを調整
4. 「原因はこれで、こう改善しました」と説明できる

「動くだけ」でなく「説明できる」エンジニアになれるのがLangSmithの価値。

#### 次にやること
- 個人開発①: BtoB向けAIアシスタント（RAG + LangGraph）

### 2026-04-21 個人開発①: BtoB向けAIアシスタント

#### 作ったもの
社内FAQ AIアシスタント（RAG + LangGraph + FastAPI）

#### 構成
- src/assistant/
  - rag.py    → ドキュメント読み込み・チャンク分割・RAGチェーン構築
  - graph.py  → LangGraphのワークフロー定義
  - api.py    → FastAPIのエンドポイント
- docs/
  - faq.md    → 社内FAQドキュメント

  #### やったこと
- docs/faq.mdを読み込んでチャンク分割してChromaDBに保存
- LangGraphで「回答生成 → 評価 → リトライ」のワークフローを実装
- FastAPIで POST /chat・GET /health エンドポイントを実装
- curlでリクエストを送って動作確認

#### 学んだこと
- TextLoaderでMarkdownファイルを読み込める
- RecursiveCharacterTextSplitterでチャンク分割。chunk_size=200で社内FAQのような短いドキュメントに適切なサイズ
- `is_sufficient = "不十分" not in response.content` でLLMの評価結果をboolに変換できる
- /health エンドポイントは本番運用で必須。サーバーが生きているか確認するため
- バグの原因はstate['answer']がstate['question']になっていたタイポ。LangSmithのトレースで発見できた

#### 疑問と回答
- Q: なぜretry_count >= 2で強制終了？
  → A: LLMの評価は不安定なので無限ループを防ぐため。本番では閾値をチューニングする
- Q: /healthエンドポイントは何に使う？
  → A: 本番運用でロードバランサーやDockerがサーバーの死活監視に使う。副業案件でも必ず求められる

#### 設計判断
- build_rag_chain()とbuild_graph()を関数化した
  - 理由：FastAPI起動時に1回だけ実行されるようにするため。リクエストのたびに初期化すると遅い
  - トレードオフ：メモリに常駐するがRAGの応答速度が上がる
- chunk_size=200・chunk_overlap=20に設定
  - 理由：FAQのような短い文書は小さいチャンクの方が検索精度が高い
  - トレードオフ：チャンクが小さすぎると文脈が失われることがある

#### 🎯 Month 2 マイルストーン達成！
GitHubに公開したLangGraphエージェント（RAG + LangGraph + FastAPI）の完成

#### 次にやること
- Month 3：個人開発②（SQL生成AIツール）・Zenn記事・案件獲得

#### やったこと
- SQLiteでproducts・salesテーブルを作成してダミーデータを投入
- LangGraphで「SQL生成 → SQL実行 → エラーならリトライ → 回答生成」のワークフローを実装
- FastAPIで POST /query・GET /health エンドポイントを実装
- 「売上金額が一番高い商品は？」という自然言語の質問からSQLを生成して回答できることを確認

#### 学んだこと
- SQLiteはファイルベースのDB。サーバー不要で `.db` ファイル1つがそのままDBになる
- `os.makedirs("data", exist_ok=True)` でディレクトリを作成。`exist_ok=True` で既存でもエラーにならない
- `random.seed(42)` で乱数を固定するとテストデータが毎回同じ順番で生成される
- `INSERT OR IGNORE` で主キーが重複する場合はスキップ。`create_database()` を何度実行しても重複データが入らない
- `strip()` で文字列前後の空白・改行を除去。`replace()` でコードブロック（\`\`\`sql）を除去してSQLをクリーンにする
- LLMが生成するSQLは毎回微妙に違う（`products_id` → `product_id` など）。エラーメッセージをプロンプトに含めてリトライすることで自己修正できる

#### 疑問と回答
- Q: SQLiteと本番DBの違いは？
  → A: SQLiteはファイルベースでサーバー不要。本番ではPostgreSQLに切り替えるだけでコードはほぼ変わらない
- Q: レスポンスにsqlとquery_resultを含める理由は？
  → A: クライアントが「どんなSQLが生成されたか」をレビューできるようにするため。副業案件でも「AIが生成したSQLを人間がレビューできるようにしてほしい」という要件はよく来る

#### 設計判断
- エラー時にエラーメッセージをプロンプトに含めてSQL再生成する
  - 理由：LLMがエラー内容を見て自己修正できる。今回も `products_id` → `product_id` に自動修正できた
  - トレードオフ：リトライ回数が増えるとレイテンシとコストが上がる
- error_count >= 2 で強制終了
  - 理由：無限ループを防ぐため
  - トレードオフ：複雑なSQLは2回では修正しきれないことがある

#### 🎯 Month 3 個人開発② 完了！

#### 次にやること
- Zenn記事①: SQL生成AIツール解説
- Zenn記事②: Claudeと学ぶAIエンジニアリング