# 0. pools (pools.make_bench = the run-time loader)
  Branin-Fav: n=2500 dim=2 rho=0.1 negate=False budget_cfg=50 f_star=0.404493
  Branin-Unfav: n=2500 dim=2 rho=0.5 negate=False budget_cfg=50 f_star=0.404493
  Park-Fav: n=256 dim=4 rho=0.1 negate=False budget_cfg=50 f_star=1.08731e-07
  Park-Unfav: n=256 dim=4 rho=0.5 negate=False budget_cfg=50 f_star=1.08731e-07
  COFs: n=608 dim=14 rho=0.065 negate=True budget_cfg=30 f_star=-18.5345
  FreeSolv: n=640 dim=10 rho=0.1 negate=False budget_cfg=50 f_star=-3.43
  Polarizability: n=1134 dim=10 rho=0.167 negate=True budget_cfg=30 f_star=-1
  HOPV15: n=240 dim=10 rho=0.1 negate=True budget_cfg=30 f_star=-10.2
  Matbench-Gap: n=3347 dim=10 rho=0.05 negate=False budget_cfg=20 f_star=0
  ExptGap-PBE: n=3508 dim=10 rho=0.05 negate=False budget_cfg=20 f_star=0
  Elastic-CHGNet: n=10819 dim=10 rho=0.05 negate=False budget_cfg=20 f_star=-523
  Elastic-SevenNet: n=10460 dim=10 rho=0.05 negate=False budget_cfg=20 f_star=-383
  Elastic-MatterSim: n=10946 dim=10 rho=0.05 negate=False budget_cfg=20 f_star=-523
  thresholds vs explorer_data.json: max |diff| = 0
# 1. raw trajectory sources
  refig42_tl: 396 files, 342760 rows
  refig42_gp: 166 files, 124640 rows
  conf62_tl: 396 files, 342760 rows
  conf62_gp: 144 files, 123542 rows
  ext: 1836 files, 616692 rows
  ext100: 580 files, 596820 rows
  confirm_ext: 1920 files, 1035742 rows
  confirm20: 624 files, 576960 rows
  cells selected: 4155 (same-horizon duplicate conflicts: 0)
  per-pool sources used (largest horizon wins):
    Branin-Fav: conf62_gp=56, conf62_tl=100, refig42_gp=60, refig42_tl=100
    Branin-Unfav: conf62_gp=59, conf62_tl=100, refig42_gp=60, refig42_tl=100
    Park-Fav: conf62_gp=60, conf62_tl=100, refig42_gp=60, refig42_tl=100
    Park-Unfav: conf62_gp=60, conf62_tl=100, refig42_gp=60, refig42_tl=100
    COFs: conf62_gp=60, conf62_tl=100, refig42_gp=60, refig42_tl=100
    FreeSolv: conf62_gp=20, conf62_tl=100, ext=179, refig42_gp=21
    Polarizability: conf62_gp=40, conf62_tl=100, ext=160, refig42_gp=20
    HOPV15: ext=320
    Matbench-Gap: ext=320
    ExptGap-PBE: confirm_ext=320
    Elastic-CHGNet: confirm_ext=320
    Elastic-SevenNet: confirm_ext=320
    Elastic-MatterSim: confirm_ext=320
  Curriculum/KD/PL identity check: NOT APPLICABLE (those three configurations are not part of the five-surrogate set)
# 2. Fig. 1 b-p attainment (recomputed from raw cells)
  cells: 104 (ref 104); n identical: True; max |mean diff| vs fig1_attainment_values.csv = 3.33e-16
  attainment table (mean over seeds):
