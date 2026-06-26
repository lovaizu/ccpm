# Zero-base dogfood findings + reflection plan (task #11)

パーツ化（task #10）後の `hposal` を、メインエージェント自身が「プラグイン利用者」役となって
`/hposal:up` を頭から実走（phase 1→4）して集めた所見と、その plugin 反映方針。所見ID（F1–F14・
T1–T3）はアンカーとして保つ。これは ccpm 内の内部作業ノート（steering.md と同じ register：英語見出し＋
日本語本文）であり、plugin 成果物ではない。

## Run record（実走記録）

- **何を回したか**：ゼロベース dogfood（task #10 のパーツ era を対象）。D-10 の二者構成で、subagent が
  `/hposal:up`（＝`hposal/skills/up/SKILL.md`）を起草実走し、main が利用者/レビュー役として★ゲート・
  質問に応じた。
- **対象案件（一般化・PII なし）**：単一ページの Wix コーポレートサイト（`*.wixsite.com` サブドメイン）、
  個人コンサルタント、toB→toC ＋法人化、基盤は「ノーコード有料プラン」と「マネージド WordPress プラン」の
  間で未定。実走は public リポジトリ外の private フォルダで行い、生成物 01–04 は private に留めた。
- **結果**：phase 1→4 が完走。実 22 スライド deck をパーツから組み立て、**export ゲート 0/0**（`{{` 残留 0・
  `例` 等の見本残留 0）、**CSS は `_head.html` とバイト一致**（369 行・機械 diff 検証）、22pp の 16:9 PDF、
  **要件バーンダウン 15/15 r 充足**、**内部値の素抜けゼロ**（人日/単価/50,000/内製/外注/二層/built-up が
  すべて grep 0、提示額 2,020,000/2,340,000 は present）。3 層比較フロー（compare-basis/build/operation ＋
  estimate.compare）が動作。
- これで steering の task #11 完了基準「メインエージェントが利用者役で全フェーズを実走した記録」を満たす。

---

## Findings

severity は low/med。各所見は **hposal の gap（プラグイン側で直す）** か **execution artifact（実行時の事故・
プラグイン欠陥ではない）** を明記。F10 のみ execution artifact。

### Phase 1 — Requirements

- **F1（gap, low）— stated-count 突合が「客が数を言った」前提**
  SKILL（`SKILL.md:90`）は「実カウントを客の申告と突合し差分を全記録」とするが、本ブリーフはページ数を
  申告していないため突合の基準が無い。実行側はナビ印象（〜7）対 実 URL（3）で代用した。
  → なぜ重要：申告が無い案件は珍しくなく、その時に何を「差分」として記録するかが手順に無いと、突合ステップが
  空回りする。

- **F2（gap, low）— 標準確認トピックが 1 トピック→2 質問に割れる**
  標準トピック⑤「客の要望の読み」が、toC スコープ＋基盤≠WordPress の 2 質問に fan-out した。SKILL（`SKILL.md:105`）の
  暗黙の「1 標準トピック＝1 質問」対応が、割れるトピックを想定していない。軽微なトレーサビリティの摩擦。

- **F3（ambiguity, low）— 基盤質問の P1/P2 境界**
  入力が価格事実（あるノーコードプランの月額）を運ぶとき、P1「基盤選定を q として名付ける」と P2「基盤を比較する」の
  線引きが曖昧。実行側は q ＋前方ポインタだけ残した（正しい）が、この線を一文で明示できる。

- **F4（gap, med）— アンカー型単一ページのページ数膨張**
  Wix のアンカー型単一ページでは「1 ページ＝1 行＝1 URL」が可視セクション/ナビと大きく乖離（3 URL 対 〜7 ナビ
  対 〜11 セクション）。SKILL の「new > current」⚠️ は精神を覆うがアンカー/単一ページの場合を名指ししていない。
  新 IA のページ数が 3 URL の母数から膨らむため、「アンカーのセクションが将来のページになる」を明示する ⚠️ が要る。

### Phase 2 — Proposal design

- **F5（gap, med）— マネージド SaaS 基盤の一次価格取得が不安定**
  WordPress.com 等のマネージド SaaS 基盤の一次価格 fetch が失敗（WebFetch が通貨文字化け／二次情報が ¥2,900 対
  ¥5,600 で食い違い）。SKILL は「q として保留、記憶から引用するな」と正しく言い、実行側もそうした。だが SaaS の
  月額が課金条件（年/月/複数年）で変わる点や、一次ページが読めない時の hold-as-q 以外の代替が手順に無い。一行ヒントで潰せる。

- **F6（gap, med）— `02` テンプレに移行チェックリスト/プラットフォーム実態ゲートのスロットが無い**
  Phase 2 の ⚠️ は「移行標準作業チェックリスト」と「プラットフォーム実態ゲート」表を実質必須にしているが、
  `02_proposal-design.md` には具体アイテム表と見積モデル節しかなく、どちらのスロットも無い（実物確認済）。実行側は
  置き場を発明（p12 配下・見積モデル節内）した。空スキャフォルドを置けば取りこぼされない。
  → なぜ重要：SKILL 自身の原則どおり「必須なのにスロットが無い構造は落ちる」。

