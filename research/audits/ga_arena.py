#!/usr/bin/env python3
# ga_arena.py — Deterministic tick-level Genetic Algorithm calibration arena for
# Strategy.md parameters, on a Hyperliquid-axiom market simulator.
#
# Axioms enforced (strategy_audit.md §2):
#   AA-4  funding accrues hourly; stresses: user spike 100%/yr AND venue cap 4%/hr (=350,400%/yr)
#   AA-5  Tier-0 fees: maker 1.5 bps, taker 4.5 bps
#   AA-6  minimum order value $10  -> F-1* livelock detector (delta in (B, $10) is un-executable)
#   AA-7  lot quantization: szDecimals=5 @ M≈$97,000 -> lot value ≈ $0.97 (granular residues)
#   AA-8  rate budget (WS-first posture, A-6 of strategy_fixes.md): refresh weight 2,
#         600/min -> Gene A >= 12 ticks is a HARD constraint (violators die)
# Frame: L_eff=3, E0=$20,000, MaxBasketNotional=$30,000, NotionalPerLevel=$5,000, StepBps=10.
#
# Genes: A RebalanceWindow ticks [10,300] · B ExposureTolerance $ [10,50] (hard >10)
#        C EdgeFloor bps [5,50] · D FundingBreaker ann% [5,20] · E EmergExitSlippage bps [5,30]
# Arena time: 60 ticks/s; sub-step = 20 ticks (1/3 s); position horizon 1800 ticks (30 s).
# Determinism: fixed seeds; common random numbers per scenario across all generations.
import json, sys
import numpy as np

SEED, POP, GENS, TOURN, ELITE = 20260921, 1000, 50, 5, 20
E0, LEVEL, STEP = 20_000.0, 5_000.0, 10.0
FEE_M, FEE_T, MIN_ORD = 1.5, 4.5, 10.0
SLOTS, HORIZON, SUB = 6, 1800, 20
TICKS_SEC = 60
REST_W_DEC, REST_BUDGET = 2.0, 600.0
A_MIN = 12                                   # 3600/A * 2 <= 600  =>  A >= 12
W1, W2, W3, W4 = 8.0, 0.8, 2.0, 100.0
MIN_TRADES = 16          # owner mandate: the Profit Layer must operate (feasibility rule)
DEATH = -1e9
LOT = 0.97                                   # $ lot value at ~$97k (AA-7)

LO = np.array([10.0, 10.0,  5.0,  5.0,  5.0])
HI = np.array([300.0, 50.0, 50.0, 20.0, 30.0])
GN = ["A_RebalanceWindow_ticks", "B_ExposureTolerance_$", "C_EdgeFloor_bps",
      "D_FundingBreaker_ann%", "E_EmergSlippage_bps"]