pool                            Branin-Fav  Branin-Unfav  Park-Fav  Park-Unfav   COFs  FreeSolv  Polarizability  HOPV15  Matbench-Gap  ExptGap-PBE  Elastic-CHGNet  Elastic-SevenNet  Elastic-MatterSim
model                                                                                                                                                                                                  
MFGP                                 0.912         0.756     0.615       0.774  0.902     0.938           0.954   0.317         0.245        0.333           0.493             0.568              0.757
Sparse MFGP                          0.589         0.224     0.834       0.888  0.923     0.899           0.844   0.080         0.322        0.337           0.574             0.725              0.863
DKL                                  0.913         0.627     0.854       0.842  0.919     0.920           0.945   0.216         0.269        0.290           0.604             0.678              0.837
Frozen-representation transfer       0.586         0.348     0.737       0.855  0.923     0.934           0.963   0.376         0.409        0.406           0.622             0.691              0.872
Pretrain-then-Joint                  0.473         0.025     0.939       0.849  0.912     0.933           0.963   0.292         0.421        0.378           0.381             0.703              0.854
End-to-End Joint                     0.688         0.358     0.836       0.860  0.920     0.937           0.963   0.332         0.381        0.365           0.507             0.727              0.880
Soft Parameter Sharing               0.469         0.105     0.941       0.868  0.900     0.938           0.963   0.245         0.435        0.410           0.334             0.734              0.862
Domain Adaptation (MMD)              0.374         0.089     0.807       0.801  0.934     0.928           0.963   0.331         0.374        0.398           0.553             0.754              0.870
  best-of-family per pool:
             pool best_TL    TL best_GP    GP   diff     verdict  min_all  max_all  min_TL  max_GP
       Branin-Fav     E2E 0.688     DKL 0.913 -0.226          GP    0.374    0.913   0.374   0.913
     Branin-Unfav     E2E 0.358    MFGP 0.756 -0.398          GP    0.025    0.756   0.025   0.756
         Park-Fav     SPS 0.941     DKL 0.854  0.087          TL    0.615    0.941   0.737   0.854
       Park-Unfav     SPS 0.868 SV-MFGP 0.888 -0.020          GP    0.774    0.888   0.801   0.888
             COFs     MMD 0.934 SV-MFGP 0.923  0.011          TL    0.900    0.934   0.900   0.923
         FreeSolv     SPS 0.938    MFGP 0.938  0.000 tie(<=0.01)    0.899    0.938   0.928   0.938
   Polarizability  Frozen 0.963    MFGP 0.954  0.009 tie(<=0.01)    0.844    0.963   0.963   0.954
           HOPV15  Frozen 0.376    MFGP 0.317  0.058          TL    0.080    0.376   0.245   0.317
     Matbench-Gap     SPS 0.435 SV-MFGP 0.322  0.113          TL    0.245    0.435   0.374   0.322
      ExptGap-PBE     SPS 0.410 SV-MFGP 0.337  0.072          TL    0.290    0.410   0.365   0.337
   Elastic-CHGNet  Frozen 0.622     DKL 0.604  0.018          TL    0.334    0.622   0.334   0.604
 Elastic-SevenNet     MMD 0.754 SV-MFGP 0.725  0.030          TL    0.568    0.754   0.691   0.725
Elastic-MatterSim     E2E 0.880 SV-MFGP 0.863  0.016          TL    0.757    0.880   0.854   0.863
  chem/materials 9 pools: {'TL': 7, 'tie': 2, 'GP': 0}
  panel o (13 pools) normalised score:
                                score  attain   n
model                                            
Frozen-representation transfer  0.764   0.671  13
End-to-End Joint                0.745   0.673  13
Domain Adaptation (MMD)         0.676   0.629  13
Soft Parameter Sharing          0.647   0.631  13
Pretrain-then-Joint             0.626   0.625  13
DKL                             0.607   0.686  13
Sparse MFGP                     0.490   0.623  13
MFGP                            0.439   0.659  13
  panel p (9 chem/mat) normalised score:
                                score  attain  n
model                                           
Frozen-representation transfer  0.890   0.688  9
Domain Adaptation (MMD)         0.875   0.678  9
End-to-End Joint                0.801   0.668  9
Pretrain-then-Joint             0.701   0.649  9
Soft Parameter Sharing          0.700   0.647  9
DKL                             0.527   0.631  9
Sparse MFGP                     0.447   0.619  9
MFGP                            0.412   0.612  9
  panel o/p max |diff| vs summary csvs: 8.88e-16 / 1.22e-15
  TL rows above every GP: o 5/5, p 5/5; TL score range o 0.63-0.76
