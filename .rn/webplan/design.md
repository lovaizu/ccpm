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
松竹梅は廃止（Scope と Level の 2 軸を 1 列に潰していた）。
**2026-09-07 追記**：計画の見出し Scope との衝突を避け、案の軸名は **Change**（Refresh／Redesign）に改める。#1 では Base（Existing site）× Change × Level（Current）で 2 案を並べ、Expand は使わなかった。1・2・3 は業界で通じる語、Level と Expand は造語のため
提案書の初出で 1 行定義する。

### D-4: 名前は #2 で決める

`hposal` は HP 限定に読めるが対象は Web サイト全般（HP／LP）。作業 slug は `webplan`。

### D-5: 最終成果物は「計画」。提案書はその時点の計画から出すビュー、タスク一覧は内部の別ファイル

計画 1 本が正。AI が各見出しを起案し、人は判断（選ぶ・承認する）だけ。提案書は提案時点の計画から一方向に
生成するビューで、出したあと更新しない。見積書は別に作らない。提案書の費用欄が見積の要約で、根拠となる
人日レベルのタスク一覧（作業項目・in/out・担当・確認者・Client 確認）は Client に出さない内部の別ファイル `tasks.md` に持ち、計画には
工程別の人日の要約だけを置く（計画の読者には作業行はノイズ）。計画はプロジェクト開始後も決定が変わるたびに直し続ける（ChangeLog に理由を残す）。

計画のアウトライン（見出しは英語・単数形。どう見せるかはビューの話なので、計画側では分ける）：

```
Requirement  Goal / Priority                                   施主から聞く（AI が起案、人が確認）
Context      Team / AsIs                                       調べる（AI が起案、人が確認）
Planning     ToBe / Scope / Content / Process / Schedule / Cost / Risk   上から順に決める。各決定は上流だけを根拠にする
Contract                                                       Planning とは別部。Cost・Schedule・Risk・Priority を参照
ChangeLog                                                      Planning とは別部。開始後の決定変更と理由
```

Contract と ChangeLog を外した Requirement / Context / Planning は Web サイトに限らない汎用の骨組み。
Priority にはトレードオフスライダー（何を固定し何を動かすか）と予算上限・期限を置き、施主と「何を守るか」を最初に揃える。
Base／Scope／Level の案の比較は Scope の冒頭に「検討した案と選んだ案」として置く（軸名 Scope と見出し Scope の衝突は
D-3 で軸名側を見直す）。Team は与件の事実（誰が居て何ができるか）として Scope の上流に置き、Process は工程ごとに
Team の役割を参照するだけにする。
トレースの仕組み：各決定に ID と「根拠にした決定」を持たせ、Cost の一行から Goal まで遡れる。上流に根拠の無い決定・
下流に使われない決定を「切れ」として検査する（AC 2・AC 3 の土台、#3 で機械検査）。

見積は行データ＋定数が正で、表はビュー。「一つの事実は一か所」を計画まで貫き、v1 の export ゲート（残留ゼロ）は
変換器の検査に置き換わる。

**根拠**：ユーザー（2026-09-06）「このプラグインは計画を作ること。最終成果物は計画。提案書は計画のビューで、計画は
プロジェクト開始後もメンテするもの、提案書はメンテしない」「すべて AI、人は判断するだけ」「どう見せるかはビューの話」「Requirement, Context, Planning ってことですか」「Contract、ChangeLog は Planning とは別。この 2 つを外せば何にでも使える」。
旧 D-5（提案書 Markdown が正・PDF はビュー）はこれで置き換え。
