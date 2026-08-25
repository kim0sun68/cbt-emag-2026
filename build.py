#!/usr/bin/env python3
"""content/content.json을 인라인으로 넣어 단일 index.html을 생성한다."""
import json, pathlib

root = pathlib.Path(__file__).parent

# (json, out, 과목명, 회차) — 그룹별 레지스트리
KISA = [
    ("emag1.json", "emag1.html", "전자기학", "1회"),
    ("emag2.json", "emag2.html", "전자기학", "2회"),
    ("content.json", "index.html", "전자기학", "3회"),
    ("power1.json", "power1.html", "전력공학", "1회"),
    ("power2.json", "power2.html", "전력공학", "2회"),
    ("power.json", "power.html", "전력공학", "3회"),
    ("kigi1.json", "kigi1.html", "전기기기", "1회"),
    ("kigi2.json", "kigi2.html", "전기기기", "2회"),
    ("kigi.json", "kigi.html", "전기기기", "3회"),
    ("circuit1.json", "circuit1.html", "회로이론·제어", "1회"),
    ("circuit.json", "circuit.html", "회로이론·제어", "2회"),
    ("circuit3.json", "circuit3.html", "회로이론·제어", "3회"),
    ("kec1.json", "kec1.html", "설비기술기준", "1회"),
    ("kec2.json", "kec2.html", "설비기술기준", "2회"),
    ("kec.json", "kec.html", "설비기술기준", "3회"),
]
SANUP = [
    ("semag3.json", "semag3.html", "전자기학", "3회"),
    ("sanup1.json", "sanup1.html", "회로이론", "1회"),
    ("sanup2.json", "sanup2.html", "회로이론", "2회"),
    ("skec1.json", "skec1.html", "설비기술기준", "1회"),
    ("skec2.json", "skec2.html", "설비기술기준", "2회"),
    ("skec3.json", "skec3.html", "설비기술기준", "3회"),
]
GROUPS = [("전기기사", KISA), ("산업기사", SANUP)]
# 정식 과목명과 과목 번호 (실제 영상 제목 형식에 맞춤)
OFFICIAL = {
    ("전기기사", "전자기학"): ("제1과목", "전기자기학"),
    ("전기기사", "전력공학"): ("제2과목", "전력공학"),
    ("전기기사", "전기기기"): ("제3과목", "전기기기"),
    ("전기기사", "회로이론·제어"): ("제4과목", "회로이론 및 제어공학"),
    ("전기기사", "설비기술기준"): ("제5과목", "전기설비기술기준"),
    ("산업기사", "전자기학"): ("제1과목", "전기자기학"),
    ("산업기사", "회로이론"): ("제4과목", "회로이론"),
    ("산업기사", "설비기술기준"): ("제5과목", "전기설비기술기준"),
}

def make_nav(current):
    rows = []
    for gname, entries in GROUPS:
        subjects = []
        seen = []
        for _, out, subj, r in entries:
            if subj not in seen:
                seen.append(subj)
        for subj in seen:
            pills = []
            for _, out, s, r in entries:
                if s != subj:
                    continue
                cls = "pill cur" if out == current else "pill"
                pills.append(f'<a class="{cls}" href="{out}">{r}</a>')
            subjects.append(f'<span class="navsub"><span class="subj">{subj}</span>{"".join(pills)}</span>')
        rows.append(f'<div class="navrow"><span class="navgroup">{gname}</span><div class="navitems">{"".join(subjects)}</div></div>')
    return "".join(rows)

PAGES = []
for gname, entries in GROUPS:
    exam = "전기기사" if gname == "전기기사" else "전기산업기사"
    for j, out, subj, r in entries:
        no, full = OFFICIAL[(gname, subj)]
        PAGES.append({
            "json": j, "out": out,
            "title": f"2026년 {r} {exam} 필기 {full} — 기출 핵심풀이",
            "video_label": f"대산전기학원 — 2026년 {r} {exam} 필기 CBT 기출적중 핵심풀이 {no} {full}",
            "nav": make_nav(out),
        })

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
  .subnav { margin-top:12px; border-top:1px solid var(--line); padding-top:10px; }
  .navrow { display:flex; align-items:flex-start; gap:8px; margin:6px 0; }
  .navgroup { flex:0 0 auto; font-size:.78rem; font-weight:800; color:#fff; background:var(--blue); border-radius:6px; padding:3px 8px; margin-top:2px; }
  .navitems { display:flex; flex-wrap:wrap; gap:6px 14px; }
  .navsub { display:inline-flex; align-items:center; gap:4px; white-space:nowrap; }
  .subj { font-size:.8rem; color:#666; margin-right:2px; }
  .pill { display:inline-block; font-size:.8rem; padding:2px 9px; border:1px solid var(--line); border-radius:999px; text-decoration:none; color:var(--blue); background:#fafbfc; }
  .pill:hover { border-color:var(--blue); }
  .pill.cur { background:var(--blue); color:#fff; border-color:var(--blue); font-weight:700; }
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
    <nav class="subnav">__NAV__</nav>
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
            .replace("__TITLE__", page["title"])
            .replace("__VIDEOID__", data["videoId"])
            .replace("__VIDEOLABEL__", page["video_label"])
            .replace("__NAV__", page["nav"])
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    (root / page["out"]).write_text(html, encoding="utf-8")
    print(page["out"], "written:", len(html), "bytes")
