# 논문 그림 전량 재생성 (2026-09-08): per-fidelity 마스킹 + 개선 TL 헤드, 11 TL vs 3 GP

## 1. 목적과 범위
- 논문(Jaewook-MFBO-TL-Paper)의 데이터 기반 그림 전부를 per-fidelity 후보 마스킹(각 fidelity는 자기 평가 후보만 제외, LF→HF 승격 허용)
  프로토콜로 다시 계산해 교체한다.
- TL 11개 모델(Sequential, Progressive, Curriculum, TwoStageJoint, DNGOJoint, DNGOGradient, KnowledgeDistillation,
  DomainAdaptationMMD, SoftParameterSharing, PseudoLabeling, Adapter) 전부에 fairness ladder에서 찾은 개선 구조를 적용한다.
- GP는 MFGP(baseline, BoTorch legacy prior), NARGP, Sparse variational MFGP 3종. DKL은 제외(사용자 지시).
- 시드 42–61(20개), 예산·비용비·FPS 초기설계·라운드로빈은 논문 프로토콜 그대로.

## 2. 개선 TL 구조 (primary arm = `blr_replace__hf_argmin`, cold, tanh)
- HF 헤드: 64×2 잔차 MLP 출력 대신 `mu_H = g_L(x) + BLR([g_L(x), phi_L(x), 1])` (선형 재척도 + LF 특징 위 선형 보정, 가중치 66개,
  prior precision a≈1(10), phi 100→LOO 선택, bias 1; beta LOO로 [1,100] 클리핑). 잔차 MLP는 학습되지만 예측에 쓰이지 않는다.
  → "HF 헤드 파라미터 과다" 문제를 제거한다 (HF 점수 2–10개에 64×2 MLP를 맞추던 구조).
- LF 질의: HF 예측 `mu_H`의 argmin (GP가 HF 사후를 겨냥하는 것과 같은 목표). HF 질의: `mu_H` argmin. 상수-sigma EI(언더플로) 규칙 폐기.
- 매 반복 재학습(cold). warm-start(50 epoch)는 보조 암으로만.
- Adapter는 backbone/out_layer로 (g_L, phi_L)을 구성. ReLU 암은 Adapter용 ReLU 서브클래스 사용.
- LF ECE/NLL/sharpness를 매 재학습마다 미표본 풀에서 `experiments/_shared_calibration.py`로 기록(run_uq.py와 동일 정의).

## 3. 판단 사항 (사용자 지시: 필요한 판단은 안전한 쪽으로 하고 보고서에 기록)
- J1 primary는 cold: PCA-10 풀에서 cold가 warm보다 낫고(HOPV15 2.78 vs 3.92), warm은 11개 모델의 학습 절차를 첫 학습 뒤 모두 같은
  generic 미세조정으로 바꿔 모델 비교가 무의미해진다. warm은 보조 암으로 실행해 표로만 보고.
- J2 BLR 헤드는 HF 네트워크를 버리므로 HF 단계만 다른 모델(Curriculum·KnowledgeDistillation·PseudoLabeling)은 궤적이 완전히 같다
  (Sequential도 거의 같음). 11개 비교는 사실상 LF 학습 절차 7종의 비교이며, 그림에는 그대로 두되 본문에서 밝혀야 한다.
- J3 GP 3종은 같은 코드(run_gp.py, ECE 로깅 포함)로 새로 실행. 피팅 실패(NotPSD/ModelFittingError)로 빠진 시드는 keystone/fix6/uq_calib의
  동일 프로토콜 구 실행으로 채움(최종 병합 기준 2셀만 20 미만: Branin-Fav Sparse 18, Branin-Unfav Sparse 19).
- J4 NARGP는 전 벤치에서 크게 실패(Branin-Fav 14.9, COFs 9.0)하나 사용자 지정 3종이므로 포함. 구현(extra_baselines/baselines.py)이
  풀 전체 스케일에서 발산하는 것으로 보이며, 논문에서는 "구현 한계"로 명시해야 한다.
