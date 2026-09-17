"""2026-09-17 bold panel letters (Nature Portfolio style) + print-size Supplementary Fig. 4 + Fig. 3 d-f letters.
Run on the VM: python vm_patch_letters.py   (idempotent: skips a file whose marker is already present)."""
import re, sys, os
R = '/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908'
S = f'{R}/figcand2_20260914_5tl/scripts'
F = f'{R}/figrepo/figures'
MARK = '_panel_title'

HELPER = '''
def _panel_title(a, letter, label, x, y, fs, letter_fs=None, **kw):
    """Nature Portfolio panel title (2026-09-17): bold lowercase letter, then the label in regular weight."""
    lfs = letter_fs if letter_fs is not None else fs + 0.9
    t = a.text(x, y, letter, transform=a.transAxes, ha="left", va="baseline", fontsize=lfs, fontweight="bold", **kw)
    fig = a.figure
    bb = t.get_window_extent(renderer=fig.canvas.get_renderer())
    w_pt = bb.width * 72.0 / fig.dpi
    if label:
        a.annotate(label, xy=(x, y), xycoords="axes fraction", xytext=(w_pt + 0.5 * fs, 0), textcoords="offset points",
                   ha="left", va="baseline", fontsize=fs, annotation_clip=False, **kw)
    return t

'''


def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:100])
    return s.replace(a, b)


def patch(path, edits, helper_before=None):
    s = open(path).read()
    if MARK in s:
        print('already patched:', path); return
    if helper_before is not None:
        assert s.count(helper_before) == 1, helper_before
        s = s.replace(helper_before, HELPER + helper_before)
    for a, b, *n in edits:
        s = rep(s, a, b, n[0] if n else 1)
    open(path, 'w').write(s); print('patched:', path)


# Fig. 1 b-p
patch(f'{S}/fig1_attainment_exact.py', [
    ('    a.text(0.0, 1.15, f"{letters[i]}  {LABEL.get(p, p)}", transform=a.transAxes, ha="left", va="bottom", fontsize=TITLE)',
     '    _panel_title(a, letters[i], LABEL.get(p, p), 0.0, 1.15, TITLE, letter_fs=8.4)'),
    ('    a.text(0.0, 1.15, f"{letter}  {title}", transform=a.transAxes, ha="left", va="bottom", fontsize=TITLE)',
     '    _panel_title(a, letter, title, 0.0, 1.15, TITLE, letter_fs=8.4)'),
], helper_before='letters = "bcdefghijklmnop"')

# Fig. 2 a-m
patch(f'{S}/fig2_trajectories_exact.py', [
    ('    a.text(0.0, 1.15, f"{letters[i]}  {LABEL.get(p, p)}", transform=a.transAxes, ha="left", va="bottom", fontsize=TITLE)',
     '    _panel_title(a, letters[i], LABEL.get(p, p), 0.0, 1.15, TITLE, letter_fs=8.4)'),
], helper_before='letters = "abcdefghijklm"')

# SI Fig. 3 a-m
patch(f'{S}/make_a1_calibration_13_attain_exact.py', [
    ("    ax.text(0.0, 1.13, f'{LETTERS[i]}  {LABEL.get(b, b)}', transform=ax.transAxes, ha='left', va='bottom', fontsize=TITLE)",
     "    _panel_title(ax, LETTERS[i], LABEL.get(b, b), 0.0, 1.13, TITLE, letter_fs=8.4)"),
], helper_before="LETTERS = list(")

# SI Fig. 2 (S2) and the title() helper used by the other supp panels
patch(f'{R}/supp_attain_5tl.py', [
    ('    a.text(0.0, 1.13, f"{letter}  {name}", transform=a.transAxes, ha="left", va="bottom", fontsize=TITLE)',
     '    _panel_title(a, letter, name, 0.0, 1.13, TITLE, letter_fs=8.4)'),
    ('    a1.text(0.0, 1.15, "a  Share of TL surrogates attaining more than greedy", transform=a1.transAxes, ha="left", va="bottom", fontsize=T2)',
     '    _panel_title(a1, "a", "Share of TL surrogates attaining more than greedy", 0.0, 1.15, T2, letter_fs=8.4)'),
    ('    a2.text(0.0, 1.15, "b  Mean attainment difference vs greedy", transform=a2.transAxes, ha="left", va="bottom", fontsize=T2)',
     '    _panel_title(a2, "b", "Mean attainment difference vs greedy", 0.0, 1.15, T2, letter_fs=8.4)'),
    ('        a.text(0.0, 1.15, f"{letters[i]}  {LABEL.get(p, p)}", transform=a.transAxes, ha="left", va="bottom", fontsize=T2)',
     '        _panel_title(a, letters[i], LABEL.get(p, p), 0.0, 1.15, T2, letter_fs=8.4)'),
], helper_before='def title(a, letter, name, sub):')

