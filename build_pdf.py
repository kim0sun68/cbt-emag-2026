#!/usr/bin/env python3
"""회차별 문제집(시험지)·해설서 인쇄 HTML을 생성하고 headless Chrome으로 PDF 변환한다.

사용: python3 build_pdf.py          # 전체 회차
      python3 build_pdf.py 1회      # 특정 회차만
출력: pdf/2026_전기기사_<회차>_문제집.pdf, pdf/2026_전기기사_<회차>_해설서.pdf
"""
import json, pathlib, subprocess, sys, base64, io, shutil

root = pathlib.Path(__file__).parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 회차 → [(json, 과목번호, 정식 과목명)] — 순서 고정. 없는 과목은 None.
ROUNDS = {
    "1회": [("emag1", "제1과목", "전기자기학"), ("power1", "제2과목", "전력공학"),
            ("kigi1", "제3과목", "전기기기"), ("circuit1", "제4과목", "회로이론 및 제어공학"),
            ("kec1", "제5과목", "전기설비기술기준")],
    "2회": [("emag2", "제1과목", "전기자기학"), None,  # 전력공학 2회 영상 미확보
            ("kigi2", "제3과목", "전기기기"), ("circuit", "제4과목", "회로이론 및 제어공학"),
            ("kec2", "제5과목", "전기설비기술기준")],
    "3회": [("content", "제1과목", "전기자기학"), ("power", "제2과목", "전력공학"),
            ("kigi", "제3과목", "전기기기"), ("circuit3", "제4과목", "회로이론 및 제어공학"),
            ("kec", "제5과목", "전기설비기술기준")],
}
CIRCLED = "①②③④"