- J5 격자(Fig 1 l–n, SI 격자): TL 가족은 논문과 같은 3개 모델(Progressive, KD, PL; 개선 헤드), MFGP 변형 = NARGP + Sparse(DKL 제거).
  MFGP/Sparse 격자 런은 공개 저장소 results/grid(이미 per-fidelity 프로토콜, 6-18 재검증)를 재사용, NARGP 126셀×10시드는 신규.
  나머지 8개 TL 모델의 격자 런은 SLURM 우선순위 정체로 취소(보너스였음).
- J6 Fig 5a,b(top-k 중첩·스크리닝 후회)는 데이터 전용이라 그대로. Fig 5c·SI computing_time은 기존 FLOPs 프로파일에서 DKL만 제거해
  재생성(BLR 헤드는 MLP 헤드보다 연산이 적으므로 TL 곡선은 보수적).
- J7 보정 그림(Fig 4e–m): LF ECE = 마지막 재학습 시점 미표본 풀 값(논문의 held-out 정의와 동일), Park는 B=10 후회와 짝지음.
- J8 포트폴리오(Fig 4a–d): EI/PI/UCB/MES/TS를 (mu_H, sigma_H)와 HF incumbent로 LF 질의에 적용, HF 질의는 항상 greedy. Park는 B=10.
  시간 제약으로 시드 42–51을 먼저 실행하고 52–61은 남는 시간에 채움(표의 n 참조).
- J9 원고 본문은 고치지 않았다. 그림만 교체하고, 새 그림과 모순되는 문장을 §6에 목록화했다(재작성은 저자 결정).
- J10 SLURM은 fairshare 우선순위 때문에 초기 GP 배치 외에는 거의 배정되지 않아, 그림에 필요한 모든 실험을 VM(l40s, 56 병렬)으로 옮겼다.
- J11 저장소 커밋에는 AI 관련 흔적을 남기지 않는다(사용자 규칙).

- J13 (추가, 2026-09-08 오전) 사용자 요청으로 DKL도 9벤치×20시드(EI 규칙, ECE 로깅) 실행(VM, results_gp_vm; 격자는 공개 저장소의
  per-fidelity DKL 셀 재사용). 그림 파이프라인을 GP 변형 집합으로 매개변수화(env GP_VARIANTS ⊂ {NARGP, DKL}, Sparse는 항상 포함;
  FIG_OUT 하위 디렉터리)해 4조합(base / nargp / dkl / nargp_dkl)의 그림·통계를 모두 생성. 대조 보드에는 NARGP·DKL 빼기/넣기 버튼을 두고
  기본값은 "NARGP 제외, DKL 포함"(사용자 지시). 원고 브랜치의 그림은 여전히 MFGP·NARGP·Sparse 조합(nargp)이며, 최종 조합은 저자 결정.

- J14 (추가) 최종 후회·AUC로 갈리지 않는 풀을 위해 여섯 지표를 추가 계산(compute_extra_metrics.py → figrepo/figures/out/extra_metrics.json):
  cost-to-threshold(상위 1 % 진입 누적 비용, 예산 절단, 도달률+중앙값, log-rank), 고정 예산 도달률(0.25/0.5/1.0B, Fisher at 0.5B),
  정규화 anytime AUC(풀 목적함수 범위로 정규화), 초기 예산(0.25B) 후회, top-5 % recall(pick_prec_top5에서 복원), 최종 후회 90번째 백분위
  (짝지은 부트스트랩). 검정 단위: 지표별로 고른 최선 TL vs 최강 GP(짝지은 시드), Holm 9벤치. 결과(MFGP·NARGP·Sparse 조합):
  구별 가능 벤치 수 nAUC 4(Branin×2, Park×2), ctt 3, early 3(COFs 포함: Sparse가 0.25B에서 0 vs TL 0.74–1.27), recall5 3(FreeSolv 포함),
  p90 3(HOPV15 포함), reach 1. Polarizability·Matbench-Gap은 어떤 지표로도 가족 간 구별 불가. Park는 상위 1 % 문턱이 최적값과 같아(중복 최적)
  ctt가 "최적 도달 비용"과 동일. Fig 3(EI vs greedy)은 여섯 지표 어느 것으로도 유의차 없음; Fig 4 TS vs greedy는 nAUC로 4벤치 유의.