# Fig. 3: bold a-c, new d-f on the marginal profiles
p = f'{F}/make_fig1ln_final_5tl.py'; s = open(p).read()
if 'letters[c + 3]' not in s:
    s = rep(s, "    ax.text(-0.26 if c == 0 else -0.30, 1.12, letters[c], transform=ax.transAxes, fontsize=LETTER, va='bottom')",
            "    ax.text(-0.26 if c == 0 else -0.30, 1.12, letters[c], transform=ax.transAxes, fontsize=LETTER, fontweight='bold', va='bottom')")
    s = rep(s, "    ax2 = axes[1, c]\n",
            "    ax2 = axes[1, c]\n"
            "    if len(letters) > c + 3:   # 2026-09-17: the marginal profiles are panels d-f (FIG1LN_LETTERS=a,b,c,d,e,f)\n"
            "        ax2.text(-0.26 if c == 0 else -0.30, 1.06, letters[c + 3], transform=ax2.transAxes, fontsize=LETTER, fontweight='bold', va='bottom')\n")
    open(p, 'w').write(s); print('patched:', p)
else:
    print('already patched:', p)

# SI Fig. 4: print-size re-layout (7.2 in wide, Fig. 1/2 rule set) + bold letters
patch(f'{F}/plot_computing_flops_blr_5tl.py', [
    ('TITLE, LABEL, TICK = 15, 13, 12', 'TITLE, LABEL, TICK = 7.5, 6.5, 6.0   # 2026-09-17: drawn at print width (7.2 in), Fig. 1/2 rule set'),
    ('fig, axes = plt.subplots(2, 5, figsize=(15, 7.0))',
     "plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.linewidth': 0.5, 'xtick.major.width': 0.5, 'ytick.major.width': 0.5, 'xtick.major.size': 2, 'ytick.major.size': 2})\n"
     'fig, axes = plt.subplots(2, 5, figsize=(7.2, 3.9))'),
    ("fontsize=10, color='#333')", "fontsize=5.5, color='#333')", 2),
    ("    ax.set_title(f'{ABC[i]}  {BLABEL.get(b, b)}', fontsize=TITLE, loc='left')",
     "    _panel_title(ax, ABC[i], BLABEL.get(b, b), 0.0, 1.03, TITLE, letter_fs=8.4)"),
    ("ax.set_title(f'{ABC[len(BENCHES)]}  Average compute rank', fontsize=TITLE, loc='left')",
     "_panel_title(ax, ABC[len(BENCHES)], 'Average compute rank', 0.0, 1.03, TITLE, letter_fs=8.4)"),
    ("loc='lower center', ncol=2, fontsize=13, frameon=True, fancybox=False,", "loc='lower center', ncol=2, fontsize=6.5, frameon=True, fancybox=False,"),
    ("edgecolor='gray', handlelength=2.4, labelspacing=1.0, bbox_to_anchor=(0.5, 0.040))", "edgecolor='gray', handlelength=2.0, labelspacing=0.6, bbox_to_anchor=(0.5, 0.062))"),
    ("fig.text(0.5, 0.024, CODE_KEY_TL_5, ha='center', va='bottom', fontsize=10.5, color='#333333')",
     "fig.text(0.5, 0.030, CODE_KEY_TL_5, ha='center', va='bottom', fontsize=6.0, color='#333333')"),
    ("fig.text(0.5, 0.006, 'GP: GP-base", "fig.text(0.5, 0.004, 'GP: GP-base"),
    ("         ha='center', va='bottom', fontsize=10.5, color='#333333')", "         ha='center', va='bottom', fontsize=6.0, color='#333333')"),
    ("plt.tight_layout(w_pad=1.4, h_pad=1.4, rect=(0, 0.085, 1, 1))", "plt.tight_layout(w_pad=1.0, h_pad=1.2, rect=(0, 0.125, 1, 1))"),
    ("ABC = list('abcdefghijk')            # regular-weight letters, no parentheses (2026-09-14)",
     "ABC = list('abcdefghijk')            # bold lowercase letters, no parentheses (2026-09-17)"),
], helper_before='fig, axes = plt.subplots(2, 5, figsize=(15, 7.0))')
print('done')
