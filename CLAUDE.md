# CBT2026_03 — 전기기사/산업기사 기출 웹 문서 프로젝트

대산전기학원 유튜브 기출 해설 영상을 판독해 GitHub Pages 정적 퀴즈 사이트로 배포하는 프로젝트.

## 배포

- 사이트: https://kim0sun68.github.io/cbt-emag-2026/ (저장소 kim0sun68/cbt-emag-2026, main 루트)
- `git push`하면 GitHub Pages가 자동 재배포 (빌드 1~3분, 404면 잠시 후 재시도)
- 배포 확인: `curl -s -o /dev/null -w "%{http_code}" https://kim0sun68.github.io/cbt-emag-2026/<페이지>?v=<임의값>` (캐시 우회용 쿼리 필수)

## 구조

- `content/*.json` — 회차별 문제 데이터 (스키마는 스킬 참조). 콘텐츠의 유일한 원본.
- `build.py` — 모든 HTML을 생성. **KISA/SANUP 레지스트리에 (json, out, 과목명, 회차) 한 줄 추가하면 페이지·네비게이션·제목이 자동 생성됨.** HTML을 직접 수정하지 말 것.
- 페이지 제목·원본강의 표기는 build.py의 OFFICIAL(정식 과목명·과목번호)에서 생성. JSON title은 사용하지 않음.
- `*.html` — 빌드 산출물 (커밋 대상)
- 626MB 교재 PDF는 .gitignore로 커밋 제외 (절대 add하지 말 것)

## 새 영상 추가

`cbt-add-video` 스킬(.claude/skills/cbt-add-video/)을 사용할 것. 유튜브 링크 하나당 20문제 페이지 하나가 나온다.

## 필수 규칙

- **정답 삼중 검증**: 판서 체크 표시 + 자막 "정답은 n번" + (계산 문제) 직접 재계산. 하나라도 불일치하면 프레임을 다시 뜯어볼 것.
- 자막은 유튜브 한국어 자동자막(yt-dlp `--sub-langs ko`)만 사용. en 요청은 429로 실패한 전례 있음. Whisper 키 미설정.
- 문제 경계는 자막만 믿지 말 것 (ASR이 문제 번호를 자주 틀림). 슬라이드 헤더 스캔으로 확정.
- 수식은 KaTeX `$...$` 표기. 영상 원본 보기가 그림/그래프면 텍스트 서술로 변환하고 solution에 그 사실을 명시.
- 임시 파일은 스크래치패드 디렉터리 사용, 작업 완료 후 삭제.
- 커밋 메시지는 한국어 `feat:`/`fix:` 프리픽스.

## 검증 명령

```bash
# JSON 검증 (모든 회차 공통)
python3 -c "import json;d=json.load(open('content/<파일>.json'));assert len(d['questions'])==20 and all(len(q['choices'])==4 and 0<=q['answerIndex']<=3 and q['timestampSec']>0 and q['theory'].strip() for q in d['questions']);print('OK')"
# 빌드
python3 build.py
```
