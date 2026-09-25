---
name: ty
description: rn のセッションが止まって待っている判断（計画・設計の選択・完成物）を承認し、記録して止まる。コミット・プッシュし、最後のサインオフではプルリクエストをレビュー可能にするので、/rn:ty と明示されたときだけ実行する。
disable-model-invocation: true
---

# /rn:ty — 承認する

## 目的

利用者は、セッションが止まって待っていたものを承認した。もう聞き直さずにそこから進めるよう、承認を `steering.md` に記録して止まる。

## 手順

1. `${CLAUDE_PLUGIN_ROOT}/references/steering.md` のとおりにセッションを見つける。
2. `Next` のサインオフにチェックを入れ、`Next` をその先へ進める。
3. Design sign-off なら、選んだもの（`$ARGUMENTS` が名指すもの、なければ自分のおすすめ）を `Assumptions` に Fact として書く。
4. Evaluation sign-off なら、セッションは終わる。`evaluations/` を消し、`gh pr ready` でプルリクエストをレビュー可能にする。
5. コミットしてプッシュし、利用者の言語で伝えて止まる。

   ```
   ● Approved: {sign-off name}. Next: /clear, then /rn:up — or say "go on" to continue here.
   ```

   Evaluation sign-off では代わりに、セッションが終わったこと、マージは利用者のものであること、マージ待ちとして `Notes` にあることを伝える。
