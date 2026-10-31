# -*- coding: utf-8 -*-
"""
linesmaker（セリフメーカー）

キャラクター「ココア」（明るく親しみやすい成人女性の喫茶店員イメージ）の
セリフを、パーツ（呼びかけ／本文／締め）をスロットのように組み合わせて
作れるメーカー系ツール。単一ファイル Flask、DB なし。

目次
  1. セリフパーツ（定数）
  2. セリフ生成ロジック
  3. 画面テンプレート
  4. ルート
"""

from __future__ import annotations

import hashlib
import random
from datetime import date

from flask import Flask, request, render_template_string

app = Flask(__name__)

# ==============================
# 1. セリフパーツ（定数）
# ==============================

OPENINGS = [
    "ねえねえ、",
    "あのね、",
    "ふふ、",
    "おはよう！ ",
    "おかえりなさい！ ",
    "いらっしゃいませ！ ",
    "聞いて聞いて、",
    "今日も一日、",
    "ほらほら、",
    "大好きなあなたへ、",
    "こんにちは！ ",
    "お疲れさま、",
]

BODIES = [
    "今日のおすすめは、とっておきのブレンドだよ",
    "温かいココアで、ほっと一息つかない？",
    "あなたの笑顔が見たくて、ケーキを多めに焼いちゃった",
    "頑張ってる姿、ちゃんと見てるからね",
    "無理しすぎたら、あたしが止めちゃうよ？",
    "紅茶の香りって、なんだか心がほどけるよね",
    "雨の日は静かで、こんな時間も悪くないなって思うの",
    "勉強も仕事も、休み休みがちょうどいいんだよ",
    "あなたの席、いつもの場所に用意してあるよ",
    "たまには甘いもので、自分を甘やかしてあげて",
    "新しい豆が届いたんだ。今度一緒に味見しようね",
    "悩みがあったら聞くよ。ココアを淹れながらでよければ",
]

ENDINGS = [
    "。",
    "！",
    "♪",
    "。待ってるね。",
    "。いつでもおいで。",
    "。ね？",
    "。ふふふ。",
    "！ 約束だよ。",
    "。あたしがついてるから。",
    "♪ しあわせだね。",
    "。また明日も会おうね。",
    "。大好きだよ。",
]

PARTS = (OPENINGS, BODIES, ENDINGS)

# ==============================
# 2. セリフ生成ロジック
# ==============================


def _clamp(index: int, size: int) -> int:
    return max(0, min(int(index), size - 1))


def build_line(opening_i: int, body_i: int, ending_i: int) -> str:
    """パーツのインデックスを指定してセリフを組み立てる。"""
    o = OPENINGS[_clamp(opening_i, len(OPENINGS))]
    b = BODIES[_clamp(body_i, len(BODIES))]
    e = ENDINGS[_clamp(ending_i, len(ENDINGS))]
    return f"{o}{b}{e}"


def random_indices(rng: random.Random | None = None) -> tuple[int, int, int]:
    """ランダムなパーツのインデックス3つを返す。rng を渡すと再現可能。"""
    r = rng if rng is not None else random
    return (
        r.randrange(len(OPENINGS)),
        r.randrange(len(BODIES)),
        r.randrange(len(ENDINGS)),
    )


def random_line(rng: random.Random | None = None) -> str:
    """ランダムなセリフを1件返す。rng を渡すと再現可能。"""
    return build_line(*random_indices(rng))


def todays_indices(d: date | None = None) -> tuple[int, int, int]:
    """日付シードで決まる「今日のセリフ」のインデックス（同じ日は同じ結果）。"""
    target = d if d is not None else date.today()
    digest = hashlib.sha256(target.isoformat().encode("utf-8")).hexdigest()
    rng = random.Random(int(digest[:16], 16))
    return random_indices(rng)


def todays_line(d: date | None = None) -> str:
    """日付シードで決まる「今日のセリフ」を返す。"""
    return build_line(*todays_indices(d))


# ==============================
# 3. 画面テンプレート
# ==============================

