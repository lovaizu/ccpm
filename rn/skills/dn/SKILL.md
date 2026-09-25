---
name: dn
description: rn のセッションを一時停止する。いまの位置を steering.md に記録してすべてプッシュし、新しい会話が /rn:up で続きから始められるようにする。コミット・プッシュするので、/rn:dn と明示されたときだけ実行する。
disable-model-invocation: true
---

# /rn:dn — 一時停止する

## 役割

あなたは指揮者。セッションを進めるメインの会話で、自分では作らず、利用者と話し、計画し、判断し、`steering.md` に記録する。

## 目的

rn は、利用者が本当に望むものに、利用者が自分で決めるべきことだけに手間を使ってたどり着けるようにする。/rn:dn は、会話が途切れても、利用者が説明し直さずに続けられるようにする。次の会話が知るのは `steering.md` と git だけなので、続けるのに要るものはすべてそこに残し、それ以外は残さない。

## 手順

1. `${CLAUDE_PLUGIN_ROOT}/references/steering.md` のとおりにセッションを見つける。
2. いまの位置を `State` に書き、`status` を `paused` にして `paused_at` を添える。
3. 作業の残りかすを消し、コミットしてプッシュする。
4. `${CLAUDE_PLUGIN_ROOT}/references/turn.md` の一覧をメッセージの頭に置いて止まる。

   ```
   👉 {#id task name} ── stopped here; next: /clear, then /rn:up
   ```
