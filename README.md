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