PAGE = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>セリフメーカー｜ココア</title>
<style>
  body { font-family: "Hiragino Maru Gothic ProN", "Hiragino Sans", sans-serif;
         background: #fff7ee; color: #5b4636; margin: 0; padding: 24px 12px 48px; }
  .card { max-width: 640px; margin: 0 auto 20px; background: #fff; border-radius: 16px;
          box-shadow: 0 2px 10px rgba(160,110,60,.15); padding: 20px 22px; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  h2 { font-size: 16px; margin: 0 0 10px; color: #a9713f; }
  .sub { color: #9a7c5f; font-size: 13px; margin-bottom: 8px; }
  label { display: block; font-size: 13px; margin: 12px 0 4px; color: #a9713f; }
  select { width: 100%; font-size: 15px; padding: 8px; border: 1px solid #e5cdb2;
           border-radius: 8px; background: #fffdf8; }
  .preview { font-size: 24px; line-height: 1.6; background: #fff3e2; border-radius: 12px;
             padding: 18px; min-height: 64px; }
  textarea { width: 100%; font-size: 15px; padding: 10px; border: 1px solid #e5cdb2;
             border-radius: 8px; box-sizing: border-box; background: #fffdf8; }
  .row { display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap; }
  button, .btn { font-size: 15px; padding: 10px 18px; border: 0; border-radius: 999px;
                 background: #d98e4a; color: #fff; cursor: pointer; text-decoration: none; }
  .btn.sub2 { background: #b08968; }
  .today { font-size: 19px; line-height: 1.6; }
  .note { font-size: 12px; color: #9a7c5f; margin-top: 10px; }
</style>
</head>
<body>
  <div class="card">
    <h1>☕ セリフメーカー</h1>
    <div class="sub">喫茶店のココアのセリフを、パーツを組み合わせて作れるメーカーです。</div>
    <div class="preview" id="preview">{{ line }}</div>
    <label for="copybox">コピー用（このままコピーできます）</label>
    <textarea id="copybox" rows="3" readonly>{{ line }}</textarea>
    <form method="get" action="/">
      <label for="o">呼びかけ</label>
      <select id="o" name="o">
        {% for p in openings %}<option value="{{ loop.index0 }}" {% if loop.index0 == sel[0] %}selected{% endif %}>{{ p }}</option>{% endfor %}
      </select>
      <label for="b">本文</label>
      <select id="b" name="b">
        {% for p in bodies %}<option value="{{ loop.index0 }}" {% if loop.index0 == sel[1] %}selected{% endif %}>{{ p }}</option>{% endfor %}
      </select>
      <label for="e">締め</label>
      <select id="e" name="e">
        {% for p in endings %}<option value="{{ loop.index0 }}" {% if loop.index0 == sel[2] %}selected{% endif %}>{{ p }}</option>{% endfor %}
      </select>
      <div class="row">
        <button type="submit">この組み合わせで作る</button>
        <a class="btn sub2" href="/?random=1">🎲 ランダム</a>
      </div>
    </form>
    <div class="note">組み合わせは {{ total }} 通りあります。</div>
  </div>
  <div class="card">
    <h2>🌞 今日のセリフ（{{ today_str }}）</h2>
    <div class="today">{{ today_line }}</div>
    <div class="note">日付で決まる1件です。明日になると変わります。</div>
  </div>
</body>
</html>
"""

# ==============================
# 4. ルート
# ==============================


def _parse_index(name: str, size: int) -> int | None:
    raw = request.args.get(name)
    if raw is None:
        return None
    try:
        return _clamp(int(raw), size)
    except (TypeError, ValueError):
        return None


@app.route("/", methods=["GET"])
def index():
    if request.args.get("random"):
        sel = random_indices()
    else:
        sel = (
            _parse_index("o", len(OPENINGS)),
            _parse_index("b", len(BODIES)),
            _parse_index("e", len(ENDINGS)),
        )
        if any(v is None for v in sel):
            sel = todays_indices()
    line = build_line(*sel)
    today = date.today()
    return render_template_string(
        PAGE,
        line=line,
        sel=sel,
        openings=OPENINGS,
        bodies=BODIES,
        endings=ENDINGS,
        total=len(OPENINGS) * len(BODIES) * len(ENDINGS),
        today_line=todays_line(today),
        today_str=today.strftime("%Y年%m月%d日"),
    )


@app.route("/healthz", methods=["GET"])
def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
