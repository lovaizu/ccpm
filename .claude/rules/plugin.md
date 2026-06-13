# プラグイン作成ルール（ccpm）

出典: 公式docs（code.claude.com/docs の plugins-reference / plugin-marketplaces / skills）で確認した事実に基づく。

## バージョン番号

- **version は plugin.json の1箇所だけに書く。** marketplace.json には version を書かない。
  - 解決順は `plugin.json` → marketplace entry → git commit SHA。**両方にあると plugin.json が勝つ**ので marketplace entry の version は重複・無意味。
  - marketplace 最上位の version は「マニフェストのメタ情報」で、利用者の更新検知には使われない。
- **plugin.json には version を必ず入れる**（semver。例 `0.1.0`）。
  - `claude plugin validate --strict` は version 未指定だと警告→失敗するため。
- **意味（利用者観点）**：version を固定すると、利用者は **bump した時だけ**更新を受け取る。リリースごとに version を上げる。
  - 省略すると毎コミットが新版扱い（commit-SHA 戦略、活発な開発中向け）だが、`--strict` を通すため本リポジトリでは plugin.json に version を置く方針。

## 検証ゲート

- 構造検証は `claude plugin validate <plugin-path> --strict` と `claude plugin validate <marketplace-root> --strict` の両方を通す。
- 挙動確認は headless で行う：`claude -p "/<plugin>:<skill>" --plugin-dir <plugin-path>`（skill 名前空間 = プラグイン名）。