# 3. Fig. 2 trajectories: mean regret at budget points (recomputed)
  max |mean at B diff| vs fig2_trajectories_values.csv: 5.68e-14
  HOPV15 mean regret at B=30/50 (n): MFGP 2.312 (40), SV-MFGP 3.320 (40), DKL 2.613 (40), Frozen 1.270 (40), PtJ 1.658 (40), E2E 1.200 (40), SPS 2.441 (40), MMD 1.470 (40)
  HOPV15 mean regret at 20: MFGP 2.498, SV-MFGP 3.713, DKL 2.811, Frozen 2.288, PtJ 2.408, E2E 2.625, SPS 2.783, MMD 2.203
  Matbench-Gap mean regret at B=30/50 (n): MFGP 0.124 (40), SV-MFGP 0.122 (40), DKL 0.207 (40), Frozen 0.120 (40), PtJ 0.058 (40), E2E 0.115 (40), SPS 0.051 (40), MMD 0.095 (40)
  Matbench-Gap mean regret at 20: MFGP 0.205, SV-MFGP 0.241, DKL 0.331, Frozen 0.176, PtJ 0.113, E2E 0.182, SPS 0.146, MMD 0.168
  Branin-Fav mean regret at B=30/50 (n): MFGP 0.020 (40), SV-MFGP 0.202 (36), DKL 0.009 (40), Frozen 0.128 (40), PtJ 0.794 (40), E2E 0.100 (40), SPS 0.370 (40), MMD 0.455 (40)
  Branin-Fav mean regret at 20: MFGP 0.028, SV-MFGP 1.361, DKL 0.048, Frozen 1.582, PtJ 2.246, E2E 1.022, SPS 2.079, MMD 2.253
  Branin-Unfav mean regret at B=30/50 (n): MFGP 0.051 (40), SV-MFGP 1.382 (39), DKL 0.059 (40), Frozen 1.160 (40), PtJ 3.757 (40), E2E 1.225 (40), SPS 2.994 (40), MMD 2.810 (40)
  Branin-Unfav mean regret at 20: MFGP 0.865, SV-MFGP 5.792, DKL 1.508, Frozen 3.273, PtJ 5.630, E2E 3.493, SPS 5.399, MMD 5.321
  Branin-Fav: MFGP mean curve <= every TL mean curve on 100% of grid points
  Branin-Fav: DKL mean curve <= every TL mean curve on 96% of grid points
  Branin-Fav: SV-MFGP mean curve <= every TL mean curve on 0% of grid points
  Branin-Unfav: MFGP mean curve <= every TL mean curve on 96% of grid points
  Branin-Unfav: DKL mean curve <= every TL mean curve on 96% of grid points
  Branin-Unfav: SV-MFGP mean curve <= every TL mean curve on 0% of grid points
  Matbench-Gap at 15: best TL 0.210 vs best GP 0.269; at 20: 0.113 vs 0.205
# 4. extension runs vs the original-budget runs: prefix identity (paper cells of HOPV15/FreeSolv/Polarizability/Matbench-Gap use the extension trajectories)
        pool       model  n  match  mismatch
    FreeSolv Sparse MFGP 40     38         2
      HOPV15 Sparse MFGP 40     35         5
Matbench-Gap Sparse MFGP 40     28        12
  total compared 980, mismatches 19
