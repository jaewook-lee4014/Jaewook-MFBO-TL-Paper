# NCS 시제 기준 및 원고 적용 기록

검토일: 2026-09-17. 대상: `main.tex` 전체(초록, 서론, Results, Discussion, Methods, 캡션, 후문) 및 `si-content.tex` 전체. 본문 36개, SI 28개 문자열 구간을 수정했다. 문장 수가 아니라 변경 구간 수다.

## 근거와 기준의 성격

- [NCS Preparing your material](https://www.nature.com/natcomputsci/submission-guidelines/preparing-your-submission): 확인한 공개 제출 안내에는 절별 시제를 일률적으로 강제하는 규정이 없다. 아래 기준을 NCS의 의무 규정으로 주장하지 않는다.
- [Nature Education: Effective Writing — Using the right tense](https://www.nature.com/scitable/topicpage/effective-writing-13815989/): 완료된 연구·관측은 과거형, 일반적 사실·결론·논문의 내용 설명은 현재형, 향후 실제 계획은 미래형을 사용한다. 같은 문장에서도 절의 의미가 다르면 시제가 달라질 수 있다.
- [Wei et al., Deep active optimization for complex systems, NCS (2025)](https://www.nature.com/articles/s43588-025-00858-x): “we introduce”와 “We benchmarked”를 함께 사용한다. 알고리즘 설명과 결과 강조에 현재형도 쓰므로 Results 전체가 반드시 과거형이어야 한다는 근거는 아니다.
- [Lin et al., Deep Bayesian active learning using in-memory computing hardware, NCS (2025)](https://www.nature.com/articles/s43588-024-00744-y): “we proposed”, “we improved”, “we calculated”로 수행 내용을 보고하고, 알고리즘 작동 원리에는 현재형을 사용한다.

실제 NCS 논문 두 편의 관행과 Nature의 명시적 작성 지침을 종합한 **이 원고의 편집 기준**이다. 게재 논문 두 편을 저널 전체의 통계적 조사로 해석하지 않는다.

## 적용 규칙

| 문장의 역할 | 원칙 | 이 원고에서의 처리 |
|---|---|---|
| 일반적 배경·확립된 사실 | 현재형 | SDLs couple, MFBO combines 유지 |
| 과거 연구의 특정 행위 | 과거형 | 특정 연구의 수행·보고 시점에 맞춤 |
| 현재까지 이어진 연구 동향·공백 | 현재완료 또는 현재형 | has become, have not been compared 유지 |
| 이 논문이 제시하는 목적·구성 | 현재형 가능 | We compare, We test, We find 유지 |
| 실제 실행·데이터 처리 | 과거형 | gap replaced, We applied, PCA was fitted |
| 수식·알고리즘·설정의 정의 | 현재형 | head predicts, loss is, TL-base trains 유지 |
| 실험에서 관측한 성능·수치·경로 | 과거형을 기본으로 채택 | matched, separated, stopped, won, had |
| 그림·표를 독자에게 설명 | 현재형 | Fig. shows, curves lie, bars show 유지 |
| 결과의 해석·의미·권고 | 현재형 및 적절한 조동사 | findings support, limitation concerns, recommend 유지 |
| 구체적 미래 계획·가능성 | 계획은 미래형, 가능성은 may/could | 근거 없이 will로 강화하지 않음 |

Methods를 모두 과거형으로 바꾸지 않았다. TL 학습 레시피, GP 구성, BLR 수식은 재사용 가능한 구현의 정의로 읽히므로 현재형을 유지했다. 실제 수행 내용을 말하는 문장은 과거형으로 구별했다. Discussion에서 벤치마크 성적을 재진술하는 부분은 과거형, 그 성적으로부터 해석·권고하는 부분은 현재형으로 구별했다. 캡션과 검토용 storyline은 그림 또는 문단의 내용을 안내하므로 현재형을 허용했다.

## 대표 수정

- 초록: `GPs perform best` → `GPs performed best`; `matches or exceeds` → `matched or exceeded`.
- Results: `all surrogates start alike, but the GP family stops improving` → `all surrogates started alike, but the GP family stopped improving`.
- 격자 결과: `It wins ... and ties` → `It won ... and tied`.
- Methods: `The electrochemical gap replaces` → `The electrochemical gap replaced`.
- SI 보정 분석: `the correlation ... has no consistent sign` → `the correlation ... had no consistent sign`.
- SI 데이터 처리: `We apply` → `We applied`.

## 변경 기록과 검증

- `baseline/`: 이 작업 시작 시점의 본문 및 SI 사본.
- `changes.json`: 64개 구간의 수정 전후 원문.
- `main.tex.diff`, `si-content.tex.diff`: 시제 편집 시점의 diff.
- `verification.json`: 시제 변경만 재구성하여 숫자, 수학 표현, LaTeX 명령, 인용·레이블·참조 보존을 검사한 결과.
- `main.tex.concurrent.diff`: 작업 도중 별도로 추가된 `Methods` → `Methods~\ref{sec:meth-loop}` 참조를 기록했다. 해당 변경을 보존했으며 시제 수정 64개에는 포함하지 않는다.
- `bash build.sh clean` 성공: `main.pdf`, `si.pdf`, `main_clean.pdf`, `si_clean.pdf` 재생성. undefined reference/citation, multiply-defined label, float-too-large 경고 없음.

이번 검토는 시제와 그에 따른 서술 일관성을 대상으로 한다. 성능 주장 자체의 타당성을 새로 검증한 결과는 아니다.
