---
name: cbt-add-video
description: Use when the user gives a 대산전기학원 YouTube 기출 해설 영상 link to add as a quiz page to the cbt-emag-2026 site — "이 영상도 해줘", "○○과목 n회 추가", a youtube.com/watch URL with 과목/회차, or requests to extract 문제/정답/해설 from a lecture video.
---

# CBT 기출 영상 → 퀴즈 페이지 추가

유튜브 기출 해설 영상 1개를 판독해 `content/*.json`을 만들고, 레지스트리에 등록해 배포하는 절차.
핵심 원칙: **자막은 경계·정답의 보조 증거일 뿐, 확정은 항상 프레임(슬라이드)으로 한다.**

## 절차

### 1. 준비 (다운로드·자막·헤더 스캔)

스크래치패드에 작업 폴더 `<id>/`(download, scan)를 만들고:

```bash
cd <작업폴더>/download
yt-dlp --skip-download --write-auto-subs --sub-langs ko --sub-format vtt -o ko "<URL>"
yt-dlp --print "%(title)s | %(duration)s" --skip-download "<URL>"   # 제목·길이 확인
yt-dlp -f "bv*[height<=1080]" -o video.mp4 "<URL>"
```

- vtt → transcript.txt 변환: 타임스탬프 파싱 후 `MM:SS 텍스트` 한 줄씩, 중복 줄 제거.
- 헤더 스캔: 40초 간격으로 문제번호 영역 크롭 추출
  `ffmpeg -loglevel error -ss <t> -i video.mp4 -frames:v 1 -vf "crop=in_w/2:in_h/8:60:30,scale=360:-2" -y ../scan/<t>.jpg`

### 2. 문제 경계 확정

1. transcript.txt에서 "n번 문제", "정답은 n번" 마커를 grep해 앵커 확보 (ASR이 번호를 틀리는 일이 흔하므로 참고용).
2. scan/ 크롭을 병렬 Read로 읽어 20문제 각각의 시작 시각(초) 확정. 40초 격자 사이가 모호하면 그 구간만 10초 간격 크롭을 추가 추출.
3. 장면 전환 감지(ffmpeg scene filter)는 이 강의 포맷에서 실패한 전례가 있음 — 쓰지 말 것.

### 3. 프레임 판독

- 문제 슬라이드(시작+6초)와 풀이 완료 슬라이드(다음 문제 시작−15초)를 1024px로 추출:
  `ffmpeg -loglevel error -ss <t> -i video.mp4 -frames:v 1 -vf scale=1024:-2 -y frames/<이름>.jpg`
- 중간 광고 전면화면("실기대비" 등)이 걸리면 ±20~60초 다른 시각으로 재시도.
- 강사 몸에 보기가 가려지면 같은 문제 구간의 다른 프레임으로 보완.
- 지문·보기 4개·판서 풀이·정답 체크 표시를 읽는다.

### 4. 정답 삼중 검증 (필수)

| 증거 | 얻는 곳 |
|---|---|
| 판서 체크(✓/동그라미/밑줄) | 풀이 슬라이드 |
| "정답은 n번" 육성 | transcript.txt (해당 문제 시간대 안에서만 인정) |
| 재계산 | 계산 문제는 직접 풀어서 대조 |

하나라도 어긋나면 추가 프레임을 뜯어 원인을 찾는다. 재계산 결과와 프레임이 자막보다 우선.

### 5. JSON 작성 → `content/<이름>.json`

```json
{"title":"(빌드가 무시함, 형식만 유지)","videoId":"<유튜브ID>","questions":[
  {"no":1,"question":"지문 ($..$ KaTeX)","choices":["① ...","② ...","③ ...","④ ..."],
   "answerIndex":0,"solution":"풀이 (\n 줄바꿈)","timestampSec":문제시작초,
   "theory":"**핵심 공식**: ...\n**개념**: ...\n**함정 포인트**: ..."}]}
```

- theory 3줄 구성: 핵심 공식(규정 과목은 핵심 수치/규정) / 개념 / 함정 포인트(같은 유형의 숫자·표현 바꿔치기 경향).
- 원본 보기가 그래프·그림이면 텍스트 서술로 변환하고 solution에 명시.
- 검증: `python3 -c "import json;d=json.load(open('content/<f>.json'));assert len(d['questions'])==20 and all(len(q['choices'])==4 and 0<=q['answerIndex']<=3 and q['timestampSec']>0 and q['theory'].strip() for q in d['questions'])"`

### 6. 등록·배포

1. `build.py`의 KISA(전기기사) 또는 SANUP(산업기사) 레지스트리에 `("<파일>.json", "<페이지>.html", "<과목 짧은이름>", "<n회>")` 한 줄 추가. 새 과목이면 OFFICIAL에 (과목번호, 정식명)도 추가.
2. `python3 build.py` → `git add -A && git commit -m "feat: ..." && git push`
3. 배포 폴링(404→200) 후 실제 페이지를 브라우저로 열어 수식 렌더링·채점 클릭·네비게이션 pill을 확인.
4. 스크래치패드 작업 폴더 삭제, 메모리 파일에 페이지·videoId 추가.

## 여러 영상 동시 처리

영상이 2개 이상이면 1번(준비)까지 직접 수행한 뒤, 영상별로 general-purpose 서브에이전트에 2~5단계를 위임한다 (프롬프트에 작업 폴더·스키마·검증 명령·삼중 검증 규칙을 그대로 넣을 것). 완료 보고를 받으면 6단계는 메인에서 일괄 수행.

## 흔한 실수

- 영상 다운로드가 HTTP 403으로 반복 실패 → 대부분 구버전 yt-dlp가 원인. `brew upgrade yt-dlp` 후 재시도하면 해결된 전례.

- 자막의 문제 번호를 그대로 믿음 → ASR이 "12번"을 "14번"으로 받아쓴 전례. 슬라이드 번호가 진실.
- 프레임 하나로 광고인지 모르고 문제를 건너뜀 → sol 프레임이 광고면 반드시 재추출.
- 슬립링 "선간" 저항, "지름"↔"반지름" 같은 조건어를 놓친 재계산 → 문제 지문의 단서를 다시 읽을 것.
- HTML 직접 수정 → 다음 빌드에서 덮어써짐. 반드시 JSON/build.py만 수정.