# 5. Fig. 3 a-c: 126-cell grid (figrepo/results/grid5tl; TL rows = the five retained classes from results_grid_5tl, GP rows = public results/grid)
  cells 126; seeds per model per cell [10]; polarizability HF range 1.0000 (advantages below are in raw HF units and in range units)
  TL vs MFGP: pos 81 tie 45 neg 0; rho(agreement) -0.81 rho(R2) -0.09; mean adv 0.0717 raw = 0.0717 range units
     profile vs agreement (raw): 0.0:0.221 0.1:0.137 0.2:0.106 0.3:0.100 0.4:0.094 0.5:0.037 0.6:0.040 0.7:0.024 0.8:0.030 0.9:0.018 1.0:0.004
     profile vs R2 (raw): 0.1:0.087 0.2:0.066 0.3:0.058 0.4:0.075 0.5:0.074 0.6:0.083 0.7:0.073 0.8:0.086 0.9:0.040
  TL vs variants: pos 66 tie 60 neg 0; rho(agreement) -0.78 rho(R2) +0.11; mean adv 0.0253 raw = 0.0253 range units
     profile vs agreement (raw): 0.0:0.066 0.1:0.058 0.2:0.033 0.3:0.048 0.4:0.038 0.5:0.007 0.6:0.018 0.7:0.005 0.8:0.006 0.9:0.000 1.0:0.000
     profile vs R2 (raw): 0.1:0.017 0.2:0.018 0.3:0.021 0.4:0.022 0.5:0.027 0.6:0.033 0.7:0.024 0.8:0.040 0.9:0.022
  variants vs MFGP: pos 81 tie 45 neg 0; rho(agreement) -0.72 rho(R2) -0.20; mean adv 0.0464 raw = 0.0464 range units
     profile vs agreement (raw): 0.0:0.155 0.1:0.079 0.2:0.073 0.3:0.052 0.4:0.056 0.5:0.030 0.6:0.022 0.7:0.019 0.8:0.024 0.9:0.018 1.0:0.004
     profile vs R2 (raw): 0.1:0.069 0.2:0.048 0.3:0.037 0.4:0.053 0.5:0.047 0.6:0.051 0.7:0.049 0.8:0.046 0.9:0.018
  max |diff| vs fig1ln_final_cells.csv: 1.39e-16
  grid TL runs: n_hf [np.int64(25)], n_lf [np.int64(249)] (sample of 50 files)
# 6. Fig. 4 a-m: loop-mean held-out LF ECE vs attainment (ECE from the summary CSVs of the original-budget runs)
             pool      r  MFGP_lowest_ece  DKL_highest_ece  MFGP_att_rank  gp_ece_min  gp_ece_max  tl_ece_min  tl_ece_max  att_min  att_max  DKL_att_rank  n_ece_min  nan_ece
       Branin-Fav -0.285             True            False              2       0.169       0.397       0.217       0.339    0.374    0.913             1         36        0
     Branin-Unfav  0.052             True             True              1       0.101       0.422       0.153       0.256    0.025    0.756             2         39        0
         Park-Fav  0.390             True            False              8       0.145       0.222       0.388       0.443    0.615    0.941             3         40        0
       Park-Unfav  0.275             True            False              8       0.173       0.240       0.357       0.390    0.774    0.888             6         40        0
             COFs -0.476            False            False              7       0.137       0.283       0.140       0.198    0.900    0.934             5         40        0
         FreeSolv  0.336            False             True              1       0.065       0.366       0.228       0.261    0.899    0.938             7         40        0
   Polarizability  0.412             True            False              6       0.106       0.204       0.360       0.381    0.844    0.963             7         40        0
           HOPV15 -0.231            False             True              4       0.065       0.405       0.063       0.085    0.080    0.376             7         40        0
     Matbench-Gap -0.667            False             True              8       0.151       0.356       0.090       0.114    0.245    0.435             7         40        0
      ExptGap-PBE -0.903            False             True              7       0.167       0.267       0.081       0.116    0.290    0.410             8         40        6
   Elastic-CHGNet  0.272             True             True              6       0.090       0.394       0.107       0.183    0.334    0.622             2         40        6
 Elastic-SevenNet  0.129             True             True              8       0.073       0.428       0.076       0.153    0.568    0.754             7         40        7
Elastic-MatterSim  0.014            False             True              8       0.095       0.445       0.084       0.125    0.757    0.880             7         40        8
  max |diff| vs fig4_calibration_attain_values.csv: ece 0.000668, attainment 0.0109
  MFGP lowest ECE on 7/13; DKL highest on 8/13; MFGP attainment rank > 6 on 5/9 chem pools; |r|>=0.5: ['Matbench-Gap', 'ExptGap-PBE']