### Phase 3 — Work breakdown

- **F7（ambiguity, low）— QC 軸と各行レビューの二重計上**
  責任分担マトリクスが「品質チェック」を軸（301/tests/QC/data-load）に持つが、SKILL（`SKILL.md:149`）は各行が
  既に create+review+feedback を持つとも言う。QC は own PD で二重計上か空欄かのどちらかになる。実行側は QC を各行
  内に持ち、マトリクスのセルをテスト実行行に向けた（妥当）が、SKILL はどちらか言っていない。一行で解決。

- **F8（gap, med — F6 と再発）— `03` テンプレが単一基盤・フラットで SKILL ゲートに追いつかない**
  `03_work-breakdown.md` の骨格は単一基盤・フラット（明細表 1 ＋小計 1）。だがモデルは「共通 1 回＋基盤分岐＋
  基盤ごと総額」を求め、完了ゲート（`SKILL.md:149`）は役割別突合表を要求する。骨格にはどちらも無く、実行側は
  「コピーして埋める」でなく作り直しになった。テンプレが SKILL ゲートに lag している。
  → F6 と統合してテーマ化（T1）。

- **F9（boundary, low）— レンジ下限の reduced-PD と「自分で丸めるな」の境界**
  レンジ下限（PD 削減後）を生の reduced-PD 値に保ち「提示丸めではない」と注記したが、「行を段階的に落とす」と
  「提示額を丸める」の線を一文で明示できる。

- **F10（execution artifact — hposal ではない）— Write が tool タグを末尾に漏らした**
  起草 subagent の Write が `</content>`/`</invoke>` 様のタグをファイル末尾に漏らし、main が read 時に検出して除去。
  プラグイン欠陥ではない。ただし Phase 4 の export grep ゲート（と一般の末尾チェック）が役に立つことの裏付け。

### Phase 4 — Proposal（パーツ組み立て＋export）— task #10 の本番試験

- **F11（parts gap, med）— `work-detail` が 1 スライド固定で 3 層見積に溢れる**
  `work-detail.html` は 1 スライドで出荷されるが、3 層「共通＋基盤分岐」見積（4 カテゴリ帯・〜18 行）は溢れる。
  outline（`04_proposal.md:76`）は「長ければ複数回使い分割」と言うが、組み込みの common/branch 変種ペアが無く、
  実行側が手で分割した。estimate の変種に倣った `work-detail.common`/`work-detail.branch` ペアがあれば、task #10 が
  ターゲットにする 3 層案件で手作業・誤りやすい一手が消える。

- **F12（outline gap, low-med）— `{{案件名}}` が `_head.html` の `<title>` にあり、忠実組み立てがゲートに到達不能**
  `{{案件名}}` が `_head.html` の `<title>` に居るため、忠実な組み立ては head を編集しない限り `grep {{ == 0`
  ゲートに永久に到達できない。「_head に触るな」は CSS の話なのに、title プレースホルダが組み立て後ファイルの fill を
  強制する。outline に「`<title>` は組み立て時 fill（CSS はバイト不変・title だけ埋める）」を明記すべき。

- **F13（parts polish, low）— `estimate.compare` のデフォルト注記が自然長でフッターに被る**
  `#estimate` の CSS が内容を拡大するため、`estimate.compare` のデフォルト注記を自然長で埋めるとフッターに溢れた。
  短いデフォルト注記か height-budget ヒントをパーツに入れれば防げる。SKILL に既にある `.dense` overflow ⚠️ と同類
  ＝パーツにも長さ予算が要る。

- **F14（mechanics, low）— `{{総ページ数}}` が全パーツのリテラルで、後からの追加/分割が全スライドを再触り**
  `{{総ページ数}}` が各パーツのリテラルなので、後からパーツを追加/分割すると分母を全スライドで振り直す（ここでは
  20→21 を 21 スライド分）。outline（`04_proposal.md:19`）は「総ページ数は組み立て時に確定」と言うが、後からの
  追加/分割が全スライドを再触りする点を flag していない。組み立て時の一括置換ステップを 1 つ文書化すれば非問題化する。

---

## Cross-cutting themes（反映プランの軸）

- **T1 — テンプレが SKILL の mandate に lag（F6 ＋ F8）**：`02`/`03` テンプレが、SKILL の ⚠️/ゲートが要求する構造
  （移行チェックリスト・プラットフォーム実態ゲート・基盤分岐・役割別突合）のスロットを欠く。Fix ＝空スキャフォルドを
  足して取りこぼせなくする。
- **T2 — パーツの 3 層対応（変種・長さ予算）と組み立て機構（F11 ＋ F13 ＋ F14）**：`work-detail` の pre-split ペア／
  `estimate.compare` 注記の長さ予算／ページ総数の組み立て時一括置換の文書化（F14 の fix はパーツでなく outline 側）。
