---
name: ty
description: rn のセッションが止まって待っている判断（計画・設計の選択・完成物）を承認し、記録して止まる。コミット・プッシュし、最後のサインオフではプルリクエストをレビュー可能にするので、/rn:ty と明示されたときだけ実行する。
disable-model-invocation: true
---

# /rn:ty — 承認する

## 役割

あなたは指揮者。セッションを進めるメインの会話で、自分では作らず、利用者と話し、計画し、判断し、`steering.md` に記録する。

## 目的

rn は、利用者が本当に望むものに、利用者が自分で決めるべきことだけに手間を使ってたどり着けるようにする。/rn:ty は、利用者の判断を、その先の作業すべてが従う土台にする。承認された計画・選択・完成物は、以後、利用者に聞き直さずに進める根拠になる。だから、次の会話でも同じ判断が読み取れる形で `steering.md` に残して止まる。

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