def make_scenarios():
    S = {}
    rng = np.random.default_rng(SEED + 1)                       # A: The Wick
    n = 2400; M = np.empty(n); M[0] = 97_000.0
    for t in range(1, n):
        d = -2.0/900 if t <= 900 else (2.0/900 if t <= 1800 else 0.0)
        M[t] = M[t-1]*(1 + (d + 1.2/1e4*rng.standard_normal())/100)
    f = np.empty(n); f[0] = 0.10
    for t in range(1, n):
        f[t] = np.clip(f[t-1] + 0.02*(0.10 - f[t-1]) + 0.006*rng.standard_normal(), 0.01, 0.40)
    S['A'] = dict(M=M, spr=np.exp(0.3*rng.standard_normal(n))*1.5,
                  fund=f, sm=np.ones(n), name="Wick")
    rng = np.random.default_rng(SEED + 2)                       # B: funding 100%/yr, 5 min
    n = 19_800; M = 97_000.0*np.exp(np.cumsum(0.8/1e4*rng.standard_normal(n)/100))
    f_ou = 0.10 + 0.0
    f = np.empty(n); f[0] = 0.10
    for t in range(1, n):
        base = 0.10
        f[t] = np.clip(f[t-1] + 0.02*(base - f[t-1]) + 0.006*rng.standard_normal(), 0.01, 0.40)
    f[3600:18_000] = 1.00                                          # 100% ann spike, 5 min
    S['B'] = dict(M=M, spr=np.exp(0.3*rng.standard_normal(n))*1.6, fund=f,
                  sm=np.ones(n), name="FundingSpike100")
    rng = np.random.default_rng(SEED + 3)                       # B2: venue cap 4%/hr, 4 min
    n = 15_600; M = 97_000.0*np.exp(np.cumsum(1.0/1e4*rng.standard_normal(n)/100))
    fund = np.where(np.arange(n) < 14_400, 35040.00, 0.10)   # TRUE venue cap: 4%/hr = 35,040% ann
    S['B2'] = dict(M=M, spr=np.exp(0.3*rng.standard_normal(n))*1.8, fund=fund,
                   sm=np.ones(n), name="FundingCap4pctHr")
    rng = np.random.default_rng(SEED + 4)                       # C: liquidity void
    n = 2400; M = 97_000.0*np.exp(np.cumsum(1.5/1e4*rng.standard_normal(n)/100))
    f = np.empty(n); f[0] = 0.10
    for t in range(1, n):
        f[t] = np.clip(f[t-1] + 0.02*(0.10 - f[t-1]) + 0.006*rng.standard_normal(), 0.01, 0.40)
    S['C'] = dict(M=M, spr=np.where(np.arange(n) < 1800, 50.0,
                  np.exp(0.3*rng.standard_normal(n))*1.5),
                  fund=f,
                  sm=np.where(np.arange(n) < 1800, 3.0, 1.0), name="LiquidityVoid")
    return S

SCEN = make_scenarios()

# precompute market state per scenario: EWMA vol (halflife 600 ticks), alpha, GGE, fill prob
def prep(sc):
    M, spr = sc['M'], sc['spr']
    n = len(M); r = np.abs(np.diff(M)/M[1:]*1e4)
    sh = np.empty(n); sh[0] = 1.2
    c = np.exp(np.log(0.5)/600.0)
    for t in range(1, n):
        sh[t] = c*sh[t-1] + (1-c)*r[t-1]
    alpha = np.clip(sh/(0.25*STEP), 1.0, 4.0)
    gge = STEP - alpha*spr/2.0
    fp = np.clip(12.0*alpha/3600.0, 0, 0.10)
    slip_req = spr*sc['sm']
    return dict(sh=sh, alpha=alpha, gge=gge, fp=fp, slip=slip_req,
                fund=sc['fund'], n=n, name=sc['name'])
PREP = {k: prep(v) for k, v in SCEN.items()}

def lhs(n, rng, lo, hi):
    d = len(lo); P = np.empty((n, d))
    for j in range(d):
        cut = (np.arange(n) + rng.permutation(n)) % n
        P[:, j] = lo[j] + (cut + rng.random(n))/n*(hi[j]-lo[j])
    return P

def hard_violation(G):
    rate_ok = (3600.0/np.maximum(G[:, 0], 1e-9))*REST_W_DEC <= REST_BUDGET
    return ~((rate_ok) & (G[:, 1] > 10.0))

