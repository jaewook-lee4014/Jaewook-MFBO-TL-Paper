import re, collections
T = '/users/k23070952/.claude/jobs/06eeb726/tmp/'
main = open(T + 'main_now.tex').read()
si = open(T + 'si_now.tex').read()

# 1. SI items referenced from the main text (plain-number convention)
refs = collections.defaultdict(set)
for kind, body in re.findall(r'Supplementary (Notes?|Tables?|Figs?\.?)~?\s*((?:[0-9]+(?:~?(?:,|and|--)~?\s*)*)+)', main):
    k = 'Note' if kind.startswith('Note') else 'Table' if kind.startswith('Table') else 'Fig'
    nums = re.findall(r'[0-9]+', body)
    if '--' in body and len(nums) == 2:
        nums = [str(n) for n in range(int(nums[0]), int(nums[1]) + 1)]
    refs[k].update(nums)
print('Referenced from main text:')
for k in ('Note', 'Table', 'Fig'):
    print(f'  {k}: {sorted(refs[k], key=int)}')

# 2. SI inventory in order
notes = re.findall(r'\\suppnote\{.*?\}\{(suppnote:[^}]*)\}', si)
tables = re.findall(r'\\label\{(supptab:[^}]*)\}', si)
figs = re.findall(r'\\label\{(suppfig:[^}]*)\}', si)
print('\nSI inventory:')
print('  Notes :', [(i + 1, n) for i, n in enumerate(notes)])
print('  Tables:', [(i + 1, t) for i, t in enumerate(tables)])
print('  Figs  :', [(i + 1, f) for i, f in enumerate(figs)])
unref = {
    'Note': [i + 1 for i in range(len(notes)) if str(i + 1) not in refs['Note']],
    'Table': [i + 1 for i in range(len(tables)) if str(i + 1) not in refs['Table']],
    'Fig': [i + 1 for i in range(len(figs)) if str(i + 1) not in refs['Fig']],
}
print('\nNOT referenced from the main text:', unref)

# 3. SI word counts per note (body only)
def clean(t):
    t = re.sub(r'\\begin\{(figure|table)\*?\}.*?\\end\{\1\*?\}', '', t, flags=re.S)
    t = re.sub(r'\\storyline\{[^}]*\}', '', t)
    t = re.sub(r'%.*', '', t)
    t = re.sub(r'\\cite[pt]?\{[^}]*\}', '', t)
    t = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?', ' ', t)
    t = re.sub(r'[{}$]', ' ', t)
    return t
starts = [m.start() for m in re.finditer(r'\\suppnote\{', si)] + [len(si)]
tab_pat = re.compile(r'\\label\{supptab:')
fig_pat = re.compile(r'\\label\{suppfig:')
print('\nSI note lengths (body words, tables/figures excluded):')
tot = 0
for i in range(len(starts) - 1):
    seg = si[starts[i]:starts[i + 1]]
    n = len(clean(seg).split()); tot += n
    nt = len(tab_pat.findall(seg)); nf = len(fig_pat.findall(seg))
    print(f'  Note {i + 1:d} {notes[i]:34s} {n:5d} words, tables {nt}, figs {nf}')
print('  total body words', tot)

# 4. Near-duplicate sentences between SI and the Methods section (8-word shingles)
meth = main[main.index('\\section{Methods}'):]
def sents(t):
    t = clean(t)
    t = re.sub(r'\s+', ' ', t)
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+', t) if len(x.split()) >= 8]
def shingles(s, k=8):
    w = re.findall(r'[A-Za-z0-9.\-]+', s.lower())
    return {' '.join(w[i:i + k]) for i in range(len(w) - k + 1)}
msh = {}
for s_ in sents(meth):
    for sh in shingles(s_):
        msh.setdefault(sh, s_)
dups = []
for s_ in sents(si):
    hits = [sh for sh in shingles(s_) if sh in msh]
    if hits:
        frac = len(hits) / max(1, len(shingles(s_)))
        if frac >= 0.5:
            dups.append((frac, s_, msh[hits[0]]))
dups.sort(reverse=True)
print(f'\nSI sentences sharing >=50% of 8-word shingles with a Methods sentence: {len(dups)}')
for frac, a, b in dups[:40]:
    print(f'  [{frac:.2f}] SI: {a[:160]}')
    print(f'         M : {b[:160]}')
