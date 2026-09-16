# 처음 보는 에디터 모의 평가 — 격리 프로토콜 (2026-09-16)

## 왜 다시 하는가

2026-09-15의 모의 편집 평가 두 건(Claude, Codex)은 저장소 루트의 `main_clean.pdf` /
`si_clean.pdf`를 읽었다. 그 두 파일은 09-15 02:28 빌드였고, 최종 텍스트(3ee34cf, 19:52)와는
문장 단위로 약 65 %가 달랐다(초록 재작성, "representation-learning problem" 삭제, HF-only
기준선 표와 특징 제거 표 추가, NCS 분량 축소). 또한 Claude 평가는 저장소 안에서 실행되어
프로젝트 메모리(개발 기록)를 로드한 상태였다. 두 문제를 모두 막는 절차가 이 디렉터리다.

## 구성

| 파일 | 역할 |
|---|---|
| `build_review_package.sh` | 지정한 git ref의 원고를 저장소 **밖**의 깨끗한 디렉터리로 내보내고, PDF와 tex의 일치를 검사하고, MANIFEST와 채워진 프롬프트를 만든다 |
| `PROMPT_editor_firstlook.ko.md` | 평가 세션에 붙여 넣는 프롬프트 원본(플레이스홀더 포함). 빌더가 `PROMPT.filled.ko.md`로 채운다 |
| `criteria/NCS_EDITOR_REVIEWER_CRITERIA_2026-09-15.ko.md` | 평가 기준(09-15 작성본의 사본) |

## 사용 순서

```bash
# 1. 패키지 만들기 (기본 ref = main, PDF는 ref에서 새로 빌드)
notes/mock_review_20260916/build_review_package.sh main
#    기존 PDF를 쓰려면:  ... main --pdf-dir review_ncs_final --pdf-prefix 09_final_
#    출력 위치:          ~/mock_review/<날짜>_<ref>/

# 2. 새 터미널에서, 패키지 디렉터리로 이동해 평가 세션을 시작
cd ~/mock_review/<날짜>_<ref>
claude            # 또는: codex --sandbox workspace-write
#    PROMPT.filled.ko.md 내용을 그대로 붙여 넣는다.
#    패키지 밖 경로 읽기 권한 요청이 뜨면 거부한다.

# 3. 결과는 out/ 아래에 저장된다. 두 도구를 각각 별도 세션에서 돌린다.
```

## 격리가 실제로 어떻게 작동하는가

- **자동 메모리**는 작업 디렉터리 경로별로 저장된다(`~/.claude/projects/<경로>/memory/`).
  저장소 밖의 새 경로에서 시작하면 이 논문의 메모리는 로드되지 않는다.
- **CLAUDE.md / AGENTS.md**는 작업 디렉터리에서 상위로 탐색된다. 패키지는 저장소 트리 밖에
  있어야 하고, 빌더가 `.git`·`CLAUDE.md`·`AGENTS.md` 부재를 검사한다.
  `~/CLAUDE.md`(다른 프로젝트, 발효 시뮬레이터 안내)는 여전히 로드되지만 이 논문과 무관하다.
  완전 격리를 원하면 평가 동안 잠시 이름을 바꾼다.
- **git 이력**은 패키지에 없다. 원고는 `git show <ref>:파일`로 내보내며 LaTeX 주석은 제거한다.
- **파일명**에 정보가 없다(`manuscript/main.pdf`, `manuscript/si.pdf`). 이전 평가 문서는 넣지 않는다.
- **프롬프트**는 이차 통제다. 이미 컨텍스트에 있는 기억을 지울 수는 없으므로, 프롬프트는
  (1) 패키지 밖 읽기 금지, (2) 사전 지식·접근 자료의 자기 선언, (3) 모든 지적을 패키지 파일
  위치에 고정, (4) 파일명·경로에서의 추론 금지를 요구하고, 출력 맨 앞의 자기 선언과
  읽은 파일 목록으로 감사한다.

## PDF와 tex 중 무엇을 읽게 하는가

둘 다 준다. 에디터가 보는 것은 PDF(그림·표·분량·배치)이므로 PDF가 1차 대상이다.
tex(주석 제거본)는 정확한 인용, 단어 수, 라벨 확인용이다. 둘이 어긋나면 그 자체를
보고하게 한다. 빌더는 초록 문장으로 PDF-tex 일치를 먼저 검사하고, 어긋나면 중단한다.

## 어느 ref를 평가하는가

기본은 `main`(09-15 19:52, 3ee34cf). 진행 중인 브랜치(예: item1-tlbase-20260916)를
평가하려면 그 ref를 넘긴다. 빌더가 ref에서 PDF를 새로 빌드하므로 루트의 오래된 PDF를
읽는 사고는 재발하지 않는다.
