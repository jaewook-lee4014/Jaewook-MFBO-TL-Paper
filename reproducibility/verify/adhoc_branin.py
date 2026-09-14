import json, glob, numpy as np, pandas as pd
R = '/mnt/data/jaewook_mfbo/MFBO-TL-Paper/experiments/refig_20260908'
D = json.load(open(f'{R}/figcand2_20260911/explorer_data.json'))
P = D['pools']['Branin-Fav']; thrs = [P['thr'][k] for k in ['5', '2', '1', '0.5']]; B = 50

def attain_pts(pts, b, thrs):
    t0 = pts[0][0]; acc = 0.0; det = []
    for thr in thrs:
        c = None
        for x, y in pts:
            if y <= thr + 1e-12: c = x; break
        ok = c is not None and c <= b + 1e-9
        if ok: acc += (b - max(c, t0)) / (b - t0)
        det.append(c if ok else None)
    return acc / len(thrs), det

def attain_raw(bud, reg, b, thrs):
    t0 = float(bud[0]); acc = 0.0; det = []
    for thr in thrs:
        ok = np.where(reg <= thr + 1e-12)[0]
        if len(ok) and bud[ok[0]] <= b + 1e-9:
            acc += (b - max(float(bud[ok[0]]), t0)) / (b - t0); det.append(float(bud[ok[0]]))
        else: det.append(None)
    return acc / len(thrs), det

for model_raw, disp in [('DomainAdaptationMMD', 'Domain Adaptation (MMD)'), ('Sequential', 'Sequential')]:
    files = glob.glob(f'{R}/results/blr_replace__hf_argmin/cells/traj_Branin-Fav_{model_raw}_*.csv') + glob.glob(f'{R}/results_conf/blr_replace__hf_argmin/cells/traj_Branin-Fav_{model_raw}_*.csv')
    raw = pd.concat([pd.read_csv(f) for f in files])
    ser = P['series'][disp]
    print('==', disp, 'thresholds', thrs)
    ndiff = 0
    for s, g in raw.groupby('seed'):
        g = g.sort_values('budget'); bud = g.budget.values.astype(float); reg = g.regret.values.astype(float)
        a_raw, d_raw = attain_raw(bud, reg, B, thrs)
        r = ser[str(s)]; a_pts, d_pts = attain_pts(r['pts'], B, thrs)
        mono = bool(np.all(np.diff(reg) <= 1e-15))
        if abs(a_raw - a_pts) > 1e-9:
            ndiff += 1
            print(f'  seed {s}: raw {a_raw:.4f} pts {a_pts:.4f} monotone={mono} n_rows={len(g)} hz={bud.max():.2f} pts_hz={r["hz"]} crossings raw {d_raw} pts {d_pts}')
            # show the raw rows around the first differing crossing
            for thr, cr, cp in zip(thrs, d_raw, d_pts):
                if cr != cp:
                    i = np.where(reg <= thr + 1e-12)[0][:1]
                    if len(i):
                        i = i[0]; print(f'     thr {thr:.6g}: raw first row {i} budget {bud[i]:.3f} reg {reg[i]:.9g}; previous rows reg {reg[max(0,i-3):i]}; pts near: {[p for p in r["pts"] if abs(p[0]-bud[i])<1.0][:4]}')
                    break
    print('  seeds differing:', ndiff, 'of', raw.seed.nunique())
