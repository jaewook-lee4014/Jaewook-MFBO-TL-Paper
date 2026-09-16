#!/usr/bin/env bash
# Build an isolated review package for a first-look mock editorial assessment.
#
#   notes/mock_review_20260916/build_review_package.sh [REF] [--pdf-dir DIR --pdf-prefix P] [--out DIR]
#
# REF          git ref to review (default: main). Text and figures are exported from the ref,
#              never from the working tree.
# --pdf-dir    use existing PDFs <DIR>/<P>main_clean.pdf and <DIR>/<P>si_clean.pdf instead of
#              building (default: build ./build.sh clean from the exported ref).
# --out        package directory (default: ~/mock_review/<YYYYMMDD>_<ref>). Must be OUTSIDE the repo.
#
# The package contains only: manuscript/{main,si}.pdf, {main,si}.txt, comment-stripped tex,
# references.bib, figures/, criteria/, PROMPT.filled.ko.md, MANIFEST.txt, out/.
# It refuses to proceed if the PDF text does not match the ref's abstract (stale-build guard).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && git rev-parse --show-toplevel)"
REF="main"; PDF_DIR=""; PDF_PREFIX=""; OUT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --pdf-dir) PDF_DIR="$2"; shift 2;;
    --pdf-prefix) PDF_PREFIX="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    -h|--help) sed -n '2,16p' "$0"; exit 0;;
    *) REF="$1"; shift;;
  esac
done

cd "$REPO"
REF_HASH="$(git rev-parse --verify "${REF}^{commit}")"
REF_SHORT="${REF_HASH:0:7}"
REF_DATE="$(git log -1 --format=%cd --date=format:'%Y-%m-%d %H:%M' "$REF_HASH")"
DATE="$(date +%Y-%m-%d)"
SAFE_REF="$(echo "$REF" | tr '/' '_')"
OUT="${OUT:-$HOME/mock_review/$(date +%Y%m%d)_${SAFE_REF}}"

# ---- isolation checks on the target location -------------------------------------------------
case "$OUT" in "$REPO"/*) echo "ERROR: package dir must be outside the repo ($REPO)"; exit 1;; esac
if [[ -e "$OUT" ]]; then echo "ERROR: $OUT exists; remove it or pass --out"; exit 1; fi
mkdir -p "$OUT/manuscript/figures" "$OUT/criteria" "$OUT/out"
d="$OUT"; while [[ "$d" != "/" ]]; do
  for f in CLAUDE.md AGENTS.md .git; do
    [[ -e "$d/$f" && "$d" != "$HOME" ]] && { echo "ERROR: $d/$f would be visible to the session"; exit 1; }
  done; d="$(dirname "$d")"; done

# ---- export text from the ref, stripping LaTeX comments --------------------------------------
strip_comments() { sed -e '/^[[:space:]]*%/d' -e 's/\([^\\]\)%.*$/\1/'; }
for f in main.tex si.tex si-content.tex; do
  git show "$REF_HASH:$f" | strip_comments > "$OUT/manuscript/$f"
done
git show "$REF_HASH:references.bib" > "$OUT/manuscript/references.bib"
git archive "$REF_HASH" paper_figures | tar -x -C "$OUT/manuscript/figures" --strip-components=1
if grep -q '\\del{\|\\new{' "$OUT/manuscript/main.tex" "$OUT/manuscript/si-content.tex"; then
  echo "WARNING: redline macros (\\del/\\new) present in the ref text"; fi

# ---- PDFs: copy or build --------------------------------------------------------------------
if [[ -n "$PDF_DIR" ]]; then
  cp "$PDF_DIR/${PDF_PREFIX}main_clean.pdf" "$OUT/manuscript/main.pdf"
  cp "$PDF_DIR/${PDF_PREFIX}si_clean.pdf"   "$OUT/manuscript/si.pdf"
  PDF_SOURCE="copied from $PDF_DIR/${PDF_PREFIX}{main,si}_clean.pdf"
else
  BUILD="$(mktemp -d)"
  git archive "$REF_HASH" | tar -x -C "$BUILD"
  ( cd "$BUILD" && chmod +x build.sh && ./build.sh clean > build.log 2>&1 ) || {
    echo "ERROR: build failed; see $BUILD/build.log. Build the PDFs elsewhere and rerun with --pdf-dir."; exit 1; }
  cp "$BUILD/main_clean.pdf" "$OUT/manuscript/main.pdf"
  cp "$BUILD/si_clean.pdf"   "$OUT/manuscript/si.pdf"
  PDF_SOURCE="built from $REF_SHORT with ./build.sh clean (tmp $BUILD)"
fi
pdftotext "$OUT/manuscript/main.pdf" "$OUT/manuscript/main.txt"
pdftotext "$OUT/manuscript/si.pdf"   "$OUT/manuscript/si.txt"

# ---- stale-build guard: the ref's abstract must appear in the PDF text ------------------------
ABS="$(grep -o '\\abstract{.*' "$OUT/manuscript/main.tex" | head -1 | sed -e 's/\\abstract{//' -e 's/\\unboldmath//' -e 's/\\[a-zA-Z]*//g')"
FIRST="$(echo "$ABS" | awk '{for(i=1;i<=8;i++) printf "%s%s", $i, (i<8?" ":"")}')"
NORM_PDF="$(tr '\n' ' ' < "$OUT/manuscript/main.txt" | tr -s ' ')"
if [[ -z "$FIRST" ]] || ! grep -qF "$FIRST" <<< "$NORM_PDF"; then
  echo "ERROR: PDF text does not contain the ref abstract opening: '$FIRST'"; echo "       PDF source: $PDF_SOURCE"; exit 1; fi
FRESH="OK (abstract opening '$FIRST' found in main.pdf)"

# ---- criteria and prompt ---------------------------------------------------------------------
cp "$HERE/criteria/NCS_EDITOR_REVIEWER_CRITERIA_2026-09-15.ko.md" "$OUT/criteria/"
awk '/^```text$/{f=1;next} /^```$/{f=0} f' "$HERE/PROMPT_editor_firstlook.ko.md" \
  | sed -e "s|{PKG}|$OUT|g" -e "s|{REF_HASH}|$REF_SHORT|g" -e "s|{REF_DATE}|$REF_DATE|g" \
        -e "s|{REF}|$REF|g" -e "s|{DATE}|$DATE|g" > "$OUT/PROMPT.filled.ko.md"

# ---- manifest --------------------------------------------------------------------------------
{
  echo "package built: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "manuscript ref: $REF ($REF_HASH), committed $REF_DATE"
  echo "pdf source: $PDF_SOURCE"
  echo "stale-build check: $FRESH"
  echo "isolation: outside repo=yes; .git=no; CLAUDE.md/AGENTS.md in tree=no"
  echo
  echo "sha256  path"
  ( cd "$OUT" && find manuscript criteria PROMPT.filled.ko.md -type f | sort | xargs sha256sum )
} > "$OUT/MANIFEST.txt"

echo "package: $OUT"
echo "ref:     $REF ($REF_SHORT, $REF_DATE)   pdf: $PDF_SOURCE"
echo "check:   $FRESH"
echo
echo "Next, in a NEW terminal (not inside the repo):"
echo "  cd $OUT && claude"
echo "  cd $OUT && codex --sandbox workspace-write"
echo "Paste the contents of PROMPT.filled.ko.md as the first message. Deny any read outside $OUT."
echo "Reports land in $OUT/out/."
