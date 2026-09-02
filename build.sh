#!/usr/bin/env bash
# Build the submission PDFs. main.tex and si.tex cross-reference each other's labels
# through the xr package, so each is compiled twice around the other's .aux.
#   ./build.sh            -> main.pdf (main text + Methods + references) and si.pdf
#   ./build.sh combined   -> main_with_si.pdf (single working PDF, SI appended)
set -e
cd "$(dirname "$0")"
PDFLATEX="pdflatex -interaction=nonstopmode -halt-on-error"
if [ "${1:-}" = "combined" ]; then
  $PDFLATEX -jobname=main_with_si "\def\withSI{1}\input{main.tex}" >/dev/null
  bibtex main_with_si >/dev/null
  $PDFLATEX -jobname=main_with_si "\def\withSI{1}\input{main.tex}" >/dev/null
  $PDFLATEX -jobname=main_with_si "\def\withSI{1}\input{main.tex}" >/dev/null
  echo "built main_with_si.pdf"; exit 0
fi
$PDFLATEX main.tex >/dev/null || true      # first pass: main.aux for the SI
$PDFLATEX si.tex   >/dev/null || true      # first pass: si.aux for the main text
bibtex main >/dev/null; bibtex si >/dev/null
$PDFLATEX main.tex >/dev/null; $PDFLATEX si.tex >/dev/null
$PDFLATEX main.tex >/dev/null; $PDFLATEX si.tex >/dev/null
$PDFLATEX main.tex >/dev/null
echo "built main.pdf and si.pdf"
grep -E "Reference .* undefined|Citation .* undefined|Float too large|multiply defined" main.log si.log || echo "no undefined references / float warnings"
