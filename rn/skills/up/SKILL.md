---
name: up
description: 新しい会話で rn のセッションを再開する。古い版のセッションは今の版に合わせ、記録された利用者の返事に応え、利用者の次の判断まで作業を進める。ファイルを書き、コミット・プッシュし、プルリクエストに返信するので、/rn:up と明示されたときだけ実行する。
disable-model-invocation: true
---

# /rn:up — 再開する

## 目的

新しい会話が `steering.md` と git からセッションを引き取り、止まっていなかったかのように、利用者の次の判断まで進める。

## 手順

1. `${CLAUDE_PLUGIN_ROOT}/references/steering.md` のとおりにセッションを見つけ、前の版で始まったものなら今の版に合わせる。
2. 伝える。

   ```
   ● Resuming {slug} at #{id}: {task name}
   ```

3. `status` を `running` にし、`paused_at` を消す。
4. `${CLAUDE_PLUGIN_ROOT}/references/turn.md` の「利用者が判断した後」のとおりに進める。
