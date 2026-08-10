# 전자기학 3회 기출 웹 문서 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 유튜브 영상(BlGWW66ZRaY)의 전기기사 전자기학 3회 기출문제·해설을 단일 페이지 HTML(정답 판정 인터랙션 포함)로 만들어 GitHub Pages에 배포한다.

**Architecture:** 콘텐츠(문제/해설/타임스탬프)를 먼저 `content.json`으로 추출·정리하고, PDF에서 미니 이론 정리를 추가한 뒤, 정적 `index.html`이 이 데이터를 인라인으로 품고 렌더링한다. 외부 의존성은 KaTeX CDN뿐.

**Tech Stack:** 순수 HTML/CSS/JS 단일 파일, KaTeX(CDN), watch 스킬(yt-dlp/ffmpeg), GitHub Pages

## Global Constraints

- 단일 파일 `index.html` (콘텐츠 데이터는 파일 내 인라인 `<script>` JSON)
- 외부 의존성은 KaTeX CDN만 허용
- 모바일 반응형 필수
- 타임스탬프 링크 형식: `https://youtu.be/BlGWW66ZRaY?t=<초>`
- 626MB PDF는 `.gitignore`로 커밋 제외 (이미 설정됨)
- GitHub 저장소 생성·공개 배포 직전에 사용자 확인 필수

---

### Task 1: 영상에서 문제·해설·타임스탬프 추출

**Files:**
- Create: `content/content.json`

**Interfaces:**
- Produces: `content/content.json` — 스키마:

```json
{
  "title": "2026 전기기사 전자기학 3회 기출",
  "videoId": "BlGWW66ZRaY",
  "questions": [
    {
      "no": 1,
      "question": "문제 지문 (수식은 $...$ KaTeX 인라인 표기)",
      "choices": ["① ...", "② ...", "③ ...", "④ ..."],
      "answerIndex": 2,
      "solution": "풀이 과정 (수식 $...$ 포함, 줄바꿈은 \\n)",
      "timestampSec": 754,
      "theory": ""
    }
  ]
}
```

`answerIndex`는 0-기반. `theory`는 Task 2에서 채우므로 빈 문자열로 둔다.

- [ ] **Step 1: watch 스킬로 영상 분석**

`/watch https://www.youtube.com/watch?v=BlGWW66ZRaY` 를 실행해 프레임과 자막(트랜스크립트)을 확보한다. 프레임에서 각 문제의 지문·보기·수식을 읽고, 자막에서 해설 논리를 추출하며, 각 문제가 시작되는 시각(초)을 기록한다.

- [ ] **Step 2: content.json 작성**

위 스키마대로 전체 문제를 `content/content.json`에 작성한다. 수식은 KaTeX 인라인 문법(`$\\frac{Q}{4\\pi\\varepsilon_0 r^2}$` 등)으로 표기한다.

- [ ] **Step 3: 검증**

Run: `python3 -c "import json;d=json.load(open('content/content.json'));print(len(d['questions']));assert all(len(q['choices'])==4 and 0<=q['answerIndex']<=3 and q['timestampSec']>0 for q in d['questions'])"`
Expected: 문제 수 출력, assert 통과. 문제 수가 영상 수록 문제 수와 일치하는지 프레임과 대조 확인.

- [ ] **Step 4: Commit**

```bash
git add content/content.json
git commit -m "feat: 영상에서 문제·해설·타임스탬프 추출"
```

### Task 2: PDF에서 미니 이론 정리 작성

**Files:**
- Modify: `content/content.json` (각 문제의 `theory` 필드)

**Interfaces:**
- Consumes: Task 1의 `content.json` (`questions[].theory` 빈 문자열)
- Produces: 모든 `theory` 필드가 채워진 `content.json`. 형식: "**핵심 공식**: ...\n**개념**: ...\n**함정 포인트**: ..." (마크다운 굵게 표기, 수식 `$...$`)

- [ ] **Step 1: PDF 전자기학 파트 위치 파악**

Read 툴로 PDF 목차(1~10페이지 부근)를 읽어 전자기학 이론이 있는 페이지 범위를 파악한다. (20페이지/요청 제한 준수)

- [ ] **Step 2: 문제별 관련 이론 발췌·요약**