def evaluate(G, rng, diag=False, enforce_hard=True):
    P = G.shape[0]
    A = np.maximum(np.round(G[:, 0]).astype(np.int64), 1)
    Bt, Ce, Df, Es = G[:, 1], G[:, 2], G[:, 3], G[:, 4]
    rate_ok = (3600.0/np.maximum(G[:, 0], 1e-9))*REST_W_DEC <= REST_BUDGET
    dhard = ~rate_ok if not enforce_hard else hard_violation(G)
    dead = dhard.copy()
    dlock = np.zeros(P, bool); dliq = np.zeros(P, bool)
    band_tot = np.zeros(P); tr_tot = np.zeros(P); corr_tot = np.zeros(P); brk_tot = np.zeros(P)
    S_ = np.zeros((P, 4)); DDs = np.zeros((P, 4)); CF = np.zeros((P, 4))
    dg = dict(trades=np.zeros(P), corr=np.zeros(P), brk=np.zeros(P), stuck=np.zeros(P)) if diag else None
    for si, key in enumerate(['A', 'B', 'B2', 'C']):
        mk = PREP[key]; n = mk['n']
        eq = np.full(P, E0); peak = np.full(P, E0); dd = np.zeros(P)
        fp = np.zeros(P); dlt = np.zeros(P); lockn = np.zeros(P, np.int64)
        lastev = np.zeros(P, np.int64); cool = np.zeros(P, np.int64)
        act = np.zeros((P, SLOTS), bool); et = np.zeros((P, SLOTS), np.int64)
        mu = np.zeros((P, SLOTS)); sg = np.zeros((P, SLOTS)); dr = np.zeros((P, SLOTS))
        rets = []; w0 = eq.copy(); t0 = 0
        for t in range(0, n, SUB):
            L = min(SUB, n - t)
            gge_t, fp_t, sl_t, fu_t = mk['gge'][t], mk['fp'][t], mk['slip'][t], mk['fund'][t]
            net_open = (dr*act).sum(axis=1)*LEVEL
            carry = net_open + dlt
            fp += np.abs(carry)*fu_t/(8760.0*3600.0*TICKS_SEC)*L
            eq -= np.abs(carry)*fu_t/(8760.0*3600.0*TICKS_SEC)*L
            # resolve matured
            mat = act & (et > 0) & (t - et >= HORIZON)
            if mat.any():
                real = mu[mat] + rng.standard_normal(int(mat.sum()))*sg[mat] - 0.0002
                real = np.maximum(real, -(STEP + 10)/1e4)
                np.add.at(eq, np.nonzero(mat)[0], LEVEL*real)
                act[mat] = False
            # breaker (Fix 3 rate-leg)
            brk = (abs(fu_t) > Df/100.0) & (cool <= 0) & ((act.any(axis=1)) | (dlt != 0)) & ~dead
            if brk.any():
                rb = np.nonzero(brk)[0]
                eq[rb] -= np.abs(carry[rb])*(FEE_T + sl_t)/1e4
                act[rb] = False; dlt[rb] = 0.0; cool[rb] = 600
                brk_tot[rb] += 1
            cool = np.maximum(cool - L, 0)
            # fills
            bleed = np.abs(carry)*np.abs(fu_t)                  # $/hr bleed on open carry
            warn = (np.abs(fu_t) > Df/100.0) | (bleed > 0.40*E0)   # Fix-3 two-leg FUNDING_WARN
            can = (~dead) & (act.sum(axis=1) < SLOTS) & (cool <= 0) & ~warn
            armed = (gge_t - FEE_M) > Ce
            fev = (rng.random(P) < fp_t*L) & armed & can
            if fev.any():
                rf = np.nonzero(fev)[0]
                slot = np.argmax(~act[rf], axis=1)
                d = np.where(rng.random(rf.size) < 0.5, 1.0, -1.0)
                idx = (rf, slot)
                act[idx] = True; et[idx] = t
                mu[idx] = gge_t*0.9/1e4
                sg[idx] = max(mk['sh'][t]*np.sqrt(HORIZON), 5.0)/1e4
                dr[idx] = d
                eq[rf] -= LEVEL*FEE_M/1e4
                dlt[rf] += d*LOT*(1.0 + np.floor(rng.random(rf.size)*24.0))
                tr_tot[rf] += 1
            # governor (evaluates when due)
            due = (~dead) & (t - lastev >= A)
            if due.any():
                lastev[due] = t
                gd = np.nonzero(due)[0]
                ad = np.abs(dlt[gd])
                need = ad > 2.0*Bt[gd]
                ex = sl_t <= Es[gd]
                corr = need & ex
                if corr.any():
                    gc = gd[corr]
                    eq[gc] -= ad[corr]*(FEE_T + sl_t)/1e4
                    dlt[gc] = 0.0
                    corr_tot[gc] += 1
                inband = (ad > Bt[gd]) & (ad*(1 - 0.0017) < MIN_ORD)   # F-1* dead-band
                band_tot[gd] += inband
                lockn[gd] = np.where(inband, lockn[gd] + 1, 0)
                dlock |= lockn > 15
            # liquidation check (conservative AA-1/AA-2 model)
            mreq = np.abs(carry)*(0.5/3.0)
            liq = (eq < mreq) & ~dead
            if liq.any(): dliq |= liq
            dead |= dlock | dliq
            # 10 s windows
            if (t + L) % 600 < L and t > 0:
                rets.append((eq - w0)/E0); w0 = eq.copy()
                pk = np.maximum(peak, eq); dd = np.maximum(dd, (pk - eq)/pk); peak = pk
        rets.append((eq - w0)/E0)
        pk = np.maximum(peak, eq); dd = np.maximum(dd, (pk - eq)/pk); peak = pk
        R = np.array(rets)
        dn = np.sqrt(np.mean(np.minimum(R, 0.0)**2, axis=0) + 1e-12)
        S_[:, si] = np.clip(np.mean(R, axis=0)/dn, -5, 5)
        DDs[:, si] = dd*100; CF[:, si] = fp
    dead |= dlock | dliq
    F = (W1*S_.mean(axis=1) - W2*DDs.max(axis=1)
         - W3*(CF.sum(axis=1)/E0*100) - W4*dliq.astype(float))
    F = np.where(dead, DEATH, F)
    inactive = tr_tot < MIN_TRADES
    F = np.where(inactive & ~dead, F - 10.0, F)   # mandate-inactive: dominated by any active genome
    stats = dict(band=band_tot, trades=tr_tot, corr=corr_tot, brk=brk_tot, inactive=inactive)
    return F, dead, dlock, dliq, dhard, stats

