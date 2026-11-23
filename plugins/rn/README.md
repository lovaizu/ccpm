# rn

rn is a Claude Code plugin that makes what you ask for, ready for the people you make it for.

rn is for you when you have Claude Code make something in a GitHub repository for other people to
use. With it, you get each deliverable you mean, one its people can use, and you decide only
what's yours.

## Non-goals

- rn doesn't put the deliverable in front of real people: its AI subagents read it as they would.
- rn doesn't finish alone where your goal leaves a question open: it asks you, and other work goes
  on.
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

At the end, you have a checked pull request that adds a command and a guide for your accounting
team.

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

rn reads your repository, then asks whom the work is for:

```text
誰のためのものか、こう考えています。
経理チームの方々。
これで合っていますか？
```

Only some of the team send invoices, so you type:

```text
経理チームのうち、月末に請求書を出す担当の人です
```

rn takes your words, and asks what they can do at the goal:

```text
わかりました。月末に請求書を出す経理担当の方々、とします。

完成したら、その方々に何ができればよいか、こう考えています。
開発者の手を借りずに、ガイドだけを見て、明細ファイルから請求書を印刷できる。
これで合っていますか？
```

You type `はい`. rn sums both up:

```text
この内容で進めます。

誰のため：月末に請求書を出す経理担当の方々
ゴール：開発者の手を借りずに、ガイドだけを見て、明細ファイルから請求書を印刷できる

この内容で合っていますか？
```

You type `はい`. rn shows the way to the goal:

```text
ゴールまでの進め方です。

1. 誰の何のためか（プロダクトビジョン）
2. どう使うか（経理担当向けのガイド）
3. 請求書に何を載せるか（請求書の書き方の決まり）
4. どう実現するか（ソリューション設計、テスト戦略）
5. 部品ごとにどう作るか（モジュール設計、テストケース）
6. 作って確かめる（コマンド本体、テストコード）

請求書には決まった書き方（インボイス制度の記載事項）があるので、それをまとめる段を3に入れました。
変更内容：https://github.com/lovaizu/playground/pull/38/files

どこで確認しますか？
a. 1だけ確認して、あとは最後まで進める
b. 1と2を確認する
c. 段ごとに確認する
残りは1から決まるので、aをおすすめします。
```

You type `a`. rn starts on the first step:

```text
いま1/6：誰の何のためか（プロダクトビジョン）

プロダクトビジョンを作っています。
```

Once it's made, rn shows it for you to check:

```text
いま1/6：誰の何のためか（プロダクトビジョン）

プロダクトビジョンができました。ご確認ください。
これで、経理担当が何のために使い、どこまでできれば足りるかが決まります。

変更内容：https://github.com/lovaizu/playground/pull/38/files

承認する場合は/rn:ty、変えたい点がある場合は/rn:gmに続けてその内容を入力してください。
```

The vision lets one statement hold several customers, but yours never does, so you type:

```text
/rn:gm 明細ファイルは取引先ごとに1つです。1つのファイルに複数の取引先が混ざることはありません
```

rn makes it again, and shows it:

```text
いま1/6：誰の何のためか（プロダクトビジョン）

プロダクトビジョンを直しました。ご確認ください。
明細ファイル1つから、その取引先の請求書を1枚印刷する、としました。

変更内容：https://github.com/lovaizu/playground/pull/38/files

承認する場合は/rn:ty、変えたい点がある場合は/rn:gmに続けてその内容を入力してください。
```

You type `/rn:ty`. While it makes the guide, rn asks what only you know:

```text
いま2/6：どう使うか（経理担当向けのガイド）

経理担当の方が使うパソコンの環境はどれですか？
a. WindowsのPowerShell
b. macOSのターミナル
c. Linuxの端末
会社のパソコンに多いので、aをおすすめします。
```

Your team works on Linux. You type:

```text
LinuxのノートPCです。明細はLibreOffice Calcで管理しています
```

rn makes the rest with no sign-off, as you chose. Each message opens with where it stands:

```text
いま4/6：どう実現するか（ソリューション設計、テスト戦略）

ソリューション設計とテスト戦略を作っています。
```

Once each step is done, an AI new to the work checks the pull request whole for rn. rn shows:

```text
6/6すべてできました。最終チェックも通りました。

ゴール：届いています。経理担当の人が、ガイドだけを見て、明細ファイルから請求書を印刷できます
全体との整合：リポジトリのREADMEに、コマンドとガイドを載せました
余分なもの：ありません
CI：すべて通っています

ほかに直せる点の提案：
- インストール手順の3行目は、v0.1.0のリリースを公開するまで404で止まります。公開してから経理担当に知らせてください

マージをおすすめします。PRを「レビュー可」にしてから、マージしてください。
PR：https://github.com/lovaizu/playground/pull/38
```

A colleague from accounting follows the guide alone. They save one customer's lines for the month
from LibreOffice Calc as CSV. They open a terminal in that folder, and type one command. The command's
end-to-end test checks this screen and the printed invoice:

```console
$ invoice 2026年11月分明細.csv
はじめて使うので、発行者の情報を伺います。次からは聞きません。
発行者の正式名称: 株式会社あおば事務用品
登録番号(Tと13桁の数字): T1234567890123
締め日と支払条件(例: 月末締め翌月末払い): 月末締め翌月末払い
お振込先の銀行名: さくら銀行
支店名: 本店営業部
口座種別(普通か当座): 普通
口座番号: 1234567
口座名義(カナ): カ)アオバジムヨウヒン
株式会社みなと商事 御中: 請求書番号2026-11-001、ご請求金額51,980円
既定のプリンター「経理室プリンター」で1枚を印刷しました。
```

The next month, the command prints without a question. You mark the pull request ready for
review, and merge it.

## How it works

rn works only on the few things that decide whether a deliverable's people can use it.

![How rn works, from your decisions to the pull request you merge](images/how-it-works.svg)

### "I can't spell out every detail up front, so it builds the wrong thing."

rn asks only the decisions that change what the people get, one at a time, with why. You check
the steps you choose of its way to the goal, and get what you mean with no specification.

### "Does it work in a language other than English?"

Yes. rn talks in your language and writes in your repository's, asking only where they disagree.

### "Its output misses what this kind of work needs."

rn plans and makes each deliverable by the best practice of its kind, such as one for a README.
For a kind it has none for, such as an invoice, its way to the goal makes one first.

### "It looks done, but the people it's for can't use it."

AI evaluators read each deliverable with only what its people have, never what rn meant. rn remakes
it from what they find, twice at most, then shows you what's still short for you to decide.

### "Each fix breaks something else."

rn takes each shortfall back to the decision it comes from, and makes the deliverable again from
the decisions. A shortfall the people would never meet changes nothing, so the deliverable doesn't
grow with each remake.

### "Does it keep working on what no one needs?"

No. Each turn, rn reviews the plan by what its work showed, and works next where the
people gain most.

### "Does it skip a step when no one watches?"

No. Lane, a plugin installed with rn, stops each part of rn that leaves a step and shows it that
step.

### "Does it change the repository's files, or merge on its own?"

No. rn works in its own worktree and a throwaway copy, and leaves the ready mark and the merge to
you.

## Documentation

- [Changelog](CHANGELOG.md): for you after an update, the changes in each version.
- [Lane](https://github.com/lovaizu/ccpm/blob/main/plugins/lane/README.md): for you if you want to
  know what Lane does, or use it in a plugin of your own.
- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](LICENSE)
