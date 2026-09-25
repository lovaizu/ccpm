# 利用者の次の判断までセッションを進める

判断が利用者のものになるまで、セッションは利用者なしで進む。1つのエージェントが作り、別のエージェントが `viewpoints.md` に照らして評価し、あなた（メインの会話）がゴールに照らして次の一手を決める。`steering.md` を持つのはあなたで、自分の文脈は判断のために取っておく。次の会話が知るのは `steering.md` と git だけなので、判断はすべてそこに書く。

## 1ターン

`Next` のタスクを取る。サインオフなら利用者の判断なので、止まる。それ以外は `Agent` で新しいエージェントを立て、`steering.md` のパス、タスクの id、`${CLAUDE_PLUGIN_ROOT}/references/viewpoints.md`（Task result）を渡す。やり直しなら評価も渡す。エージェントは作業をコミット・プッシュし、`steering.md` はあなたに任せ、コミットを返す。それを評価させて、判断する。

## 評価させる

`Agent` で新しい general-purpose のエージェントを立てる。渡すのは `${CLAUDE_PLUGIN_ROOT}/references/evaluate.md`、種類（Plan・Design choice・Task result・Finished work）、`steering.md` のパス、Task result ならタスクの id とコミット、そして評価を書くファイル `evaluations/{NN}-{plan | design-{id} | task-{id} | finished-work}.md`（`{NN}` は `01` から数える）。それ以外は渡さない。あなたの理由は、評価をあなたの見方に引き寄せてしまうからだ。評価をコミットしてプッシュする。

## 判断する

ゴールに照らして、受け入れる、More を渡してやり直させる、直す、利用者のために止まる、のどれかにする。同じやり方で届かないことが続くとき、利用者が承認したものを変えることになるときは、利用者が選ぶことだ。Design sign-off を次のタスクとして足し、まだ終わっていないタスクは選択の前の計画として `Notes` に移す。一手を `steering.md` に書き、コミット・プッシュし、1行で見せる。

```
● {#id task name | plan | design choice | finished work} ── evaluated: {passes | fails ({the deciding More})} → {next move}
```

## 利用者のために止まる

利用者が判断するものは、先に評価させておく。計画、Design sign-off の選択肢（それぞれの費用と得るもの、おすすめを添え、リポジトリが設計を置く場所に書いて `design` に記すか、サインオフのタスクの中に書く）、完成物だ。コミット・プッシュし、利用者の言語で、メッセージの頭に一覧を置く。

```
── {slug}: {the Goal in one line} ──
✅ {#id task name / …}
👉 {#id sign-off name} ── {what you need from the user}
⬜ {#id task name / …}
({what happens after this stop})

Draft PR: {url}
```

プルリクエストで読んでもらうよう、おすすめを添えて頼む。返事は `/rn:ty`（おすすめ以外を選ぶなら `/rn:ty <choice>`）か `/rn:gm <feedback>` だ。

## 利用者が判断した後

`/rn:up` は `Next` から進める。設計が選ばれた後は、それに沿ったタスクを書き、計画を評価させる。`Feedback` があれば、止まっていたものを評価が通るまで直す。計画や選択肢は自分で、完成物は新しいタスクで直す。それから、フィードバックの元になったプルリクエストの各スレッドに、何を変えたかとコミットを、コメントの言語で返信する。解決するのは利用者に任せる。そして `Feedback` を none にする。
