# webplan — design notes（v2・ゼロベース）

本文の設計（背景 → ペイン → ベネフィット → UX → 構造 → 部品）は #2 で書く。ここには着手前の決定だけを置く。

## 決定

### D-1: learn-by-doing — 案件実走 → 設計 → 実装 → dogfood の順で作る

**保証**：プラグインのフローが、実際に人が決めた順序と入力・出力を再現する。既存利用者への影響が無い。

**決定と理由**：v1（hposal）の Round 3 実走で、4フェーズが「文書を順に書く」流れであり、Base／Scope／Level・進め方の上限・
コンテンツの担当・体制が固まらないまま 02/03 を書いて手戻りが出た。スキル作成と案件を並行すると両方が濁るので、
まず仮案件を手で最後まで進めて `worklog.md` に記録し、一般化した `learnings.md` から設計する。v1 と案件
フォルダの派生物は削除（履歴からも除去）し、前提にしない。参考の型＝wayfinder（Destination を先に置き、decision を
一つずつ解き、fog が晴れたら spec に畳んで handoff）。

**破れの検知**：`learnings.md` の決定順と SKILL の手順順の突き合わせ／`.rn/webplan/project/` が `git ls-files` に
現れないこと。

### D-2: 読者層＝日本限定（v1 D-6 を引き継ぐ）

利用者が読む成果物（README・テンプレ・提案書の可視コピー）＝日本語、SKILL.md・メタ・CHANGELOG・コミット/PR＝英語。
`.claude/rules/language.md` の例外条項による。

### D-3: 語彙は案件で試してから確定する

Base（Existing site／Template／Reference／Brand assets）× Scope（Refresh／Redesign＋Expand オプション）× Level
（Basic／Current／Signature）／工程 Discovery → Content → Design〔Direction → Refinement → Rollout〕→ Build → QA →
Launch → Handover → Care／上限 Direction 2 案・revision 2 回／ロール Client／Provider（＋Subcontractor）。
松竹梅は廃止（Scope と Level の 2 軸を 1 列に潰していた）。1・2・3 は業界で通じる語、Level と Expand は造語のため
提案書の初出で 1 行定義する。

### D-4: 名前は #2 で決める

`hposal` は HP 限定に読めるが対象は Web サイト全般（HP／LP）。作業 slug は `webplan`。

### D-5: 最終成果物は提案書の Markdown、PDF はビュー

正＝`04_proposal.md`（目次・各ページの文・数字）。HTML パーツ → PDF は md からの一方向変換で、人が直すのは md だけ。
見積も 正＝行データ＋定数、ビュー＝表。「一つの事実は一か所」を提案書まで貫き、v1 の export ゲート（残留ゼロ）は変換器の
検査に置き換わる。#1 の逆算は「`04_proposal.md` の目次と各節に必要な決定」から始める。

**根拠**：ユーザー（2026-09-06）「最終成果物は pdf だけどそれはビューなので、テキストの md が最終成果物では」。