각 문제의 주제(예: 쿨롱 법칙, 유전체, 전자유도)에 해당하는 PDF 페이지를 읽고, 공식 + 개념 설명 + 자주 나오는 함정/유형 포인트를 3~6줄로 요약해 `theory` 필드에 기입한다.

- [ ] **Step 3: 검증**

Run: `python3 -c "import json;d=json.load(open('content/content.json'));assert all(q['theory'].strip() for q in d['questions']);print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add content/content.json
git commit -m "feat: 문제별 미니 이론 정리 추가"
```

### Task 3: index.html 제작

**Files:**
- Create: `index.html`

**Interfaces:**
- Consumes: 완성된 `content/content.json` — 내용을 `index.html` 내부 `<script>const DATA = {...}</script>`로 인라인 삽입
- Produces: 배포 가능한 단일 `index.html`

**동작 요구사항 (스펙 그대로):**
- 상단: 제목, 원본 영상 링크, 사용 안내 한 줄, 점수 현황 "정답 n / 푼 문제 m / 전체 N"
- 문제 카드: 번호·지문·보기 4개 버튼
- 보기 클릭 시: 정답이면 해당 보기 초록 ✓, 오답이면 선택 보기 빨강 ✗ + 정답 보기 초록 표시 → 해설 자동 펼침. 이미 답한 문제는 재클릭 무시.
- [해설 보기] 버튼: 클릭 시 판정 없이 해설만 펼침/접힘 토글
- 해설 영역: 정답 표기, 풀이 과정, 미니 이론 정리, "▶ 영상 해설 바로가기" 링크(`https://youtu.be/BlGWW66ZRaY?t=<timestampSec>`, 새 탭)
- 수식: KaTeX auto-render (CDN: `katex.min.css`, `katex.min.js`, `auto-render.min.js`, delimiters `$...$`와 `$$...$$`). 해설이 동적으로 펼쳐진 뒤에도 렌더링되도록 페이지 로드 시 전체를 한 번에 렌더링(해설은 display:none으로 숨김)한다.
- 점수는 JS 변수로만 유지(저장 없음)
- 반응형: `meta viewport`, 카드 max-width 720px 중앙 정렬, 보기 버튼 세로 배치

- [ ] **Step 1: index.html 작성**

위 요구사항을 모두 구현한 단일 파일을 작성한다. 구조: `<style>` 인라인 CSS → 헤더 → `<div id="app">` → 인라인 `DATA` → 렌더링 JS(카드 생성, 클릭 핸들러, 점수 갱신) → KaTeX 로드 및 `renderMathInElement(document.body)`.

- [ ] **Step 2: 로컬 브라우저 검증**

브라우저 툴로 `index.html`을 열어 확인:
- 전 문제 카드 렌더링, 수식 정상 표시 (콘솔 에러 0건)
- 정답 클릭 → 초록 ✓ + 해설 펼침 / 오답 클릭 → 빨강 ✗ + 정답 초록 + 해설 펼침
- 점수 현황 갱신, [해설 보기] 토글, 타임스탬프 링크 URL 형식 확인
- 모바일 뷰포트(375px)에서 레이아웃 확인

Expected: 전 항목 통과

- [ ] **Step 3: 콘텐츠 대조 검증**

렌더링된 문제·정답·해설을 영상 프레임과 무작위 5문제 이상 대조하여 오탈자·정답 오류가 없는지 확인한다.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: 전자기학 3회 기출 웹 문서 index.html"
```

### Task 4: GitHub Pages 배포

**Files:**
- Modify: 없음 (저장소 push + Pages 설정)

**Interfaces:**
- Consumes: Task 3의 `index.html`
- Produces: 공유용 GitHub Pages URL

- [ ] **Step 1: 사용자 확인 (필수 게이트)**

저장소 이름(제안: `cbt-emag-2026`)과 공개 배포 여부를 사용자에게 확인받는다. 확인 전에는 절대 진행하지 않는다.

- [ ] **Step 2: 저장소 생성 및 push**

```bash
gh repo create <확인받은이름> --public --source=. --push
```

- [ ] **Step 3: Pages 활성화**

```bash
gh api -X POST repos/{owner}/<이름>/pages -f 'source[branch]=main' -f 'source[path]=/'
```

- [ ] **Step 4: 배포 확인**

`https://<owner>.github.io/<이름>/` 접속해 페이지 로드·수식·클릭 동작을 최종 확인하고 URL을 사용자에게 전달한다.