## 4. 실행 규모와 위치
- 코드: `experiments/refig_20260908/` (run_tl.py, run_gp.py, collect.py, stats_refig.py, figrepo/figures/*.py = 공개 저장소 스크립트의
  DKL 제거·NARGP 대체 패치본). VM 미러: /mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908.
- TL 9벤치: primary 1,980런; hf_ei 1,980; ts/pi/ucb/mes; warm/relu/mlp_small(보조). 격자: 3모델×126셀×10시드 = 3,780런.
- GP: 3종×9벤치×20시드(EI) + MFGP greedy 180런 (SLURM 4스레드); NARGP 격자 1,260런(VM).
- 병합 결과(공개 저장소 형식): `figrepo/results/`; 그림: `figrepo/figures/out/`; 통계: `figrepo/figures/out/stats_refig.md`,
  `FRIEDMAN_NEMENYI_9bench.md`, `effect_sizes_bestTL_vs_GP.csv`, `means_14models.csv`, `si_star_sensitivity_table.tex`.
- 재생성 명령: `bash run_make_all_detached.sh` → `bash pull_figs.sh` (VM에서 collect.py + 그림 스크립트 + stats_refig.py).

## 5. 핵심 결과 (최종 후회, Park는 B=10; 시드 평균)
| 벤치 | 최선 TL | TL | 최강 GP | GP | r | Holm p | 판정 |
|---|---|---|---|---|---|---|---|
| Branin-Fav | E2E | 0.109 | MFGP | 0.015 | −1.00 | 0.002 | GP |
| Branin-Unfav | E2E | 1.20 | MFGP | 0.058 | −0.98 | 0.003 | GP |
| Park-Fav | PtJ | ~0 | Sparse | ~0 | +0.83 | 0.008 | TL (B=10) |
| Park-Unfav | E2E | ~0 | MFGP | 0.045 | +0.93 | 0.002 | TL (B=10) |
| COFs | (모두) | 0 | MFGP/Sparse | 0 | 0 | 1 | 동률 |
| FreeSolv | (모두) | 0 | MFGP/Sparse | 0.0135 | +1.0 (n=1 비영) | 1 | 동률 |
| Polarizability | (모두) | 0 | Sparse | 0 | 0 | 1 | 동률 |
| HOPV15 | Sequential | 0.50 | MFGP | 2.13 | +0.87 | 0.017 | TL |
| Matbench-Gap | Adapter | 0.075 | MFGP | 0.142 | +0.56 | 0.13 | 동률(TL 경향) |
- 평균 순위(14 모델): E2E 5.4, SGJ 5.6, Adapter 6.3, SPS 6.4, KD=Curr=PL 6.5, Seq 6.8, PtJ 7.6, MFGP 8.1, Prog 8.7, MMD 8.8, Sparse 9.3, NARGP 12.4.
  Friedman χ²(13)=30.0, p=0.005 (논문: 20.85, p=0.105); Nemenyi CD 6.61 (논문 7.15) → NARGP만 최상위와 CD 초과.
- Fig 3(획득 매트릭스): MFGP EI≈greedy(논문과 동일); TL은 EI가 greedy와 같거나 더 낫다(HOPV15 1.36 vs 1.77, Branin-Unfav 1.13 vs 1.20).
  "TL은 EI로 바꾸면 급격히 나빠진다"는 문장은 성립하지 않는다.
- 격자(개선 TL 3종 vs legacy GP): anytime-AUC TL>baseline 126/126셀(BH 유의 108), TL>변형(NARGP+Sparse) 125/126(96);
  최종 후회 TL>baseline 81/126(유의 0). 이점은 top-10 일치도가 낮을수록 커진다(한계 곡선 0.20→0.00).
- 보정 vs 후회 Pearson r: Branin-Fav −0.40, Branin-Unfav −0.38, Park-Fav −0.51, Park-Unfav −0.75, COFs −0.45, FreeSolv −0.43,
  Polarizability −0.62, HOPV15 +0.13, Matbench-Gap +0.68 → "모든 벤치에서 음수"는 성립하지 않음(7/9).
- 포트폴리오(Fig 4a–d, 20시드 완료): COFs·FreeSolv·Polarizability는 greedy와 5개 UQ 획득함수 모두 후회 0(동률, "이기는" 비율 0/11).
  판별력 있는 풀에서만 차이: Branin-Unfav TS 10/11, Branin-Fav PI 9/11, Park-Unfav UCB 9/11·MES/TS 8/11, HOPV15 MES 6/11,
  Matbench-Gap TS 0/11·EI 5/11. 논문 문장("COFs에서 greedy가 전부 이김", "FreeSolv·polarizability에서 TS가 전부 이김")은 모두 0-0 동률로 대체.
  → 논문 그림은 캡션 정의(화학 3풀)대로 재생성했고(b–d 패널이 전부 0), 판별 풀 3개(Branin-Unfav, HOPV15, Matbench-Gap)로 바꾼
  대안본을 `figrepo/figures/out/acquisition_portfolio_alt.pdf`로 별도 생성(원고에는 넣지 않음).
- 보조 암(11모델×20시드 합동, primary 대비 최종 후회, r>0 = primary 우세):
  warm-start: Branin-Fav 0.034 vs 0.372 (r −1.00), Branin-Unfav 0.77 vs 2.37 (r −0.79) → warm이 크게 유리; COFs 0.018 vs 0 (r +1.0),
  Matbench 0.164 vs 0.135 (r +0.24) → 약간 불리; HOPV15 동일. 사전에 정한 primary(cold)를 유지하되 이 민감도를 본문에 밝힐 것.
  ReLU: Branin-Fav 0.12 vs 0.37, Branin-Unfav 1.06 vs 2.37, HOPV15 0.83 vs 1.64에서 유리(r −0.5…−0.8), Matbench 0.156 vs 0.135 불리 →
  SI 활성함수 표의 "tanh ≥ ReLU" 결론은 뒤집힘(3승 1패 ReLU).
  소형 MLP 헤드(16×1, `mlp_small`): BLR 헤드보다 Branin-Fav 0.64 vs 0.37, HOPV15 2.32 vs 1.48, Matbench 0.21 vs 0.14로 나쁨,
  Branin-Unfav만 1.87 vs 2.18로 나음 → BLR 헤드 선택을 지지. DomainAdaptationMMD×mlp_small은 MMD 손실의 특징 차원 불일치(64 vs 16)로
  실행 불가(180런 실패)라 표에서 제외(J12).

## 6. 새 그림과 모순되는 원고 문장 (main.tex 줄 번호, 2026-09-08 기준)
- 223: "four-member GP family (… deep-kernel …)" → 3종(DKL 제외).
- 234, 275, 282, 325, 335, 459, 472, 843: "fifteen surrogates" → 14; CD 7.15 → 6.61; Friedman p=0.105 → 0.005.
- 226–233 (Fig 1 캡션): "GP family attains … the highest regret on the molecular-descriptor benchmarks (f–i)" → COFs·FreeSolv·Polarizability는
  0 동률, HOPV15만 TL 우세, NARGP는 모든 벤치 최하위.
- 238 (Fig 1 캡션 m), 368, 785: "deep-kernel and sparse variational" → NARGP and sparse variational; "NARGP was not run on the grid" 삭제.
- 282–296: Branin 수치 0.07/0.05 vs 0.42/1.24, p, r → 0.015/0.058 vs 0.109/1.20, r −1.00/−0.98, Holm p 0.002/0.003.
- 298–300: "baseline MFGP ranked at the bottom on COFs, FreeSolv, polarizability, HOPV15" → 성립하지 않음.
- 318–325: "Curriculum, KD, E2E lowest average ranks … spread 5.3–11.8" → E2E·SGJ·Adapter 상위, 범위 5.4–12.4; KD=Curr=PL 동일 궤적.
- 335: Matbench MFGP 2위 0.29 vs 0.23 → MFGP 0.14 vs Adapter 0.07(비보정 p=0.03, Holm 동률).
- 347–353 (Fig 2 캡션): "GP family remains in a high-regret regime on COFs/FreeSolv/polarizability" → MFGP·Sparse가 COFs에서 0 도달,
  FreeSolv 0.0135, Polarizability 0.0045.
- 403–410 (Fig 3 캡션): "TL degrades sharply when EI replaces greedy" → 반대.
- 443–466, 420–432 (Fig 4): 포트폴리오 문장은 새 표로 재확인 필요; "correlation negative on every benchmark (−0.88 … −0.08)" → 7/9, 범위 −0.75…+0.68.
- 531–533: DKL 언급("deep-kernel GP … 30-fold") 삭제; 나머지 FLOPs 수치는 그대로.
- 366–372, 캡션 l–n: "positive in every cell" → anytime-AUC 기준만 126/126; 최종 후회는 81/126.
- SI: 활성함수 표(보조 암 결과로 갱신), 효과크기 표(effect_sizes_bestTL_vs_GP.csv), 별표 민감도 표(si_star_sensitivity_table.tex), Nemenyi CD.
- 개요 그림(fig1_overview.tex): GP ×4 → ×3, DKL 삭제, "up to 16× lower regret" → "up to 4× lower regret (HOPV15)".

## 7. 다중 지표 합의 페이지 (2026-09-08 오후, 보드 v4)
- 요청: "지표에 따라 순위가 바뀌는데 Fig 1 b-k에서 여러 지표를 동시에 평가하는 방법" → 제안한 세 방식을 모두 보드에 넣음.
- J15 지표는 사전 지정 3종(면이 다른 것만): 최종 후회(Park B=10) · cost-to-threshold(상위 1 % 진입 누적 비용, 예산 절단, E[min(c,B)]/B) · p90 후회.
  상관 지표(anytime AUC, 초기 후회)는 이중 계산이라 제외. 합의 순위에는 검정을 얹지 않음(지표가 독립 반복이 아님).
- 계산: compute_multimetric.py (VM, 15:43 완료) → figrepo/figures/out/<combo>/mm_{consensus,dominance,profiles}.{pdf,png,jpg}, mm_metrics.json (4조합).
  보드용 JPEG는 pdftoppm q78 r100 → board/new/<combo>/. 보드 자산(old/, new/)을 job tmp에서 패키지 board/로 복사해 자급자족.
  빌더 build_board4.py (v1–v3를 이 디렉터리에서 import, B/OUT을 패키지로 재지정). 게시: 같은 URL 8c2e0357 (13.08 MB), 16:5x.
- 결과 (MFGP·NARGP·Sparse 조합): Kendall W Branin 0.91/0.94, HOPV15 0.89, Park-Fav 0.85, Matbench 0.84, Polarizability 0.79, Park-Unfav 0.75, COFs 0.62, FreeSolv 0.60
  (화학 풀의 낮은 W는 최종 후회 0 동점 → ctt에서만 갈리는 동점 효과). 평균 합의 순위 E2E 5.7 … MFGP 7.6 … NARGP 12.5 (DKL 조합: DKL 7.6 < MFGP 8.1).
  지배 판정(비보정 반대 없음 + Holm 찬성): GP 지배 Branin×2(MFGP가 13개 전부), TL 지배 Park-Fav·HOPV15·Matbench-Gap(ctt 0.003이 결정)·Polarizability(ctt 0.006만; DKL 조합에서는 최강 GP=DKL, ctt 0.17 → 지배 없음),
  지배 없음 Park-Unfav(합의 1위 GP가 SV-MFGP: 최종 E2E 0 vs 0.32 p 0.60, ctt 11.0 vs 12.8; E2E는 MFGP는 지배)·COFs·FreeSolv(NARGP를 지배하는 13쌍 외 0쌍; DKL 조합 0쌍).
  Fig 1b-k 대비: Matbench·Polarizability 동률→TL 지배, Park-Unfav TL→지배 없음, 나머지 6개 동일.
  데이터 프로파일 면적: MFGP 0.954 > Seq 0.951 > Curr/KD/PL 0.950 > E2E 0.943 … NARGP 0.674 (DKL 조합: DKL 0.959 1위). τ=0 절편 MFGP 11/27.
  → 순위 평균(TL 1위)과 프로파일(MFGP 1위)이 다른 답: 순위 평균은 격차 크기를 버림. "평균 순위 1위"를 우위 근거로 쓰지 말 것.
- 원고 문장 제안은 보드 #mm 종합 항목 참조. 재현: python compute_multimetric.py (VM) → python build_board4.py → Artifact url 재게시.

## 8. 코드 단계 감사와 확인 캠페인 (2026-09-09)
- 감사 범위: run_tl.py / run_gp.py / benchmark.py / extra_baselines/baselines.py → collect.py → 그림·통계 스크립트 전부를 읽고, 저장 결과의 완전성·단조성·요약=궤적 끝값·VM/SLURM 중복 동일성을 확인. 계측 러너(run_tl_conf.py, run_gp_conf.py: LF_MASK=lf|both, INIT_DESIGN=fps|random, 픽 로깅)가 기본값에서 기존 행을 비트 단위로 재현(TL은 환경 간에도 동일, GP는 같은 기계에서만 동일·환경 간 AUC ≈1 % 차이).
- 발견: (F1) LF 단계 마스킹이 논문 코드(LF∪HF 제외)와 달리 LF만 제외 → greedy 암의 LF 낭비율 0.4–2 %(Branin-Unfav 7 %); 42-61 짝지어 재실행 결과 99셀 중 유의차 0, 가족 판정은 HOPV15만 TL→동률 → 재실행 불필요, 규칙·낭비율 명시. (F2) 대체된 GP 19행·Sparse 결측 3시드를 VM에서 새로 실행(results_gp_vm2; NARGP 4행 값 상이)해 병합 결과가 전부 20/20 신선한 시드. (F3) Curr=KD=PL 비트 동일 → 접힌 Fig 1k(final_regret_collapsed, k=12/13). (F4) BLR 헤드 FLOPs 재프로파일(run_flop_profile_blr.py): TL k_N 0.94, GP 2.68/2.29/2.83/2.50(base/dkl/nargp/nargp_dkl), break-even 58/40/95/71. (F5) 같은 시드 선택·검정 → held-out 62-81 + 교차적합: Branin GP ×2만 재현, HOPV15·Park는 동률(|Δregret|<1e-6 동률 처리). (F9) FPS 초기설계가 최적점을 포함(FreeSolv 100 %, Park-Fav 80 %, Polarizability 87.5 %). (F10) 비학습 베이스라인(run_nonlearn.py): Branin-Unfav 최선 TL ≈ HF-랜덤, HOPV15 MFGP ≈ HF-랜덤. (F12) 무작위 초기설계(42-61): TL은 화학·Park 풀에서 여전히 100 % 후회 0, GP 가족은 크게 저하(MFGP FreeSolv 0.0135→0.29, HOPV15 2.13→3.35), 판정 Branin GP / HOPV15 TL(Holm 0.002) / 나머지 동률.
- 산출물: conf_analysis.{json,md}, audit_status.json, results_conf/, results_gp_conf/, results_gp_vm2/, results_nonlearn[_initrand]/, figrepo/results/flop_profile_blr/, figrepo/figures/out/<combo>/{compute_scaling_law_blr,computing_time_blr,final_regret_collapsed}.pdf; 보드 페이지 #audit(build_board_audit.py, 제안 P1–P14 결정 라디오). 실패 9런(Sparse Branin-Fav ×7 NotPSD, Sparse Branin-Unfav s69, MFGP FreeSolv 무작위초기 s50)은 해당 셀 n=19.
