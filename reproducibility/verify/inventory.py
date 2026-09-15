#!/usr/bin/env python
"""Inventory of result roots: per (root, arm, benchmark, model) -> seeds, n, max budget, mtimes.
Reads only summary_*.csv (small) and, for max budget, the last row of traj files via tail."""
import os, re, sys, json, glob, subprocess, time
import pandas as pd
ROOTS = sys.argv[1:]
rows = []
pat = re.compile(r'summary_(.+?)_([A-Za-z]+)_s(\d+)(?:-(\d+))?\.csv$')
for root in ROOTS:
    if not os.path.isdir(root):
        rows.append(dict(root=root, note='MISSING')); continue
    for arm in sorted(os.listdir(root)):
        cells = os.path.join(root, arm, 'cells')
        if not os.path.isdir(cells):
            continue
        agg = {}
        for f in sorted(glob.glob(os.path.join(cells, 'summary_*.csv'))):
            m = pat.search(os.path.basename(f))
            if not m: continue
            bench, model = m.group(1), m.group(2)
            try:
                df = pd.read_csv(f)
            except Exception as e:
                rows.append(dict(root=root, arm=arm, benchmark=bench, model=model, note=f'READ_ERROR {e}')); continue
            key = (bench, model)
            a = agg.setdefault(key, dict(seeds=set(), files=[], mtime_min=1e18, mtime_max=0, n_rows=0, cols=set(),
                                         n_hf=set(), n_lf=set(), extra={}))
            a['seeds'] |= set(int(s) for s in df['seed'].tolist())
            a['n_rows'] += len(df)
            a['files'].append(os.path.basename(f))
            st = os.stat(f); a['mtime_min'] = min(a['mtime_min'], st.st_mtime); a['mtime_max'] = max(a['mtime_max'], st.st_mtime)
            a['cols'] |= set(df.columns)
            if 'n_hf' in df: a['n_hf'] |= set(int(x) for x in df['n_hf'].tolist())
            if 'n_lf' in df: a['n_lf'] |= set(int(x) for x in df['n_lf'].tolist())
            for c in ('hf_head', 'lf_target', 'warm', 'act', 'gp_acq', 'lf_mask', 'init_design'):
                if c in df: a['extra'][c] = sorted(set(str(v) for v in df[c].tolist()))
            # max budget from the traj file (last line)
            tf = f.replace('summary_', 'traj_')
            if os.path.exists(tf):
                try:
                    last = subprocess.run(['tail', '-n', '1', tf], capture_output=True, text=True).stdout.strip().split(',')
                    a.setdefault('traj_last', []).append(last)
                except Exception:
                    pass
        for (bench, model), a in sorted(agg.items()):
            seeds = sorted(a['seeds'])
            maxb = None
            if a.get('traj_last'):
                try:
                    maxb = max(float(x[3]) for x in a['traj_last'] if len(x) >= 5)
                except Exception:
                    maxb = None
            rows.append(dict(root=root, arm=arm, benchmark=bench, model=model, n_seeds=len(seeds),
                             seed_min=min(seeds) if seeds else None, seed_max=max(seeds) if seeds else None,
                             seeds=','.join(map(str, seeds)) if len(seeds) < 45 else f'{min(seeds)}..{max(seeds)}',
                             n_rows=a['n_rows'], dup_rows=a['n_rows'] - len(seeds), n_files=len(a['files']),
                             n_hf=','.join(map(str, sorted(a['n_hf']))), n_lf=','.join(map(str, sorted(a['n_lf']))),
                             max_budget_last=maxb,
                             mtime_min=time.strftime('%Y-%m-%d %H:%M', time.localtime(a['mtime_min'])),
                             mtime_max=time.strftime('%Y-%m-%d %H:%M', time.localtime(a['mtime_max'])),
                             extra=json.dumps(a['extra'], sort_keys=True), cols=' '.join(sorted(a['cols']))))
out = pd.DataFrame(rows)
out.to_csv('inventory_out.csv', index=False)
print(out.drop(columns=['cols']).to_string(max_rows=None, max_colwidth=60))
