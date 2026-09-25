---
name: gm
description: rn のセッションが止まって待っているもの（計画・設計の選択・完成物）に変更を求める。フィードバックは引数から、なければプルリクエストのレビューコメントから取り、記録して止まる。コミット・プッシュするので、/rn:gm と明示されたときだけ実行する。
disable-model-invocation: true
---

# /rn:gm — いいね、もっと

## 目的

利用者は、セッションが止まって待っていたものに、もっと望むことがある。直しが要約ではなく利用者の言ったことに答えるよう、フィードバックを利用者の言葉のまま丸ごと記録して止まる。

## 手順

1. `${CLAUDE_PLUGIN_ROOT}/references/steering.md` のとおりにセッションを見つける。
2. フィードバックは `$ARGUMENTS`。なければ、プルリクエストの未解決のレビュースレッドを、場所と URL つきで取る。解決済みかどうかは GraphQL でしか分からない。

   ```
   gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){reviewThreads(first:100){nodes{isResolved path line comments(first:20){nodes{url body}}}}}}}' -F o={owner} -F r={repo} -F n={number}
   ```

3. `Feedback` に書き足す。
4. コミットしてプッシュし、利用者の言語で伝えて止まる。

   ```
   ● Recorded: {n} points on {sign-off name}. Next: /clear, then /rn:up — or say "go on" to continue here.
   ```
