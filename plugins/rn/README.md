# rn

rn is a Claude Code plugin that makes what you ask for, ready for the people you make it for.

rn is for you when you have Claude Code make something in a GitHub repository for other people to
use. With it, you see what you asked for work early, and you decide only what's yours: which
need to meet first, and how it works for you once you try it.

This version makes the first working slice of a request. Growing it after you try it, one
addition at a time, comes in a later version.

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

At your repository's root in Claude Code, `/rn:on` asks what it can help with.

## Walkthrough

At the end, you hold a command that prints an invoice from your accounting team's statement, made
before anything else of the request.

This run is the one that rn's architecture draws, with its talk in Japanese. No end-to-end run of
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

rn reads your repository, then asks whom it's for, and then what for, one at a time:

```text
誰が使いますか？

1. 経理チームの方（おすすめ）
   依頼の「経理チームが」から読みました
2. ほかの人
   誰かを書いてください
```

You type `1`. rn asks:

```text
経理チームの方は、それで何をしたいですか？

1. 月末に、開発者の手を借りずに請求書を出したい（おすすめ）
   依頼の「Pythonを書かずに」から読みました
2. ほかのこと
   その点を書いてください
```

You type `1`. rn asks which need to make first:

```text
どれから作りますか？

1. 明細ファイルから、請求書を1枚印刷できる（おすすめ）
   印刷できれば、経理チームの方が月末に自分で請求書を出せます
2. インボイス制度の記載事項を満たしている
3. 発行者の情報を毎回入れなくて済む
4. ガイドだけで使い始められる
```

You type `1`. Before it makes anything, rn looks for what already prints an invoice, in your
repository and among the tools your team has, and makes only what that lacks. It shows what it
makes before you can try it:

```text
試せるまでに、次の3つを作ります。

1. invoice コマンド
2. 請求書の型
3. 使い方の説明
```

Each time one is done, rn tells you, so you can say at once what's off:

```text
invoice コマンドができました（1/3）
```

Once AI evaluators have tried it as your accounting team would, rn hands it to you:

```text
試せるようになりました（3/3）

できること：明細ファイル1つから、請求書を1枚印刷する
まだしないこと：2から4

  cd .claude/worktrees/rn-20261126-invoice-from-statement
  invoice 見本の明細.csv

これで足りれば /rn:ty、変えたい点があれば /rn:gm に続けてその内容を入力してください。
```

You run it, and the printer gives one invoice with the customer, the lines, and the total. You
type `/rn:ty`. rn checks the pull request whole, then asks what happens to the needs you didn't
pick:

```text
最終チェックが通り、1ができました。

選ばなかった2から4を、どうしますか？

1. 2と3はissueに残し、4は残さない（おすすめ）
   2と3は印刷を毎月使うのに要り、4は使う人が少ないうちは要りません
2. すべてissueに残す
3. どれも残さない
```

You type `1`. rn shows:

```text
2と3をissueに残しました：https://github.com/lovaizu/playground/issues/39 、https://github.com/lovaizu/playground/issues/40

PRを「レビュー可」にしてから、マージしてください：https://github.com/lovaizu/playground/pull/38
```

You mark the pull request ready for review, and merge it.

## How it works

rn puts in your hands, early, the least that runs for the one need you pick.

### "I can't spell out every detail up front, so it builds the wrong thing."

You don't spell it out. rn lists the needs it found in your words and picks one with why, and
you pick. You then try what runs, and say what's off.

### "It builds the whole request before anything runs."

No. rn makes the least that runs, through every kind of deliverable it needs at once, and hands it
to you before it makes more.

### "Does it work in a language other than English?"

Yes. rn talks in your language and writes in your repository's, asking only where they disagree.

### "Does it make what already exists?"

No. Before it makes anything, rn looks for what already meets the need, such as a feature of
Claude Code, a tool you have, or a part of your repository, and makes only what that lacks.

### "Does it show how far it has come?"

Yes. When making starts, rn lists what it makes before you can try it, and tells you each time
one is done, such as `（1/3）`.

### "Its output misses what this kind of work needs."

rn makes each deliverable by the best practice of its kind, such as one for a README, and meets
each of its necessary conditions, while what it makes stays the least.

### "It looks done, but the people it's for can't use it."

Before you see it, AI evaluators try each deliverable with only what its people have, never what
rn meant. Then you try it yourself.

### "Does it drop part of the request?"

No. Each need that you or the issue named stays on the list. At the end, rn proposes for each one left
whether to keep it in an issue.

### "Does it change what others share?"

Only with your say. Where the work needs a change to a part outside what you asked for, such as
the repository's checks, rn asks whether to give it an issue of its own instead.

### "Can a run stop and go on later?"

Yes. `/rn:dn` stops the run once what it's writing is whole, and `/rn:up` picks it up where it
stopped, in any conversation.

### "Can a run be called off?"

Yes. Say so, such as `中止して`. Once you confirm, rn removes the run's worktree, its branch, and its
pull request.

### "Does it change the repository's files, or merge on its own?"

No. rn works in its own worktree, and leaves the ready mark and the merge to you.

## Documentation

- [Changelog](CHANGELOG.md): for you after an update, the changes in each version.
- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](LICENSE)
