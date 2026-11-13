# route2.py - windowed A* router (3 layers: Top, Bottom, Inner2), per-net width, pour-net handling.
# usage: py route2.py in.dsn order.txt out.json [prev.json ...]
#   order.txt: one net per line, optional "NET width"
#   prev.json: already routed results to paint first (resume)
# env: MZG grid (5), MZM extra clearance margin (2), MZN node limit (4e6), MZPAD window margin (900)
import sys, os, json, heapq, math, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import *

H = 9850
ps, pins, pinnet, wires, vias = load(sys.argv[1])
order = []
for line in open(sys.argv[2]):
    p = line.split()
    if p: order.append((p[0], float(p[1]) if len(p) > 1 else 12.0, [tuple(map(float, q.split(','))) for q in p[2].split(';')] if len(p) > 2 else None))
OUT = sys.argv[3]
prev_files = sys.argv[4:]

nets = sorted(set(pinnet.values()) | {w[0] for w in wires} | {v[0] for v in vias})
NID = {n: i + 1 for i, n in enumerate(nets)}
lab = [np.zeros((NY, NX), np.int32) for _ in range(3)]
thr = np.zeros((NY, NX), np.int32)
CLR = 9.9
MG = float(os.environ.get('MZM', '2'))
NMAX = int(float(os.environ.get('MZN', '4e6')))
PADW = float(os.environ.get('MZPAD', '900'))
VIAD = 31.5


def paint_box(arr, fn, nid, x0, y0, x1, y1):
    # paint only inside a bounding box (DSN coords) to keep PIL images small
    c0 = max(int((x0 - OX) / G) - 2, 0); c1 = min(int((x1 - OX) / G) + 3, NX)
    r0 = max(int((OY - y1) / G) - 2, 0); r1 = min(int((OY - y0) / G) + 3, NY)
    if c1 <= c0 or r1 <= r0: return
    im = Image.new('1', (c1 - c0, r1 - r0), 0); dr = ImageDraw.Draw(im)
    class D:  # shift drawing
        def ellipse(s, b, fill): dr.ellipse([b[0] - c0, b[1] - r0, b[2] - c0, b[3] - r0], fill=fill)
        def polygon(s, pts, fill): dr.polygon([(a - c0, b - r0) for a, b in pts], fill=fill)
        def line(s, pts, fill, width): dr.line([(a - c0, b - r0) for a, b in pts], fill=fill, width=width)
    fn(D())
    m = np.array(im, bool)
    arr[r0:r1, c0:c1][m] = nid


def pad_ext(sh):
    kind, a = sh
    if kind == 'circle': return a[0] / 2 + 2
    return max(abs(v) for v in a[1:]) + 2


VIA = ('circle', [VIAD])
for pid, (pst, x, y) in pins.items():
    n = pinnet.get(pid); nid = NID.get(n, -1) if n else -1
    sh = ps[pst]; e = max(pad_ext(s) for s in sh.values())
    for z, L in enumerate(LAY):
        if L in sh: paint_box(lab[z], lambda dr: draw_pad(dr, sh[L], x, y), nid, x - e, y - e, x + e, y + e)
    paint_box(thr, lambda dr: draw_pad(dr, sh.get('TopLayer') or list(sh.values())[0], x, y), nid, x - e, y - e, x + e, y + e)

edge = np.ones((NY, NX), bool); e = int(25 / G); edge[e:-e, e:-e] = False
for k in [k for k in os.environ.get('MZKO', '').split(';') if k]:
    x0, y0, x1, y1 = map(float, k.split(','))
    c0, c1 = int((x0 - OX) / G), int((x1 - OX) / G); r0, r1 = int((OY - (y1 + H)) / G), int((OY - (y0 + H)) / G)
    for z in range(3): lab[z][max(r0, 0):r1, max(c0, 0):c1] = -1

