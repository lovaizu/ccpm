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
- rn doesn't merge: it leaves one pull request, ready once you sign off the last deliverable.

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

At your repository's root in Claude Code, `/rn:on` asks what you want to make.

## Walkthrough

At the end, you have a pull request that adds a command and a guide for your accounting team.

This run comes from an end-to-end test of rn, with its talk in Japanese. Your accounting team asks
a developer for each invoice, and you want them to print it themselves. At your repository's root
in Claude Code, you type:

```text
/rn:on
```

rn shows:

```text
What do you want to make?
```

You type:

```text
経理チームが、Python を書かずに、明細から請求書を印刷できるコマンドがほしい
```

rn puts the goal in its words, and proposes Japanese for the deliverables and for its talk:

```text
目標の確認です。私なりにまとめると次のとおりです。

目標:
  経理チームが、開発者の手を借りずに、明細から請求書を自分たちで印刷できるようにする。経理チームの人は、ガイドだけを見ながら、明細ファイルからコマンド一つで請求書を印刷する。
  (コマンドとガイドは日本語で作り、このやり取りも日本語で進めます)
この理解で合っていますか?
```

You type `はい`. rn asks whether to set down the rules of an invoice first, such as the issuer's
registration number:

```text
ひとつ、決めていただきたいことがあります。
  請求書のレイアウトを作る前に、請求書の書き方の決まりごと(インボイス制度で必要な記載事項、たとえば登録番号、税率ごとの合計と消費税額、交付先の名前など)を先にまとめるべきかどうかです。まとめておけば、印刷した請求書がそのまま取引先に出せることを確かめながら作れます。まとめなければ、その分早く着手できますが、記載事項の抜けは印刷されるまで気づきにくくなります。
  先にまとめることをおすすめします。請求書には決まった書き方があり、記載事項が欠けた請求書は経理チームが使えないからです。

請求書の決まりごとを先にまとめますか?(おすすめ:はい)
```

You type `はい`. rn shows its plan:

```text
計画ができました。ご承認ください。
  1. 経理チームが明細から請求書を印刷できるまでの計画
  2. 請求書の決まりごと(インボイス制度の記載事項など)をまとめたもの
  3. 経理チームが何のために、どこまでできれば足りるかの整理
  4. 経理チーム向けのガイド(ガイドだけを見て準備から印刷までできるもの)
  5. 明細の読み込みから請求書の印刷までの全体の組み立て
  6. コマンドの各部品の役割と呼び出し方
  7. 守るべき振る舞いを確かめるテストケースの一覧
  8. 明細ファイルを渡すだけで請求書を印刷できるコマンド本体
  請求書のレイアウトそのものは、2 の決まりごとができてから計画に加えます。
  変更内容: https://github.com/lovaizu/playground/pull/38/files
承認する場合は /rn:ty、変えたい点がある場合は /rn:gm に続けてその内容を入力してください。
```

You type `/rn:ty`. rn makes the deliverables, and you sign off the rules of an invoice and the
team's aim, each with `/rn:ty`. While it makes the guide, rn asks you three questions in the same
form as the first. To printing the registration number and the tax of each rate, you answer
`載せる`. To a license, you answer `社内だけで使うので付けない`. To where the team asks for help,
you answer `このリポジトリの Issues にしてください`.

rn shows the guide:

```text
「経理チーム向けのガイド」ができました。ご承認ください。
  これでできること:経理チームのメンバーが、このガイドだけを見て次のことを確かめられます。invoice が自分たちの仕事に合うか、準備に何が要るか、どんな請求書が出てくるか、つまずいたらどうするか。ただし、まだ開発中なので、いまはインストールも印刷もできません。
  ご相談せずに決めたこと:
  - 使う環境は Windows の PowerShell にしました
  - インストールは、配布ファイル(invoice 0.1.0)を uv というツールで入れる3行の手順にしました。配布ファイルはまだありません
  - 発行者の名称・登録番号・振込先などは、初回の実行で一度だけ尋ねます
  - 消費税の端数は、税率ごとに一度だけ切り捨てます
  - 明細の CSV に必要な7つの列と、単価の税抜・税込の示し方を書きました
  - 「できないこと」には「明細を作ったり直したりはしない」を挙げました
  - 「ほかの資料」には、経理チームが開けるページと Issues だけを載せました
  ほかに直せる点の提案:
  - 冒頭に「いまはインストールのコマンドもまだ通らない」と書き添える。いまは、試した人が見慣れないエラー(404)に出会い、開発者に尋ねてしまいます
  - インストールの3行がエラーなく通り、最後に「invoice 0.1.0」と出るのを確かめる。コマンド本体の配布ができてからでないと確かめられません
  変更内容: https://github.com/lovaizu/playground/pull/38/files
承認する場合は /rn:ty、変えたい点がある場合は /rn:gm に続けてその内容を入力してください。
```