def stream_mean(G, seeds):
    """Mean fitness of genome row-set G averaged over several CRN streams (batch 24 copies)."""
    vals = []
    for s in seeds:
        r = np.random.default_rng(s)
        Fb, db, dlb, dlqb, dhb, stb = evaluate(np.tile(G, (24, 1)), r)
        v = ~db
        vals.append(float(Fb[v].mean()) if v.any() else None)
    vals = [x for x in vals if x is not None]
    return float(np.mean(vals)) if vals else None

def run_ga(gens):
    rngE = np.random.default_rng(SEED + 100)
    G = lhs(POP, rngE, LO, HI)
    hist, best, bestF = [], None, -np.inf
    hof = None; hof_score = -np.inf
    for g in range(gens):
        rng_g = np.random.default_rng((SEED + 1000)*7919 + g)   # CRN within generation
        F, dead, dlock, dliq, dhard, st = evaluate(G, rng_g)
        via = ~dead & ~st['inactive']
        if via.any():
            bi = int(np.argmax(np.where(via, F, -np.inf)))
            if F[bi] > bestF:
                bestF = float(F[bi]); best = G[bi].copy()
        var = float(np.var(F[via])) if via.sum() > 2 else 0.0
        hist.append(dict(gen=g, best=float(F[via].max()) if via.any() else None,
                         mean=float(F[via].mean()) if via.any() else None,
                         var=var, alive=int((~dead).sum()), active=int(via.sum()),
                         hard=int(dhard.sum()), livelock=int(dlock.sum()), liq=int(dliq.sum()),
                         best_gene=[round(float(x), 3) for x in G[bi]] if via.any() else None))
        # hall of fame: candidates scored on 2 fresh streams before admission
        if via.any() and g % 3 == 2:
            cand = G[bi]
            sc = stream_mean(cand, [SEED+500, SEED+501])
            if sc is not None and sc > hof_score:
                hof_score = sc; hof = cand.copy()
        if var < 0.01 and g >= 10 and via.sum() > POP*0.5:
            break
        idx_v = np.nonzero(via)[0]
        if idx_v.size < ELITE + 2:
            break
        picks = idx_v[rngE.integers(0, idx_v.size, (POP, TOURN))]
        winners = picks[np.arange(POP), np.argmax(F[picks], axis=1)]
        p1, p2 = G[winners], G[winners[::-1]]
        lam = rngE.random((POP, 1))
        child = lam*p1 + (1 - lam)*p2
        sig = (HI - LO)*0.15*(0.93**g)*np.array([1, 1, 2.5, 1, 1])
        child = np.clip(child + rngE.standard_normal(child.shape)*sig, LO, HI)
        order = np.argsort(np.where(via, F, -np.inf))[::-1][:ELITE]
        child[:ELITE] = G[order]
        if hof is not None:
            child[0] = hof                      # champion always persists
        # restart on collapse
        if via.sum() < POP*0.10:
            n_inj = POP//3
            child[-n_inj:] = lhs(n_inj, rngE, LO, HI)
        G = child
    return dict(best=best, bestF=bestF, hist=hist, G=G, F=F, hist_len=len(hist),
                hof=(hof if hof is not None else best), hof_score=hof_score)