# pour regions (EasyEDA coords) -> masks in grid (Inner1 only, so they only act as connection targets)
def poly_mask(P):
    im = Image.new('1', (NX, NY), 0); dr = ImageDraw.Draw(im)
    dr.polygon([((P[i] - OX) / G, (OY - (P[i + 1] + H)) / G) for i in range(0, len(P), 2)], fill=1)
    return np.array(im, bool)
A = [4470, -15, 9200, -15, 9200, -4250, 5980, -4250, 5980, -6380, 4470, -6380]
B1 = [8880, -8500, 10935, -8500, 10935, -9835, 8880, -9835]
B2 = [11295, -8500, 13560, -8500, 13560, -9835, 11295, -9835]
GNDA_M = poly_mask(A) | poly_mask(B1) | poly_mask(B2)
GND_M = ~GNDA_M
ER = int(200 / G)
from scipy import ndimage as ndi
POUR = {'GND': ndi.binary_erosion(GND_M, iterations=ER), 'GNDA': ndi.binary_erosion(GNDA_M, iterations=ER)}
POUR_PAD = {'GND': GND_M, 'GNDA': GNDA_M}

out = []
for an, AP in json.loads(os.environ.get('AREAS', '[]')):
    m = poly_mask(AP) & (lab[2] == 0); lab[2][m] = NID[an]


def commit(path, nid, w, endvia=False):
    segs = []; vs = []
    for a, b in zip(path, path[1:]):
        if a[0] != b[0]: vs.append(a)
        else: segs.append((a, b))
    if endvia: vs.append(path[-1])
    for z, y, x in vs:
        X, Y = OX + x * G, OY - y * G
        for zz in range(3): paint_box(lab[zz], lambda dr: draw_pad(dr, VIA, X, Y), nid, X - 20, Y - 20, X + 20, Y + 20)
        paint_box(thr, lambda dr: draw_pad(dr, VIA, X, Y), nid, X - 20, Y - 20, X + 20, Y + 20)
    for a, b in segs:
        P = (OX + a[2] * G, OY - a[1] * G); Q = (OX + b[2] * G, OY - b[1] * G)
        paint_box(lab[a[0]], lambda dr: draw_line(dr, P, Q, w), nid, min(P[0], Q[0]) - w, min(P[1], Q[1]) - w, max(P[0], Q[0]) + w, max(P[1], Q[1]) + w)
    rec = {'net': nets[nid - 1], 'w': w, 'path': [(z, OX + x * G, OY - y * G) for z, y, x in path], 'endvia': endvia}
    out.append(rec)


# replay previous results
for f in prev_files:
    for r in json.load(open(f)):
        nid = NID[r['net']]
        p = [(z, int(round((OY - y) / G)), int(round((x - OX) / G))) for z, x, y in r['path']]
        commit(p, nid, r.get('w', 12), r.get('endvia', False))

