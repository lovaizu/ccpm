# rn

rn is a Claude Code plugin that makes what you ask for, ready for the people you make it for.

rn is for you when you have Claude Code make something in a GitHub repository for other people to
use. With it, you see what you asked for work early, and you decide only what's yours: you
correct one proposal of what it makes, and say how it works for you once you try it.

rn makes the first working slice of a request, and once you've tried it, grows it one addition
at a time, for each need you choose to make now.

## Non-goals

- rn doesn't put the deliverable in front of real people: you try it as they would, and its AI
  evaluators read it before you do.
- rn doesn't make all of your request at once: it makes the least that runs for the need you pick.
- rn doesn't make a small change faster than Claude Code alone: for a one-line fix, ask Claude Code.
- rn doesn't mark its pull request ready or merge it: it proposes the merge, and leaves both to
  you.

## Requirements

- macOS or Linux: `uname` shows it.
- Claude Code 2.1.328 or later: `claude --version` shows it.
- Python 3.9 or later, run as `python3`: `python3 --version` shows it.
- Git: `git --version` shows it.
- The GitHub command-line tool `gh`, logged in: `gh auth status` shows `Logged in to github.com`.
- A GitHub repository you can push to: at its root, `gh repo view --json viewerPermission` shows
  `WRITE`, `MAINTAIN`, or `ADMIN`.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install rn@ccpm
```

On the branch you want the work on, in Claude Code, `/rn:on` asks what it can help with. Where
that branch isn't one for the work, such as the default branch, rn asks you what to do first.

## Walkthrough

At the end, you hold a command that prints an invoice from your accounting team's statement, made
before anything else of the request.

This work is the one that rn's architecture draws, with its talk in Japanese. No end-to-end run of
this version records it yet. Your accounting team asks a developer for each invoice, and you
want them to print it themselves. At your repository's root in Claude Code, you type:

```text
/rn:on
```

rn shows:

```text
何をお手伝いしましょう？issueの番号でも、やりたいことの一言でも大丈夫です。
```

You type:

```text
経理チームが、Pythonを書かずに、明細から請求書を印刷できるコマンドがほしい
```

rn reads your repository, then shows what it would make, in one message:

```text
こう進めます。違うところだけ直してください。

ゴール：経理チームの方が、開発者に頼まずに、月末に自分で請求書を出せる
  ご依頼の「経理チームが、Pythonを書かずに、明細から請求書を印刷できるコマンドがほしい」から読みました

進め方：まず1を作ります（おすすめ）
  印刷できれば、経理チームの方が月末に自分で請求書を出せます
  1. 明細ファイルから、請求書を1枚印刷できる
  2. インボイス制度の記載事項を満たしている
  3. 発行者の情報を毎回入れなくて済む
  4. ガイドだけで使い始められる
  2から4は、1を試したあとに、今作るかissueに残すかをご相談します
  1の作り方：明細ファイルを渡すと、請求書を1枚印刷する invoice コマンド
  試して確かめること：経理チームの方が、説明だけを見て、明細から請求書を印刷できる

作るもの：新しく作るので、おおまかに次の3つです
  1. 請求書の型
  2. invoice コマンド
  3. 使い方の説明
  1はできた時点でお見せします（おすすめ）
  請求書の見た目は経理チームの方が決めることなので、コマンドより先に見ると手戻りが少なくなります

※仮に決めた点：使うのは経理チームの方（ご依頼の「経理チームが」から）

これで進めてよければ「OK」、直すところがあればその内容を入力してください。
```

You type `OK`. rn makes the invoice's template first, and shows it to you before anything rests
on it:

```text
請求書の型ができました。

見本の請求書で、見た目を確かめてください：

  見本の請求書.pdf

これで足りれば /rn:ty、変えたい点があれば /rn:gm に続けてその内容を入力してください。
```

You type `/rn:ty`. Each time a task is done, rn tells you what's left, and each change to the plan
with why, so you can say at once what's off:

```text
invoice コマンドができました。

残り：
- 使い方の説明を書く

計画の変更：明細の列が空のときのタスクを足しました。見本の明細に空の列があったためです。