# 7. Fig. 5 a,b: top-k overlap and LF-only screening regret (from the pools as loaded by the runs)
             pool     n     r2  spearman  top10_overlap  top1pct_overlap  screening_regret  screening_regret_pct_range  lf_rank_of_hf_best  top1_hit regime  hf_range
       Branin-Fav  2500 0.9688    0.9874            0.6           0.6000            3.3551                      1.0903                 139         0      B  307.7246
     Branin-Unfav  2500 0.5802    0.8132            0.1           0.3600            0.9969                      0.3240                1380         0      B  307.7246
         Park-Fav   256 0.9649    0.9872            1.0           1.0000            0.0000                      0.0000                   1         1      A   25.9303
       Park-Unfav   256 0.7171    0.8791            0.9           0.5000            0.0000                      0.0000                   1         1      A   25.9303
             COFs   608 0.9582    0.9984            0.8           0.8333            4.5170                     24.4007                   2         0      B   18.5116
         FreeSolv   640 0.8676    0.9404            0.6           0.6667            0.2700                      0.9343                   4         0      A   28.9000
   Polarizability  1134 0.9878    0.9915            1.0           1.0000            0.0892                      8.9194                   2         0      A    1.0000
           HOPV15   240 0.0153    0.1175            0.0           0.0000            3.9000                     38.2653                  13         0      B   10.1920
     Matbench-Gap  3347 0.4563    0.5749            0.0           0.0303            0.9100                      8.8350                 973         0      B   10.3000
      ExptGap-PBE  3508 0.4100    0.4872            0.0           0.0000            1.1500                     11.1650                1033         0      B   10.3000
   Elastic-CHGNet 10819 0.2907    0.6783            0.4           0.1389          384.0000                     73.5632                   8         0      B  522.0000
 Elastic-SevenNet 10460 0.4054    0.7295            0.3           0.3846          369.0000                     96.5969                   4         0      B  382.0000
Elastic-MatterSim 10946 0.7954    0.8556            0.8           0.7064            3.0000                      0.5747                   2         0      B  522.0000
# 8. Fig. 5c + SI Fig. 3: FLOPs (figrepo/results/flop_profile_blr/flop_profile.csv)
  rows 720; models ['DKL Multi-Fidelity', 'DNGO-Gradient', 'DNGO-Joint', 'Domain Adaptation (MMD)', 'MFGP', 'Soft Parameter Sharing', 'Sparse MFGP', 'Two-Stage Joint']; benchmarks ['Branin-Fav', 'Branin-Unfav', 'COFs', 'FreeSolv', 'HOPV15', 'Matbench-Gap', 'Park-Fav', 'Park-Unfav', 'Polarizability']; seeds [np.int64(42), np.int64(43)]; fractions [np.float64(0.1), np.float64(0.3), np.float64(0.5), np.float64(0.7), np.float64(1.0)]
  GP: k_N = 2.29 (R2 0.93)
  TL: k_N = 0.94 (R2 1.00)
  break-even N = 45.9; GP/TL fit-cost ratio at N=100: 2.87x, N=200: 7.35x
  per-model exponent k: DKL Multi-Fidelity 1.52, DNGO-Gradient 0.92, DNGO-Joint 0.95, Domain Adaptation (MMD) 0.97, MFGP 3.04, Soft Parameter Sharing 0.91, Sparse MFGP 2.32, Two-Stage Joint 0.94
  Branin-Fav      cheapest TL Two-Stage Joint 0.224 TF; Sparse 20.8x DKL 15.0x MFGP 4.2x; cheapest overall Two-Stage Joint
  Branin-Unfav    cheapest TL Two-Stage Joint 0.020 TF; Sparse 6.1x DKL 5.8x MFGP 2.0x; cheapest overall Two-Stage Joint
  Park-Fav        cheapest TL Two-Stage Joint 0.209 TF; Sparse 21.5x DKL 11.7x MFGP 2.3x; cheapest overall Two-Stage Joint
  Park-Unfav      cheapest TL Two-Stage Joint 0.017 TF; Sparse 7.3x DKL 3.9x MFGP 0.4x; cheapest overall MFGP
  COFs            cheapest TL Two-Stage Joint 0.178 TF; Sparse 21.5x DKL 10.1x MFGP 3.6x; cheapest overall Two-Stage Joint
  FreeSolv        cheapest TL Two-Stage Joint 0.229 TF; Sparse 22.0x DKL 12.5x MFGP 5.6x; cheapest overall Two-Stage Joint
  Polarizability  cheapest TL Two-Stage Joint 0.031 TF; Sparse 11.8x DKL 4.7x MFGP 0.8x; cheapest overall MFGP
  HOPV15          cheapest TL Two-Stage Joint 0.077 TF; Sparse 19.3x DKL 6.6x MFGP 0.5x; cheapest overall MFGP
  Matbench-Gap    cheapest TL Two-Stage Joint 0.140 TF; Sparse 19.4x DKL 11.7x MFGP 4.2x; cheapest overall Two-Stage Joint
