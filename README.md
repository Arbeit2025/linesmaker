# セリフメーカー（linesmaker）

喫茶店の店員「ココア」のセリフを、パーツ（呼びかけ／本文／締め）を
スロットのように組み合わせて作れるメーカー系 Web ツールです。

## できること

- パーツは「呼びかけ」「本文」「締め」が各12種（合計 12×12×12 = 1,728 通り）
- プルダウンで選んでも、「🎲 ランダム」ボタンでも作れます
- 組み上がったセリフは大きなプレビューと、コピー用テキストエリアに表示
- 「今日のセリフ」：日付シードで決まる、その日だけの1件を表示

## 構成

- 単一ファイル Flask アプリ（`app.py`）。DB は使わず、セリフのパーツは
  `app.py` 内の定数です
- 画面は `render_template_string` で `app.py` に埋め込み

## ローカル起動

```bash
pip install -r requirements.txt
python app.py
# http://localhost:5000
```

本番相当の起動：

```bash
gunicorn app:app
```

## テスト

```bash
python -m unittest discover -s tests
```

## デプロイ

Render の Web Service（Free）を想定し、`render.yaml` を同梱しています
（start: `gunicorn app:app`、ヘルスチェックは `/healthz`）。
