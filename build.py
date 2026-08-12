#!/usr/bin/env python3
"""content/content.json을 인라인으로 넣어 단일 index.html을 생성한다."""
import json, pathlib

root = pathlib.Path(__file__).parent

SUBJECTS = [
    ("content.json", "index.html", "전기자기학"),
    ("power.json", "power.html", "전력공학"),
    ("kigi.json", "kigi.html", "전기기기"),
    ("kec.json", "kec.html", "전기설비기술기준"),
]
PAGES = [
    {"json": j, "out": out,
     "video_label": f"대산전기학원 — 2026년 3회 전기기사 필기 CBT 기출적중 핵심풀이 ({name})",
     "nav": "다른 과목: " + " · ".join(
         f'<a href="{o}">{n} →</a>' for _, o, n in SUBJECTS if o != out)}
    for j, out, name in SUBJECTS
]

TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<style>
  :root { --green:#1a7f37; --red:#c62828; --blue:#1256a2; --bg:#f5f6f8; --card:#fff; --line:#e0e3e8; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:'Apple SD Gothic Neo','Malgun Gothic',sans-serif; background:var(--bg); color:#222; line-height:1.65; }
  .wrap { max-width:720px; margin:0 auto; padding:16px 14px 80px; }
  header { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:20px 18px; margin-bottom:18px; }
  header h1 { font-size:1.25rem; margin:0 0 8px; }
  header p { margin:4px 0; font-size:.9rem; color:#555; }
  header a { color:var(--blue); }
  #score { position:sticky; top:0; z-index:10; background:var(--blue); color:#fff; border-radius:0 0 10px 10px; padding:8px 14px; font-weight:700; text-align:center; margin:-16px -14px 16px; font-size:.95rem; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:18px 16px; margin-bottom:16px; }
  .qno { font-weight:800; color:var(--blue); margin-bottom:6px; }
  .qtext { margin-bottom:12px; font-weight:600; }
  .choice { display:block; width:100%; text-align:left; background:#fafbfc; border:1.5px solid var(--line); border-radius:9px; padding:10px 12px; margin:6px 0; font-size:.95rem; font-family:inherit; cursor:pointer; line-height:1.6; }
  .choice:hover { border-color:var(--blue); }
  .choice.correct { border-color:var(--green); background:#e8f5e9; font-weight:700; }
  .choice.wrong { border-color:var(--red); background:#ffebee; }
  .choice:disabled { cursor:default; opacity:1; color:inherit; }
  .mark { float:right; font-weight:800; }
  .mark.ok { color:var(--green); } .mark.no { color:var(--red); }
  .toggle { margin-top:10px; background:none; border:1px solid var(--blue); color:var(--blue); border-radius:8px; padding:7px 14px; font-size:.88rem; cursor:pointer; font-family:inherit; }
  .expl { display:none; margin-top:14px; border-top:1px dashed var(--line); padding-top:12px; font-size:.93rem; }
  .expl.open { display:block; }
  .answer-line { font-weight:800; color:var(--green); margin-bottom:8px; }
  .sol { white-space:pre-wrap; margin-bottom:12px; }
  .theory { background:#f2f7ff; border-left:4px solid var(--blue); border-radius:0 8px 8px 0; padding:10px 12px; white-space:pre-wrap; margin-bottom:12px; }
  .ytlink { display:inline-block; background:#c4302b; color:#fff; text-decoration:none; border-radius:8px; padding:8px 14px; font-size:.88rem; font-weight:700; }
  footer { text-align:center; color:#888; font-size:.8rem; margin-top:30px; }
  @media (max-width:480px){ .wrap{padding:12px 10px 60px;} .card{padding:14px 12px;} }
</style>
</head>
<body>
<div class="wrap">
  <div id="score"></div>
  <header>
    <h1>__TITLE__</h1>
    <p>보기를 클릭하면 채점되고 해설이 열립니다. 채점 없이 보려면 [해설 보기]를 누르세요.</p>
    <p>원본 강의: <a href="https://www.youtube.com/watch?v=__VIDEOID__" target="_blank" rel="noopener">__VIDEOLABEL__</a></p>
    <p>__NAV__</p>
  </header>
  <div id="app"></div>
  <footer>출처: 대산전기학원 유튜브 강의 · 학습용 정리 자료</footer>
</div>
<script id="data" type="application/json">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const marks = ['①','②','③','④'];
let answered = 0, correct = 0;

function updateScore(){
  document.getElementById('score').textContent =
    `정답 ${correct} / 푼 문제 ${answered} / 전체 ${DATA.questions.length}`;
}

function mdBold(s){
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;')
          .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
}

const app = document.getElementById('app');
DATA.questions.forEach(q => {
  const card = document.createElement('div');
  card.className = 'card';
  const ts = q.timestampSec;
  card.innerHTML = `
    <div class="qno">문제 ${q.no}</div>
    <div class="qtext">${mdBold(q.question)}</div>
    <div class="choices"></div>
    <button class="toggle">해설 보기</button>
    <div class="expl">
      <div class="answer-line">정답: ${marks[q.answerIndex]}</div>
      <div class="sol">${mdBold(q.solution)}</div>
      <div class="theory">${mdBold(q.theory)}</div>
      <a class="ytlink" href="https://youtu.be/${DATA.videoId}?t=${ts}" target="_blank" rel="noopener">▶ 영상 해설 바로가기 (${Math.floor(ts/60)}:${String(ts%60).padStart(2,'0')})</a>
    </div>`;
  const choicesBox = card.querySelector('.choices');
  const expl = card.querySelector('.expl');
  let done = false;
  q.choices.forEach((c, i) => {
    const b = document.createElement('button');
    b.className = 'choice';
    b.innerHTML = mdBold(c);
    b.addEventListener('click', () => {
      if (done) return;
      done = true;
      answered++;
      const btns = choicesBox.querySelectorAll('.choice');
      btns.forEach(x => x.disabled = true);
      if (i === q.answerIndex) {
        correct++;
        b.classList.add('correct');
        b.insertAdjacentHTML('beforeend','<span class="mark ok">✓</span>');
      } else {
        b.classList.add('wrong');
        b.insertAdjacentHTML('beforeend','<span class="mark no">✗</span>');
        btns[q.answerIndex].classList.add('correct');
      }
      expl.classList.add('open');
      updateScore();
    });
    choicesBox.appendChild(b);
  });
  card.querySelector('.toggle').addEventListener('click', () => {
    expl.classList.toggle('open');
  });
  app.appendChild(card);
});
updateScore();

document.addEventListener('DOMContentLoaded', () => {
  const tryRender = () => {
    if (window.renderMathInElement) {
      renderMathInElement(document.body, {
        delimiters: [{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],
        throwOnError: false
      });
    } else setTimeout(tryRender, 100);
  };
  tryRender();
});
</script>
</body>
</html>
"""

for page in PAGES:
    data = json.loads((root / "content" / page["json"]).read_text(encoding="utf-8"))
    html = (TEMPLATE
            .replace("__TITLE__", data["title"])
            .replace("__VIDEOID__", data["videoId"])
            .replace("__VIDEOLABEL__", page["video_label"])
            .replace("__NAV__", page["nav"])
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    (root / page["out"]).write_text(html, encoding="utf-8")
    print(page["out"], "written:", len(html), "bytes")
