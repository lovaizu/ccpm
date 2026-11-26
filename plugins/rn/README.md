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

rn reads your repository, then shows what the run aims at and the needs it found, with its pick:

```text
この run で目指すこと：
  月末に請求書を出す経理担当の方が、開発者の手を借りずに、明細ファイルから請求書を印刷できる

できるようにしたいこと：
  1. 明細ファイルから、請求書を1枚印刷できる     ← おすすめ
  2. インボイス制度の記載事項を満たしている
  3. 発行者の情報を毎回入れなくて済む
  4. ガイドだけで使い始められる

1をおすすめします。2から4は、印刷できて初めて意味を持つからです。
番号で選んでください。目指すことが違えば、その点を書いてください。
```

You type `1`. rn makes the least that prints an invoice, and each message opens with where it
stands:

```text
いま：明細ファイルから請求書を1枚印刷できる、の一番細い形を作っています。
```

Once AI evaluators have tried it as your accounting team would, rn hands it to you:

```text
一番細い形ができました。試してください。

できること：明細ファイル1つから、請求書を1枚印刷する
まだしないこと：2から4

試し方：
  cd .claude/worktrees/rn-20261126-invoice-from-statement
  invoice 見本の明細.csv

これで足りれば/rn:ty、変えたい点があれば/rn:gmに続けてその内容を入力してください。
```

You run it, and the printer gives one invoice with the customer, the lines, and the total. You
type `/rn:ty`. rn checks the pull request whole, then shows:

```text
最終チェックも通りました。

目指すこと：1が届いています。経理担当の方が、明細ファイルから請求書を1枚印刷できます
選ばなかったこと：2から4。issueに残すか、何もしないかを提案します
  2と3は、印刷を毎月使うのに要るので、issueに残すことをおすすめします
  4は、使う人が少ないうちは要らないので、何もしないことをおすすめします

マージをおすすめします。PRを「レビュー可」にしてから、マージしてください。
PR：https://github.com/lovaizu/playground/pull/38
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

### "Its output misses what this kind of work needs."

rn makes each deliverable by the best practice of its kind, such as one for a README, and meets
each of its necessary conditions, while what it makes stays the least.

### "It looks done, but the people it's for can't use it."

Before you see it, AI evaluators try each deliverable with only what its people have, never what
rn meant. Then you try it yourself.

### "Does it drop part of the request?"

No. Each need that you or the issue named stays on the list. At the end, rn proposes for each one left
whether to keep it in an issue.

### "Can a run stop and go on later?"

Yes. `/rn:dn` stops the run once what it's writing is whole, and `/rn:up` picks it up where it
stopped, in any conversation.

### "Does it change the repository's files, or merge on its own?"

No. rn works in its own worktree, and leaves the ready mark and the merge to you.

## Documentation

- [Changelog](CHANGELOG.md): for you after an update, the changes in each version.
- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](LICENSE)
