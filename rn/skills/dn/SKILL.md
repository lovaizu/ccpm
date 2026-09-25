---
name: dn
description: rn のセッションを一時停止する。いまの位置を steering.md に記録してすべてプッシュし、新しい会話が /rn:up で続きから始められるようにする。コミット・プッシュするので、/rn:dn と明示されたときだけ実行する。
disable-model-invocation: true
---

# /rn:dn — 一時停止する

## 目的

この会話はもうすぐ終わる。次の会話が知るのは `steering.md` と git だけなので、続けるのに要るものはすべてそこに残し、それ以外は残さない。

## 手順

1. `${CLAUDE_PLUGIN_ROOT}/references/steering.md` のとおりにセッションを見つける。
2. いまの位置を `State` に書き、`status` を `paused` にして `paused_at` を添える。
3. 作業の残りかすを消し、コミットしてプッシュする。
4. `${CLAUDE_PLUGIN_ROOT}/references/turn.md` の一覧をメッセージの頭に置いて止まる。

   ```
   👉 {#id task name} ── stopped here; next: /clear, then /rn:up
   ```