# 9. SI Fig. 1 (S1) and SI Fig. 2 (S2): acquisition arms under attainment
          pool  B  MFGP_EI  n_MFGP_EI  MFGP_greedy  n_MFGP_greedy  MFGP_paired_delta_EI_minus_greedy  n_pairs_MFGP  E2E_EI  n_E2E_EI  E2E_greedy  n_E2E_greedy  E2E_paired_delta  n_pairs_E2E
    Branin-Fav 50    0.912         40        0.912             40                             -0.001            40   0.651        40       0.688            40            -0.037           40
  Branin-Unfav 50    0.756         40        0.739             40                              0.017            40   0.365        40       0.358            40             0.007           40
      Park-Fav 50    0.615         40        0.630             40                             -0.015            40   0.835        40       0.836            40            -0.001           40
    Park-Unfav 50    0.774         40        0.790             40                             -0.016            40   0.861        40       0.860            40             0.001           40
          COFs 30    0.902         40        0.902             40                              0.000            40   0.918        40       0.920            40            -0.002           40
      FreeSolv 30    0.937         39        0.938             40                              0.000            39   0.937        40       0.937            40             0.000           40
Polarizability 30    0.954         40        0.951             40                              0.002            40   0.963        40       0.963            40             0.000           40
        HOPV15 30    0.317         40        0.234             40                              0.083            40   0.399        40       0.332            40             0.067           40
  Matbench-Gap 20    0.165         40        0.144             40                              0.022            40   0.287        40       0.287            40             0.000           40
  HOPV15 EI - greedy per TL surrogate (42-61): {'Frozen': (0.05, 20), 'PtJ': (0.002, 20), 'E2E': (0.134, 20), 'SPS': (0.058, 20), 'MMD': (-0.05, 20)}
acq           pool  B  n_models  mean_delta  win_share  n_seeds_min  n_seeds_max
 EI     Branin-Fav 50         5      -0.017        0.2           20           20
 EI   Branin-Unfav 50         5      -0.007        0.2           20           20
 EI       Park-Fav 50         5       0.003        0.6           20           20
 EI     Park-Unfav 50         5       0.002        0.8           20           20
 EI           COFs 30         5      -0.004        0.2           20           20
 EI       FreeSolv 30         5      -0.001        0.0           20           20
 EI Polarizability 30         5       0.000        0.0           20           20
 EI         HOPV15 30         5       0.039        0.8           20           20
 EI   Matbench-Gap 20         5      -0.012        0.2           20           20
 PI     Branin-Fav 50         5       0.047        1.0           20           20
 PI   Branin-Unfav 50         5       0.020        0.8           20           20
 PI       Park-Fav 50         5       0.010        0.6           20           20
 PI     Park-Unfav 50         5       0.004        0.6           20           20
 PI           COFs 30         5      -0.005        0.0           20           20
 PI       FreeSolv 30         5      -0.001        0.2           20           20
 PI Polarizability 30         5       0.000        0.0           20           20
 PI         HOPV15 30         5       0.048        0.8           20           20
 PI   Matbench-Gap 20         5       0.006        0.4           20           20