Your team works on Linux, which rn didn't know. You type:

```text
/rn:gm 経理チームは Linux のノートPCを使っていて、明細は LibreOffice Calc で管理しています。Windows の PowerShell ではなく、Linux の端末で動く手順にしてください
```

rn shows:

```text
ご指摘のとおり、ガイドを Linux の端末向けに作り直しています。直すのは次の2つで、明細は LibreOffice Calc から CSV で書き出す前提にします。
- インストール手順
- 「使ってみる」の実行例

ほかに直せる点として出した2つの提案は、今回のご指示に含まれていなかったので取り下げました。
```

rn shows the guide again, made for the Linux terminal, and you type `/rn:ty`. In the same form,
you then sign off the architecture, the invoice's layout, the command's parts, and their tests. For the parts, you take one of rn's proposals with `/rn:gm`.

Once rn has made the command, it asks:

```text
ひとつ、決めていただきたいことがあります。
  承認済みの「部品の役割」と「テストケースの一覧」を、いまのコマンド本体の振る舞いに合わせて直し直すかどうかです。
  コマンド本体には、あとから決めた点が入っています。
  - 全角の数字・英字・記号は半角に、半角カナは全角に読み替える
  - 取引日は「2026/11/20」の形も受け付ける
  - 明細の行は取引日の順に並べる
  - 宛先の敬称を会社の形から決める
  ところが、承認済みの2つの文書は、まだ「明細の順に並べる」と書いていたり、これらを「決まっていない」としていたりします。このままだと、あとでコマンドを直す人は、文書とコードのどちらが正しいのか分かりません。
  - 直す場合:「部品の役割」と「テストケースの一覧」をもう一度作り直します。コマンド本体はそのあとで手直しし、テストを文書のケースと一対一に合わせます。
  - 直さない場合:文書と食い違ったまま、コマンド本体の残りの手直し(依存の版の固定と、テストで結果をまるごと確かめること)だけ進めます。
  直すことをおすすめします。コマンドを守っていく人が、文書だけを頼りに正しい振る舞いを確かめられるようにするためです。

承認済みの2つの文書を、コマンド本体の振る舞いに合わせて作り直しますか?(おすすめ:作り直す)
```

You type `作り直してください`, and sign off the two remade documents and the command, each with
`/rn:ty`. rn shows:

```text
完了しました。プルリクエストはマージできる状態です: https://github.com/lovaizu/playground/pull/38

マージする前に、2点確認してください。
- 古いテスト `invoice/tests/unit/test_width.py` と `test_sheet.py` の削除が、このプルリクエストに含まれているかを、私はまだ確かめていません。残っていると、テストが走らなくなるおそれがあります。
- インストール手順の3行目は、v0.1.0 のリリースを公開するまで 404 で止まります。経理チームがガイドどおりに invoice を入れられるのは、公開したあとです。
```

A colleague from accounting follows the guide alone. They save the month's lines from LibreOffice
Calc as CSV, open a terminal in that folder, and type one command. The command's end-to-end test
checks this screen and the printed invoice:

```console
$ invoice 2026年11月分明細.csv
はじめて使うので、発行者の情報を伺います。次からは聞きません。
発行者の正式名称: 株式会社あおば事務用品
登録番号(T と 13 桁の数字): T1234567890123
締め日と支払条件(例: 月末締め翌月末払い): 月末締め翌月末払い
お振込先の銀行名: さくら銀行
支店名: 本店営業部
口座種別(普通か当座): 普通
口座番号: 1234567
口座名義(カナ): カ)アオバジムヨウヒン
株式会社みなと商事 御中: 請求書番号 2026-11-001、ご請求金額 51,980 円
既定のプリンター「経理室プリンター」で 1 枚を印刷しました。
```

The next month, the command prints without a question. You then merge the pull request.

## How it works

rn works only on the few things that decide whether a deliverable's people can use it.

![How rn works, from your decisions to the pull request you sign off](images/how-it-works.svg)

### "I can't spell out every detail up front, so it builds the wrong thing."

rn asks only the decisions that change what the people get, one at a time, each with a
recommendation. You sign off the plan and each deliverable, so you get what you mean without a
specification.

### "Does it work in a language other than English?"

Yes. rn proposes a language for the deliverables and one for its talk, and you settle both with
the goal.

### "Its output misses what this kind of work needs."

rn plans and makes each deliverable by the best practice of its kind, such as one for a README.
For a kind it has none for, it asks you first whether to make one.

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

No. rn works in its own worktree and branch, runs commands in a throwaway copy, and leaves
the merge to you.

## Documentation

- [Changelog](CHANGELOG.md): for you after an update, the changes in each version.
- [Lane](https://github.com/lovaizu/ccpm/blob/main/plugins/lane/README.md): for you if you want to
  know what Lane does, or use it in a plugin of your own.
- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](LICENSE)