KATEX = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<script>window.addEventListener('load',()=>renderMathInElement(document.body,
  {delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],throwOnError:false}));</script>"""

BASE_CSS = """
@page { size: A4; margin: 14mm 12mm 16mm; }
* { box-sizing: border-box; }
body { font-family:'Apple SD Gothic Neo','Malgun Gothic',sans-serif; font-size:9.5pt; line-height:1.5; color:#111; margin:0; }
.cover { height: 250mm; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; page-break-after: always; }
.cover h1 { font-size:26pt; margin:4mm 0; }
.cover .sub { font-size:13pt; color:#333; }
.cover .box { border:2px solid #111; padding:8mm 14mm; margin-top:12mm; font-size:11pt; text-align:left; }
.subject-head { page-break-before: always; border-bottom:2.5px solid #111; padding-bottom:2mm; margin-bottom:4mm;
  display:flex; justify-content:space-between; align-items:flex-end; }
.subject-head h2 { font-size:14pt; margin:0; }
.subject-head .meta { font-size:8.5pt; color:#444; text-align:right; }
.katex { font-size: 1.02em; }
footer-note { display:block; text-align:center; color:#777; font-size:8pt; margin-top:6mm; }
"""

EXAM_CSS = BASE_CSS + """
.qwrap { column-count:2; column-gap:8mm; column-rule:0.4pt solid #bbb; }
.q { break-inside: avoid; margin-bottom:4.5mm; }
.qno { font-weight:800; }
.choices { margin:1mm 0 0 1mm; padding:0; list-style:none; }
.choices li { margin:0.6mm 0; }
.omr { page-break-before: always; }
.omr h2 { font-size:13pt; border-bottom:2px solid #111; padding-bottom:2mm; }
.omr table { border-collapse:collapse; width:100%; margin-top:3mm; }
.omr th,.omr td { border:0.5pt solid #333; text-align:center; font-size:8.5pt; padding:1mm 0.5mm; }
.omr th { background:#eee; }
.omr .c { color:#999; letter-spacing:1px; }
"""

SOL_CSS = BASE_CSS + """
.anstab table { border-collapse:collapse; width:100%; margin-top:3mm; }
.anstab th,.anstab td { border:0.5pt solid #333; text-align:center; font-size:9pt; padding:1.2mm 0.5mm; }
.anstab th { background:#eee; }
.s { border-bottom:0.4pt solid #ccc; padding:2.5mm 0; break-inside: avoid; }
.s .h { font-weight:800; }
.s .ans { color:#0a5a2a; font-weight:800; }
.s .ts { color:#555; font-size:8.5pt; }
.s .sol { margin:1mm 0; white-space:pre-wrap; }
.s .th { background:#f1f5fb; border-left:2.5px solid #1256a2; padding:1.5mm 2.5mm; white-space:pre-wrap; font-size:8.8pt; margin-top:1mm; }
.qr { width:22mm; height:22mm; }
"""

def qr_datauri(url):
    import segno
    buf = io.BytesIO()
    segno.make(url).save(buf, kind="png", scale=6, border=1)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")

def bold(s):
    out, parts = esc(s), []
    while "**" in out:
        a, _, rest = out.partition("**")
        b, _, out = rest.partition("**")
        parts.append(a + "<b>" + b + "</b>")
    return "".join(parts) + out

def mmss(sec):
    return f"{sec//60}:{sec%60:02d}"

def load_round(rnd):
    subs = []
    for entry in ROUNDS[rnd]:
        if entry is None:
            continue
        f, no, name = entry
        d = json.loads((root / "content" / f"{f}.json").read_text(encoding="utf-8"))
        subs.append({"no": no, "name": name, "vid": d["videoId"], "qs": d["questions"]})
    return subs

def cover(rnd, kind, subs):
    rows = "".join(f"<div>{s['no']} {s['name']} — 20문제</div>" for s in subs)
    note = "" if len(subs) == 5 else "<div style='color:#a00'>※ 제2과목 전력공학은 자료 확보 후 추가 예정</div>"
    return f"""<div class="cover"><div class="sub">2026년 {rnd} 전기기사 필기 CBT 기출</div>
<h1>{kind}</h1><div class="sub">총 {len(subs)}과목 · {20*len(subs)}문제</div>
<div class="box">{rows}{note}<div style="margin-top:4mm;color:#555">출처: 대산전기학원 유튜브 기출 해설 강의 · 학습용 정리 자료</div></div></div>"""

def build_exam(rnd, subs):
    body = [cover(rnd, "문제집", subs)]
    for s in subs:
        body.append(f'<div class="subject-head"><h2>{s["no"]} {s["name"]}</h2><div class="meta">20문제</div></div><div class="qwrap">')
        for q in s["qs"]:
            ch = "".join(f"<li>{bold(c)}</li>" for c in q["choices"])
            body.append(f'<div class="q"><span class="qno">{q["no"]}.</span> {bold(q["question"])}<ul class="choices">{ch}</ul></div>')
        body.append("</div>")
    # OMR 마킹표
    rows = []
    for i in range(20):
        cells = "".join(f'<td class="c">{" ".join(CIRCLED)}</td>' for _ in subs)
        rows.append(f"<tr><th>{i+1}</th>{cells}</tr>")
    heads = "".join(f"<th>{s['name']}</th>" for s in subs)
    body.append(f'<div class="omr"><h2>정답 마킹표</h2><table><tr><th>문번</th>{heads}</tr>{"".join(rows)}</table>'
                f'<footer-note>채점은 별권 「해설서」의 정답 일람표를 사용하세요.</footer-note></div>')
    return f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">{KATEX}<style>{EXAM_CSS}</style></head><body>{"".join(body)}</body></html>'

def build_sol(rnd, subs):
    body = [cover(rnd, "해설서", subs)]
    # 정답 일람표
    rows = []
    for i in range(20):
        cells = "".join(f"<td>{CIRCLED[s['qs'][i]['answerIndex']]}</td>" for s in subs)
        rows.append(f"<tr><th>{i+1}</th>{cells}</tr>")
    heads = "".join(f"<th>{s['name']}</th>" for s in subs)
    body.append(f'<div class="anstab"><h2 style="font-size:13pt;border-bottom:2px solid #111;padding-bottom:2mm">정답 일람표</h2>'
                f'<table><tr><th>문번</th>{heads}</tr>{"".join(rows)}</table></div>')
    for s in subs:
        url = f"https://youtu.be/{s['vid']}"
        body.append(f'<div class="subject-head"><h2>{s["no"]} {s["name"]} 해설</h2>'
                    f'<div class="meta">원본 강의 QR<br><img class="qr" src="{qr_datauri(url)}"><br>{url}</div></div>')
        for q in s["qs"]:
            body.append(f'<div class="s"><div class="h">{q["no"]}. {bold(q["question"])}</div>'
                        f'<div><span class="ans">정답 {CIRCLED[q["answerIndex"]]}</span> '
                        f'<span class="ts">▶ 영상 해설 {mmss(q["timestampSec"])}</span></div>'
                        f'<div class="sol">{bold(q["solution"])}</div><div class="th">{bold(q["theory"])}</div></div>')
    return f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">{KATEX}<style>{SOL_CSS}</style></head><body>{"".join(body)}</body></html>'

def to_pdf(html_path, pdf_path):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=25000", f"--print-to-pdf={pdf_path}",
                    html_path.as_uri()], check=True, capture_output=True)

def main():
    targets = sys.argv[1:] or list(ROUNDS)
    out = root / "pdf"; tmp = root / "print_tmp"
    out.mkdir(exist_ok=True); tmp.mkdir(exist_ok=True)
    for rnd in targets:
        subs = load_round(rnd)
        for kind, builder in [("문제집", build_exam), ("해설서", build_sol)]:
            h = tmp / f"{rnd}_{kind}.html"
            h.write_text(builder(rnd, subs), encoding="utf-8")
            p = out / f"2026_전기기사_{rnd}_{kind}.pdf"
            to_pdf(h, p)
            print(p.name, f"{p.stat().st_size//1024}KB")
    shutil.rmtree(tmp)

if __name__ == "__main__":
    main()
