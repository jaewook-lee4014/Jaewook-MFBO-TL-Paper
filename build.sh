#!/usr/bin/env bash
# Build the submission PDFs. main.tex and si.tex are independent documents (references across
# them are plain numbers); build_pair simply runs the usual pdflatex/bibtex passes for both.
#   ./build.sh            -> main.pdf and si.pdf (redline: struck superseded text, blue replacement text)
#   ./build.sh clean      -> main_clean.pdf and si_clean.pdf (current text only; wrappers main_clean.tex / si_clean.tex)
#   ./build.sh combined   -> main_with_si.pdf (single working PDF, SI appended, redline)
set -e
cd "$(dirname "$0")"
PDFLATEX="pdflatex -interaction=nonstopmode -halt-on-error"
build_pair () {   # $1 = main-text job, $2 = SI job
  $PDFLATEX $1.tex >/dev/null || true      # first pass: $1.aux for the SI
  $PDFLATEX $2.tex >/dev/null || true      # first pass: $2.aux for the main text
  bibtex $1 >/dev/null || true; bibtex $2 >/dev/null || true   # bibtex exits 1 on mere warnings
  $PDFLATEX $1.tex >/dev/null; $PDFLATEX $2.tex >/dev/null
  $PDFLATEX $1.tex >/dev/null; $PDFLATEX $2.tex >/dev/null
  $PDFLATEX $1.tex >/dev/null
  echo "built $1.pdf and $2.pdf"
  grep -E "Reference .* undefined|Citation .* undefined|Float too large|multiply defined" $1.log $2.log || echo "no undefined references / float warnings"
}
case "${1:-}" in
  combined)
    $PDFLATEX main_with_si.tex >/dev/null; bibtex main_with_si >/dev/null || true
    $PDFLATEX main_with_si.tex >/dev/null; $PDFLATEX main_with_si.tex >/dev/null
    echo "built main_with_si.pdf" ;;
  clean)
    build_pair main si            # the clean wrappers read the labels of the base build
    build_pair main_clean si_clean ;;
  *) build_pair main si ;;
esac