UCB     Branin-Fav 50         5      -0.095        0.0           20           20
UCB   Branin-Unfav 50         5      -0.030        0.0           20           20
UCB       Park-Fav 50         5       0.003        0.8           20           20
UCB     Park-Unfav 50         5       0.005        0.6           20           20
UCB           COFs 30         5      -0.001        0.2           20           20
UCB       FreeSolv 30         5       0.002        0.4           20           20
UCB Polarizability 30         5       0.000        0.0           20           20
UCB         HOPV15 30         5       0.030        0.6           20           20
UCB   Matbench-Gap 20         5      -0.020        0.4           20           20
MES     Branin-Fav 50         5      -0.106        0.2           20           20
MES   Branin-Unfav 50         5      -0.044        0.0           20           20
MES       Park-Fav 50         5       0.003        0.8           20           20
MES     Park-Unfav 50         5       0.006        0.8           20           20
MES           COFs 30         5      -0.003        0.2           20           20
MES       FreeSolv 30         5       0.002        0.4           20           20
MES Polarizability 30         5       0.000        0.0           20           20
MES         HOPV15 30         5       0.026        0.6           20           20
MES   Matbench-Gap 20         5       0.006        0.2           20           20
 TS     Branin-Fav 50         5      -0.045        0.4           20           20
 TS   Branin-Unfav 50         5       0.069        1.0           20           20
 TS       Park-Fav 50         5       0.006        0.6           20           20
 TS     Park-Unfav 50         5       0.010        0.8           20           20
 TS           COFs 30         5      -0.001        0.2           20           20
 TS       FreeSolv 30         5      -0.008        0.0           20           20
 TS Polarizability 30         5       0.000        0.0           20           20
 TS         HOPV15 30         5      -0.087        0.2           20           20
 TS   Matbench-Gap 20         5      -0.138        0.0           20           20
  reference supp_acq_portfolio_meandelta.csv:
          Branin-Fav  Branin-Unfav  Park-Fav  Park-Unfav   COFs  FreeSolv  Polarizability  HOPV15  Matbench-Gap
EI            -0.017        -0.007     0.003       0.002 -0.004    -0.001             0.0   0.039        -0.012
PI             0.047         0.020     0.010       0.004 -0.005    -0.001             0.0   0.048         0.006
GP-UCB        -0.095        -0.030     0.003       0.005 -0.001     0.002             0.0   0.030        -0.020
MES           -0.106        -0.044     0.003       0.006 -0.003     0.002             0.0   0.026         0.006
Thompson      -0.045         0.069     0.006       0.010 -0.001    -0.008             0.0  -0.087        -0.138
# 10. Table 1 / SI Table 4: pool sizes, R2, synthetic definitions
  Branin-Fav: alpha 0.8; R2(1000 uniform, seed 42) 0.9665; R2(pool) 0.9688; csv == src functions: True; lattice 50^2; pool min HF 0.404493
  Branin-Unfav: alpha 0.1; R2(1000 uniform, seed 42) 0.5615; R2(pool) 0.5802; csv == src functions: True; lattice 50^2; pool min HF 0.404493
  Park-Fav: alpha 0.6; R2(1000 uniform, seed 42) 0.9651; R2(pool) 0.9649; csv == src functions: True; lattice 4^4; pool min HF 1.08731e-07
  Park-Unfav: alpha 0.0; R2(1000 uniform, seed 42) 0.7241; R2(pool) 0.7171; csv == src functions: True; lattice 4^4; pool min HF 1.08731e-07
             pool     n   rho  r2_pool  budget_cfg  negate                         csv  r2_1000uniform csv_regenerates_from_src  alpha  lattice_points_per_axis  pool_min_HF
       Branin-Fav  2500 0.100   0.9688          50   False    synthetic_branin_fav.csv          0.9665                     True    0.8                     50.0 4.044927e-01
     Branin-Unfav  2500 0.500   0.5802          50   False  synthetic_branin_unfav.csv          0.5615                     True    0.1                     50.0 4.044927e-01
         Park-Fav   256 0.100   0.9649          50   False      synthetic_park_fav.csv          0.9651                     True    0.6                      4.0 1.087313e-07
       Park-Unfav   256 0.500   0.7171          50   False    synthetic_park_unfav.csv          0.7241                     True    0.0                      4.0 1.087313e-07
             COFs   608 0.065   0.9582          30    True                    cofs.csv             NaN                      NaN    NaN                      NaN          NaN
         FreeSolv   640 0.100   0.8676          50   False                freesolv.csv             NaN                      NaN    NaN                      NaN          NaN
   Polarizability  1134 0.167   0.9878          30    True          polarizability.csv             NaN                      NaN    NaN                      NaN          NaN
           HOPV15   240 0.100   0.0153          30    True                  hopv15.csv             NaN                      NaN    NaN                      NaN          NaN
     Matbench-Gap  3347 0.050   0.4563          20   False            matbench_gap.csv             NaN                      NaN    NaN                      NaN          NaN
      ExptGap-PBE  3508 0.050   0.4100          20   False            expt_gap_pbe.csv             NaN                      NaN    NaN                      NaN          NaN
   Elastic-CHGNet 10819 0.050   0.2907          20   False    elastic_chgnet_shear.csv             NaN                      NaN    NaN                      NaN          NaN
 Elastic-SevenNet 10460 0.050   0.4054          20   False  elastic_sevennet_shear.csv             NaN                      NaN    NaN                      NaN          NaN