- **T3 — SKILL のエッジケース指針の穴（F1 ＋ F2 ＋ F4 ＋ F5 ＋ F7 ＋ F12）**：no-stated-count／標準トピックの
  fan-out／アンカー単一ページの IA 膨張／SaaS 価格の課金条件＋一次ページ読めない時の代替／QC 軸対各行レビューの重複／
  title は組み立て fill の注記。すべて一〜二行の追記で、構造変更なし。

---

## 反映方針（reflection plan）

**全所見は additive**：一〜二行の指針追記／テンプレのスキャフォルド／パーツ変種、のいずれか。**phase/parts モデルの
構造的な作り直しは一切含意しない**（task #10 のモデルは end-to-end で検証済み）。優先度は **followup＝フォローアップの
plugin タスクとして実施／minor＝機会があれば畳み込む** で区別。

### → SKILL.md（`hposal/skills/up/SKILL.md`）

| 所見 | HOW（一行） | 優先 |
|---|---|---|
| F1 | Phase 1 のカウント突合に「申告が無い場合は印象/ナビ対 実カウントを差分として記録」を 1 行追記 | followup |
| F2 | 標準トピックは複数 q に割れてよい（⑤ 例）を 1 行注記 | minor |
| F4 | アンカー型単一ページの ⚠️：可視セクションが将来ページになり新 IA が母数から膨らむ | followup |
| F5 | SaaS 月額は課金条件で変わる＝どの一次figureが canonical か／一次ページ不読時の代替を 1 行 | followup |
| F7 | QC 軸はマトリクスのセルをテスト実行行に向け、各行 review と二重計上しない、を 1 行 | minor |
| F9 | レンジ下限は「行を段階的に落とす」結果で「提示額の丸め」ではない、を 1 行 | minor |

### → テンプレ（`hposal/references/templates/`）— T1

| 所見 | WHERE | HOW（一行） | 優先 |
|---|---|---|---|
| F6 | `02_proposal-design.md` | 移行標準作業チェックリスト表＋プラットフォーム実態ゲート表の空スキャフォルドを足す | followup |
| F8 | `03_work-breakdown.md` | 「共通 1 回＋基盤分岐＋基盤ごと総額」と役割別突合表の空骨格を足す | followup |

### → パーツ（`hposal/references/templates/parts/`）— T2

| 所見 | WHERE | HOW（一行） | 優先 |
|---|---|---|---|
| F11 | `work-detail.common.html` / `work-detail.branch.html` | estimate の変種に倣った pre-split ペアを新設 | followup |
| F13 | `estimate.compare.html` | デフォルト注記を短く、または height-budget ヒントをコメントで添える | minor |

### → アウトライン（`04_proposal.md`）

| 所見 | HOW（一行） | 優先 |
|---|---|---|
| F12 | `<title>` の `{{案件名}}` は組み立て時 fill（CSS はバイト不変・title だけ埋める）を明記 | followup |
| F14 | 後からの追加/分割は `{{総ページ数}}` を全スライド再触り＝組み立て時の一括置換ステップを 1 つ文書化 | minor |
| F11 | スロット 20（work-detail）の変種選択に common/branch ペアを反映（パーツ新設に合わせて） | followup |

### → README

該当なし（利用者の読み物に直接効く所見は今回なし）。

### → execution-only（変更なし）

| 所見 | 理由 |
|---|---|
| F10 | 起草 subagent の Write 事故。プラグイン欠陥ではない。export grep ゲートの存在価値の裏付けに留める | 変更なし |
| F3 | 実行側が正しく処理（q ＋前方ポインタ）。明示するなら F5 系の P1/P2 注記に畳み込む程度 | minor |

**backlog の読み方**：followup ＝ 次の plugin タスクで束ねて実施（T1 のテンプレ 2 本・T2 の work-detail ペア・
SKILL の F1/F4/F5・outline の F12 が芯）。minor ＝ 隣接編集のついでに畳み込む。

---

## Positives / 何が効いたか

task #10 のパーツモデルが、実在の 3 層案件で機能した。具体的に効いた仕組み：

- **export residue grep ゲート**（`{{`/見本残留 0）と **byte-identical-CSS ルール**（`_head.html` と diff 空）が
  実際に仕事をした。F10 の tool タグ漏れも、末尾チェックの価値を裏付けた。
- **機械突合**（明細合計＝役割別小計の再加算一致）が両基盤分岐で一致を確認＝ゲートが効くことを実証。
- **fill-marker 規約**（人間が後で埋める値は `（…）`/`※`、AI fill は `{{ }}`）が摩擦なく機能。
- **SKILL の Wix/301/toC/基盤未定 ⚠️** が、no-robots-Sitemap・wixsite-301-infeasible・toC-legal・基盤未定の
  落とし穴をすべて捕捉。
- 3 層 compare パーツが `02` の基盤分岐モデルと `03` の基盤別総額に素直に対応し、as-is/to-be.single・画面 2 変種・
  fill-marker が摩擦なく嵌まった ＝ **#10 のパーツモデルを実 3 層案件で end-to-end 検証**できた。