NB = [(0, 1, 1), (0, -1, 1), (1, 0, 1), (-1, 0, 1), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
VC = 40.0


HW = float(os.environ.get('MZHW', '1.5'))


PBAND = float(os.environ.get('MZPB', '45')); PK = float(os.environ.get('MZPK', '4'))


def astar(S, T, free, viaok, hz, R, C, pen):
    RC = R * C; N = 3 * RC; INF = 1e18
    pas = bytearray(np.concatenate([(free[z] | T[z] | S[z]).ravel() for z in range(3)]).astype(np.uint8).tobytes())
    tg = bytearray(np.concatenate([(T[z] & ~S[z]).ravel() for z in range(3)]).astype(np.uint8).tobytes())
    vo = bytearray(viaok.ravel().astype(np.uint8).tobytes())
    hl = (hz.ravel() * HW).tolist()
    pl = np.concatenate([p.ravel() for p in pen]).tolist()
    dist = [INF] * N; prev = {}; pq = []
    for z in range(3):
        for k in (np.flatnonzero(S[z].ravel()) + z * RC).tolist():
            dist[k] = 0.0; heapq.heappush(pq, (hl[k % RC], 0.0, k))
    nb = [(1, 1.0), (-1, 1.0), (C, 1.0), (-C, 1.0), (C + 1, 1.4142), (C - 1, 1.4142), (-C + 1, 1.4142), (-C - 1, 1.4142)]
    n = 0; push = heapq.heappush; pop = heapq.heappop
    while pq:
        f, g, k = pop(pq)
        if g > dist[k]: continue
        n += 1
        if tg[k]:
            p = [k]
            while k in prev: k = prev[k]; p.append(k)
            return [(q // RC, (q % RC) // C, q % C) for q in p[::-1]]
        if n > NMAX: return None
        z, r = divmod(k, RC); y, x = divmod(r, C)
        for d, c in nb:
            dx = d % C if False else None
            k2 = k + d
            if d in (1, C + 1, -C + 1) and x == C - 1: continue
            if d in (-1, C - 1, -C - 1) and x == 0: continue
            if d > 1 and y == R - 1: continue
            if d < -1 and y == 0: continue
            if not pas[k2]: continue
            g2 = g + c * (1.0 + pl[k2])
            if g2 < dist[k2]: dist[k2] = g2; prev[k2] = k; push(pq, (g2 + hl[r + (d)], g2, k2))
        if vo[r]:
            for z2 in range(3):
                if z2 == z: continue
                k2 = z2 * RC + r; g2 = g + VC
                if pas[k2] and g2 < dist[k2]: dist[k2] = g2; prev[k2] = k; push(pq, (g2 + hl[r], g2, k2))
    return None


def los(z, a, b, free, S, T):
    (y0, x0), (y1, x1) = a, b; n = int(max(abs(y1 - y0), abs(x1 - x0)) * 2) + 1
    for i in range(n + 1):
        t = i / n; y = int(round(y0 + (y1 - y0) * t)); x = int(round(x0 + (x1 - x0) * t))
        if not (free[z][y, x] or S[z][y, x] or T[z][y, x]): return False
    return True


def smooth(path, free, S, T):
    out_ = [path[0]]; i = 0
    while i < len(path) - 1:
        z = path[i][0]; e = i
        while e + 1 < len(path) and path[e + 1][0] == z: e += 1
        if e == i: out_.append(path[i + 1]); i += 1; continue
        best = i + 1
        for j in range(e, i, -1):
            if los(z, path[i][1:], path[j][1:], free, S, T): best = j; break
        out_.append(path[best]); i = best
    return out_


def route_net(n, w, pad, only=None):
    nid = NID[n]
    pinpos = [(x, y) for pid, (pst, x, y) in pins.items() if pinnet.get(pid) == n]
    pour = POUR.get(n) if only is None else None
    if only is not None: pinpos = [(x, y + H) for x, y in only]
    if pour is not None:   # only pins outside own pour need a route
        pinpos = [(x, y) for x, y in pinpos if not POUR_PAD[n][min(max(int(round((OY - y) / G)), 0), NY - 1), min(max(int(round((x - OX) / G)), 0), NX - 1)]]
        if not pinpos: return 'pour-ok'
    xs = [p[0] for p in pinpos]; ys = [p[1] for p in pinpos]
    x0, x1 = min(xs) - pad, max(xs) + pad; y0, y1 = min(ys) - pad, max(ys) + pad
    c0, c1 = max(int((x0 - OX) / G), 0), min(int((x1 - OX) / G) + 1, NX)
    r0, r1 = max(int((OY - y1) / G), 0), min(int((OY - y0) / G) + 1, NY)
    R, C = r1 - r0, c1 - c0
    Lz = [lab[z][r0:r1, c0:c1] for z in range(3)]; Th = thr[r0:r1, c0:c1]
    TR = w / 2 + CLR + MG; VR = VIAD / 2 + CLR + MG
    bord = np.zeros((R, C), bool); b = int(math.ceil(TR / G)) + 1
    if r0 > 0: bord[:b] = True
    if r1 < NY: bord[-b:] = True
    if c0 > 0: bord[:, :b] = True
    if c1 < NX: bord[:, -b:] = True
    ed = edge[r0:r1, c0:c1] | bord
    free = []; obany = np.zeros((R, C), bool); pen = []
    for z in range(3):
        ob = (Lz[z] != 0) & (Lz[z] != nid); obany |= ob
        dd = ndimage.distance_transform_edt(~ob) * G
        free.append((dd >= TR) & ~ed)
        pen.append(np.clip((TR + PBAND - dd) / PBAND, 0, 1) * PK)
    viaok = (ndimage.distance_transform_edt(~obany) * G >= VR) & ~ed
    loc = lambda x, y: (int(round((OY - y) / G)) - r0, int(round((x - OX) / G)) - c0)
    pour_l = pour[r0:r1, c0:c1] & viaok if pour is not None else None

    def comps():
        labs = []; off = 0
        for z in range(3):
            l, k = ndimage.label(Lz[z] == nid, structure=np.ones((3, 3))); l[l > 0] += off; labs.append(l); off += k
        par = list(range(off + 1))
        def f(a):
            while par[a] != a: par[a] = par[par[a]]; a = par[a]
            return a
        tm = Th == nid
        for z in range(1, 3):
            for u, v in set(zip(labs[0][tm].tolist(), labs[z][tm].tolist())):
                if u and v: par[f(u)] = f(v)
        mp = np.array([f(i) for i in range(off + 1)], np.int64)
        return [mp[l] for l in labs]

    nres = 0
    for it in range(400):
        labs = comps()
        pc = []
        for x, y in pinpos:
            yy, xx = loc(x, y)
            if 0 <= yy < R and 0 <= xx < C and labs[0][yy, xx]: pc.append(int(labs[0][yy, xx]))
        pcs = sorted(set(pc))
        if pour is not None:
            if not pcs: return 'pour-ok %d paths' % nres
            src = pcs[0]
            S = [labs[z] == src for z in range(3)]
            others = pcs[1:]
            T = [np.isin(labs[z], others) | pour_l for z in range(3)]
        else:
            if len(pcs) < 2: return 'ok %d paths' % nres
            # grow from the component with most pins
            src = max(pcs, key=pc.count)
            S = [labs[z] == src for z in range(3)]
            T = [np.isin(labs[z], [c for c in pcs if c != src]) for z in range(3)]
        tany = T[0] | T[1] | T[2]
        hz = ndimage.distance_transform_edt(~tany)
        path = astar(S, T, free, viaok, hz, R, C, pen)
        if path is None: return 'FAIL %d/%d' % (nres, len(pcs))
        path = smooth(path, free, S, T)
        z, y, x = path[-1]
        endvia = pour is not None and pour_l[y, x] and not any(np.isin(labs[zz][y, x], others) for zz in range(3))
        commit([(z, y + r0, x + c0) for z, y, x in path], nid, w, bool(endvia))
        nres += 1
        if endvia:  # this component now reaches the pour: drop its pins
            pinpos = [(px, py) for px, py in pinpos if int(labs[0][loc(px, py)]) != src]
    return 'iter-limit'


t0 = time.time()
for n, w, only in order:
    if n not in NID: print(n, 'unknown', flush=True); continue
    t = time.time()
    r = route_net(n, w, PADW, only)
    if r.startswith('FAIL'):
        r2 = route_net(n, w, PADW * 3, only)
        r = r + ' -> retry ' + r2
        if r2.startswith('FAIL') and w > 12:
            r += ' -> w12 ' + route_net(n, 12, PADW * 3, only)
    print('%-14s w%-4g %s  %.1fs' % (n, w, r, time.time() - t), flush=True)
    json.dump(out, open(OUT, 'w'))
json.dump(out, open(OUT, 'w'))
print('DONE %.0fs' % (time.time() - t0))