Elastic-MatterSim 10946 0.050   0.7954          20   False elastic_mattersim_shear.csv             NaN                      NaN    NaN                      NaN          NaN
  Park csv vs formulas: standard Park (sqrt(1+A)-1) max diff 0.707; SI equation (sqrt(1+A)) 0.707; code (sqrt(A)) 0.707
# 11. initial design sizes, seeds per cell, environment cross-check
             pool  budget_cfg   rho  n_init_hf  n_init_lf  init_cost n_hf_end n_lf_end
       Branin-Fav          50 0.100          2         25      4.500     [24]    [259]
     Branin-Unfav          50 0.500          2          5      4.500     [24]     [52]
         Park-Fav          50 0.100          2         25      4.500     [24]    [256]
       Park-Unfav          50 0.500          2          5      4.500     [24]     [52]
             COFs          30 0.065          2         23      3.495     [15]    [230]
         FreeSolv          50 0.100          2         25      4.500     [24]    [259]
   Polarizability          30 0.167          2          8      3.336     [16]     [83]
           HOPV15          30 0.100          2         15      3.500     [15]    [149]
     Matbench-Gap          20 0.050          2         20      3.000     [10]    [199]
      ExptGap-PBE          20 0.050          2         20      3.000     [30]    [600]
   Elastic-CHGNet          20 0.050          2         20      3.000     [30]    [600]
 Elastic-SevenNet          20 0.050          2         20      3.000     [30]    [600]
Elastic-MatterSim          20 0.050          2         20      3.000     [30]    [600]
  n per cell (Fig. 1):
pool                            Branin-Fav  Branin-Unfav  Park-Fav  Park-Unfav  COFs  FreeSolv  Polarizability  HOPV15  Matbench-Gap  ExptGap-PBE  Elastic-CHGNet  Elastic-SevenNet  Elastic-MatterSim
model                                                                                                                                                                                                 
MFGP                                    40            40        40          40    40        40              40      40            40           40              40                40                 40
Sparse MFGP                             36            39        40          40    40        40              40      40            40           40              40                40                 40
DKL                                     40            40        40          40    40        40              40      40            40           40              40                40                 40
Frozen-representation transfer          40            40        40          40    40        40              40      40            40           40              40                40                 40
Pretrain-then-Joint                     40            40        40          40    40        40              40      40            40           40              40                40                 40
End-to-End Joint                        40            40        40          40    40        40              40      40            40           40              40                40                 40
Soft Parameter Sharing                  40            40        40          40    40        40              40      40            40           40              40                40                 40
Domain Adaptation (MMD)                 40            40        40          40    40        40              40      40            40           40              40                40                 40
  VM vs SLURM (blr_replace__hf_ei, same seeds): 1846 overlapping runs; final regret identical 1846; auc identical 1846; max |auc diff| 0
  figrepo/results (collect.py output) vs raw cells 42-61: 1440 rows, 0 not found in raw, max |final diff| 4.44e-16; cells per model: {'DKL': 180, 'Domain Adaptation (MMD)': 180, 'End-to-End Joint': 180, 'Frozen-representation transfer': 180, 'MFGP': 180, 'Pretrain-then-Joint': 180, 'Soft Parameter Sharing': 180, 'Sparse MFGP': 180}