お願いすることはありません。
```

Once AI evaluators have tried it as your accounting team would, rn hands it to you:

```text
試せるようになりました。

できること：明細ファイル1つから、請求書を1枚印刷する
まだしないこと：2から4
確かめること：説明だけを見て、明細から請求書を印刷できる

  invoice 見本の明細.csv

これで足りれば /rn:ty、変えたい点があれば /rn:gm に続けてその内容を入力してください。
```

You run it, and the printer gives one invoice with the customer, the lines, and the total. You
type `/rn:ty`. rn checks the pull request whole, then asks what happens to the needs not made
yet:

```text
PRの点検が通り、1ができました。

選ばなかった2から4を、どうしますか？

1. 2を今作り、3と4はissueに残す（おすすめ）
   2がないと、経理チームの方は請求書を月末にそのまま出せません
2. すべてissueに残す
```

You type `1`. rn grows the command to meet 2 the same way, one addition, and hands it to you
to try. Once you type `/rn:ty` again, it asks of 3 and 4, and you keep both in issues. rn shows:

```text
3と4をissueに残しました：https://github.com/lovaizu/playground/issues/39 、https://github.com/lovaizu/playground/issues/40

PRを「レビュー可」にしてから、マージしてください：https://github.com/lovaizu/playground/pull/38
```

You mark the pull request ready for review, and merge it.

## How it works

rn puts in your hands, early, the least that runs for the one need you pick.

### "I can't spell out every detail up front, so it builds the wrong thing."

You don't spell it out. rn reads your words, your issue and its earlier work, and your
repository, and proposes the goal it reads you're after, with the words of yours it rests on, the
way to it, and what it makes, marking what it had to assume. You correct only what's off, then try
what runs, and say what's off there.

### "Does it ask a lot of questions before anything starts?"

No. rn asks nothing that your request, your issue, or your repository already says. Where your
issue already says what you want, one proposal comes first, and once you agree, rn starts. A
request that leaves more open takes a few proposals, the goal first.

### "A question to it turns into a change."

No. rn answers a question with why, from what it planned and what it made, and changes nothing
until you ask for a change.

### "I see the parts only at the end, and the rework piles up."

No. rn names each thing it makes, the files where they exist, and asks which ones you want to see
as soon as they're made, recommending those whose rework would cost most later. rn waits for your
word on each before it makes what rests on it.

### "It builds the whole request before anything runs."

No. rn makes the least that runs, through every kind of deliverable it needs at once, and hands it
to you before it makes more.

### "Does it work in a language other than English?"

Yes. rn talks in your language and writes in your repository's, asking only where they disagree.

### "Does it show how far it has come?"

Yes. Each time a task is done, rn tells you what's left before you can try it, and each change to
the plan with why. It shows no count, as the tasks change while rn finds what the work takes.

### "Its output misses what this kind of work needs."

rn makes each deliverable by the best practice of its kind, such as one for a README, and meets
each of its necessary conditions, while what it makes stays the least.

### "It looks done, but the people it's for can't use it."

Before you see it, AI evaluators try each deliverable with only what its people have, never what
rn meant. Where they still find something after two tries, rn shows it to you in your terms and
asks whether to mend it now. Then you try it yourself.

### "Does it drop part of the request?"

No. Each need that you or the issue named stays on the list. Once you've tried what runs, rn
proposes for each one left whether to make it now or keep it in an issue.

### "Can rn's work stop and go on later?"

Yes. rn pushes its work to GitHub as it goes, so nothing stays only on your computer. `/rn:dn`
stops the work once what it's writing is whole, and `/rn:up` picks it up where it stopped, in any
conversation.

### "Can rn's work be called off?"

Yes. Say so, such as `中止して`. rn asks what goes, such as its pull request and its branch, and
removes only what you confirm.

### "Does it change the repository's files, or merge on its own?"

No. rn works on the branch you start it on, makes a branch or a worktree only when you ask for one,
and leaves the ready mark and the merge to you.

## Documentation

- [Changelog](CHANGELOG.md): for you after an update, the changes in each version.
- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](LICENSE)
