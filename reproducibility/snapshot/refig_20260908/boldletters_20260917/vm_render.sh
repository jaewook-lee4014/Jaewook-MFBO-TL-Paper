#!/usr/bin/env bash
# 2026-09-17 bold panel letters / print-size Fig. 4 and SI Fig. 4 / Fig. 3 d-f. Run on the VM l40s.
set -e
R=/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908
PY=/mnt/data/jaewook_mfbo/bo_env/bin/python
S=$R/figcand2_20260914_5tl/scripts
F=$R/figrepo/figures
BK=$R/_backup_boldletters_20260917
mkdir -p $BK
SCRIPTS="$S/fig1_attainment_exact.py $S/fig2_trajectories_exact.py $S/make_a1_calibration_13_attain_exact.py $R/supp_attain_5tl.py $F/make_fig1ln_final_5tl.py $F/plot_computing_flops_blr_5tl.py $F/make_b2_topk_13.py"
OUTS="$R/figcand2_20260914_5tl/fig1_attainment.pdf $R/figcand2_20260914_5tl/fig2_trajectories.pdf $R/figcand2_20260914_5tl/fig4_calibration_attain.pdf $R/figcand2_20260914_5tl/supp/supp_acq_portfolio.pdf $F/out/fig5tl_20260914/fig_grid_final.pdf $F/out/fig5tl_20260914/computing_time_blr.pdf $F/out/fig5_13/B2_topk_13.pdf"
VALS="$R/figcand2_20260914_5tl/fig1_attainment_values.csv $R/figcand2_20260914_5tl/fig1_attainment_summary_deficit.csv $R/figcand2_20260914_5tl/fig1_attainment_summary_deficit_chem.csv $R/figcand2_20260914_5tl/fig2_trajectories_values.csv $R/figcand2_20260914_5tl/fig4_calibration_attain_values.csv $R/figcand2_20260914_5tl/supp/supp_acq_portfolio_values.csv $R/figcand2_20260914_5tl/supp/supp_acq_portfolio_winshare.csv $R/figcand2_20260914_5tl/supp/supp_acq_portfolio_meandelta.csv $F/out/fig5tl_20260914/fig1ln_final_cells.csv $F/out/fig5tl_20260914/computing_flops_values_blr.csv $F/out/fig5_13/B2_topk_13_values.csv"
# backups, once
for f in $SCRIPTS $OUTS; do [ -f $BK/$(basename $f) ] || cp -p $f $BK/; done
[ -f $BK/md5_BEFORE.txt ] || md5sum $OUTS $VALS > $BK/md5_BEFORE.txt
# patch
$PY $BK/vm_patch_letters.py
cp $BK/make_b2_topk_13_new.py $F/make_b2_topk_13.py
# render
echo "== Fig. 1 b-p";   cd $R && $PY $S/fig1_attainment_exact.py > $BK/log_fig1.txt 2>&1; tail -1 $BK/log_fig1.txt
echo "== Fig. 2";       cd $R && $PY $S/fig2_trajectories_exact.py > $BK/log_fig2.txt 2>&1; tail -1 $BK/log_fig2.txt
echo "== SI Fig. 3";    cd $F && ECE_X=mean CAL_LETTERS=abcdefghijklm CAL_STEM=fig4_calibration_attain $PY ../../figcand2_20260914_5tl/scripts/make_a1_calibration_13_attain_exact.py > $BK/log_sifig3.txt 2>&1; tail -1 $BK/log_sifig3.txt
echo "== SI Fig. 2";    cd $R && $PY supp_attain_5tl.py S2 > $BK/log_sifig2.txt 2>&1; tail -1 $BK/log_sifig2.txt
echo "== Fig. 3";       cd $F && FIG_OUT=fig5tl_20260914 FIG_OUT_DIR=figrepo/figures/out/fig5tl_20260914 FIG1LN_LETTERS=a,b,c,d,e,f FIG_STEM=fig_grid_final $PY make_fig1ln_final_5tl.py > $BK/log_fig3.txt 2>&1; tail -1 $BK/log_fig3.txt
echo "== Fig. 4";       cd $F && MPLBACKEND=Agg FIG_OUT=fig5_13 $PY make_b2_topk_13.py > $BK/log_fig4.txt 2>&1; tail -1 $BK/log_fig4.txt
echo "== SI Fig. 4";    cd $F && FIG_OUT=fig5tl_20260914 GP_VARIANTS=DKL $PY plot_computing_flops_blr_5tl.py > $BK/log_sifig4.txt 2>&1; tail -1 $BK/log_sifig4.txt
md5sum $OUTS $VALS > $BK/md5_AFTER.txt
echo "== value-file md5 differences (expect none):"
diff <(grep '\.csv$' $BK/md5_BEFORE.txt) <(grep '\.csv$' $BK/md5_AFTER.txt) && echo "all value files unchanged"
echo "== new PDF md5:"; grep '\.pdf$' $BK/md5_AFTER.txt