if __name__ == "__main__":
    gens = int(sys.argv[1]) if len(sys.argv) > 1 else GENS
    print(f"[ga] pop={POP} gens<={gens} seed={SEED} sub={SUB} ticks/s={TICKS_SEC} "
          f"weights=({W1},{W2},{W3},{W4}) min_trades={MIN_TRADES}", flush=True)
    main = run_ga(gens)
    gold = main['hof'] if main['hof'] is not None else main['best']
    print(f"[ga] discovery best={[round(float(x),3) for x in main['best']]} F={main['bestF']:.4f} "
          f"gens_run={main['hist_len']}", flush=True)
    print(f"[ga] last gen: {main['hist'][-1]}", flush=True)
    # ---- validation: 4 fresh streams (discovery-vs-validation honesty)
    v_seeds = [SEED+600, SEED+601, SEED+602, SEED+603]
    val = stream_mean(gold, v_seeds)
    val_discovery = stream_mean(main['best'], v_seeds)
    champion = gold if (val_discovery is None or (val or -1e9) >= (val_discovery or -1e9)) else main['best']
    champ_val = val if champion is gold else val_discovery
    print(f"[validate] HoF meanF(4 streams)={val}  discovery-best meanF={val_discovery} "
          f"-> champion={np.round(champion,3).tolist()} ({champ_val:.3f})", flush=True)
    out = dict(golden=[float(x) for x in champion], goldenF_disc=main['bestF'],
               goldenF_valid=champ_val, hist=main['hist'],
               weights=dict(W1=W1, W2=W2, W3=W3, W4=W4, MIN_TRADES=MIN_TRADES), seed=SEED,
               validation_streams=v_seeds)
    # ---- F-1* controls
    rng = np.random.default_rng(SEED + 7)
    lo2 = LO.copy(); lo2[1] = 2.0; hi2 = HI.copy(); hi2[1] = 10.0
    Gc = lhs(POP, rng, lo2, hi2)
    Gc[:, 0] = champion[0]; Gc[:, 2] = champion[2]; Gc[:, 3] = champion[3]; Gc[:, 4] = champion[4]
    Fc, deadc, dlockc, dliqc, dhc, stc = evaluate(Gc, rng, enforce_hard=False)
    vc = ~deadc & ~stc['inactive']
    occ_c = float((stc['band'] > 0).mean())
    med_c = float(np.median(stc['band'][stc['band'] > 0])) if (stc['band'] > 0).any() else 0.0
    print(f"[control B∈2..10 hard-off] livelock deaths={int(dlockc.sum())}/{POP} "
          f"touching-deadband={100*occ_c:.1f}% median-band-evals={med_c:.0f}", flush=True)
    Gref = Gc.copy(); Gref[:, 1] = 10.5 + rng.random(POP)*(HI[1]-10.5)
    Fr, deadr, dlockr, dliqr, dhr, str_ = evaluate(Gref, rng, enforce_hard=False)
    occ_r = float((str_['band'] > 0).mean())
    print(f"[reference B∈10.5..50 hard-off] livelock deaths={int(dlockr.sum())}/{POP} "
          f"touching-deadband={100*occ_r:.1f}%", flush=True)
    Gc20 = Gc.copy(); Gc20[:, 0] = 20.0
    Fc20, deadc20, dlockc20, dliqc20, dhc20, stc20 = evaluate(Gc20, rng, enforce_hard=False)
    occ_c20 = float((stc20['band'] > 0).mean())
    print(f"[control A=20 B∈2..10] livelock deaths={int(dlockc20.sum())}/{POP} "
          f"({100*dlockc20.mean():.1f}%) touching-deadband={100*occ_c20:.1f}%", flush=True)
    out['control'] = dict(band=[2.0, 10.0], livelock_deaths=int(dlockc.sum()), pop=POP,
                          surviving=int(vc.sum()), touching_pct=100*occ_c, median_band_evals=med_c,
                          ref_band=[10.5, 50.0], ref_livelock_deaths=int(dlockr.sum()),
                          ref_touching_pct=100*occ_r,
                          fastA20_deaths=int(dlockc20.sum()), fastA20_touching_pct=100*occ_c20)
    # ---- golden single-genome diagnostics (champion's own stream behavior)
    Gg = np.tile(champion, (8, 1))
    Fg, deadg, dlockg, dliqg, dhg, stg = evaluate(Gg, np.random.default_rng(SEED + 9))
    out['golden_diag'] = {k: (float(v[0]) if k != 'inactive' else bool(v[0])) for k, v in stg.items()}
    out['golden_diagF'] = float(Fg[0]) if not deadg[0] else None
    # ---- OAT ±10% (24 copies, 4 paired streams) + noise floor
    NC = 24
    def batchF(Gb, seeds):
        vals = []
        for s in seeds:
            r = np.random.default_rng(s)
            Fb, db, dlb, dlqb, dhb, _st = evaluate(np.tile(Gb, (NC, 1)), r)
            v = ~db
            vals.append(float(Fb[v].mean()) if v.any() else None)
        vals = [x for x in vals if x is not None]
        return float(np.mean(vals)) if vals else None
    base = batchF(champion, v_seeds)
    nf1 = batchF(champion, [SEED+705, SEED+706])
    noise_floor = abs(nf1 - base)
    sens = []
    for j in range(5):
        row = dict(gene=GN[j], base=base)
        for tag, m in (("m10", 0.90), ("p10", 1.10), ("m25", 0.75), ("p25", 1.25)):
            Gs = np.tile(champion, (NC, 1)); Gs[:, j] *= m
            Gs = np.clip(Gs, LO, HI)
            row[tag] = batchF(Gs, v_seeds)
        row['delta10'] = (row['p10'] - row['m10']) if (row['p10'] is not None and row['m10'] is not None) else None
        row['delta25'] = (row['p25'] - row['m25']) if (row['p25'] is not None and row['m25'] is not None) else None
        sens.append(row)
        print(f"[sens] {row['gene']}: base={base:.3f} ±10%Δ={row['delta10']} ±25%Δ={row['delta25']} "
              f"(noise≈{noise_floor:.3f})", flush=True)
    out['noise_floor'] = noise_floor
    out['sensitivity'] = sens
    with open('/home/user/hypergrid/ga_results.json', 'w') as f:
        json.dump(out, f, indent=1)
    print("[ga] wrote ga_results.json", flush=True)
