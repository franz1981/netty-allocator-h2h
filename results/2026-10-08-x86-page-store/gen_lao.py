#!/usr/bin/env python3
"""gen_lao.py: benchmark.html in lao's report format (neoionet/netty-allocator-benchmark-report 1.2.4-snap/benchmark.html,
Apache-2.0), x86 tabs filled with this run's cells, ARM tabs hidden, plus a dashed line for the page store with mmap off."""
import json, os
R = os.path.dirname(os.path.abspath(__file__))
s = open(f'{R}/lao-benchmark-1.2.4-snap.html').read()
D = json.load(open(f'{R}/data.json'))   # [threads, method, live, alloc, rw, pattern, ns, rss, used]
KEY = {'ADAPTIVE_MMAP_OFF': 'ADAPTIVE-MMAP-OFF'}
def rows(thr):
    return [[r[1], r[2], KEY.get(r[3], r[3]), r[4], r[5], round(r[6]), r[7], r[8]] for r in D if r[0] == thr]
def fill(block, thr):
    for a, b in [
        ('const D=[];', 'const D=' + json.dumps(rows(thr), separators=(',', ':')) + ';'),
        ('const AL=["POOLED","ADAPTIVE","MIMALLOC"];', 'const AL=["POOLED","ADAPTIVE","ADAPTIVE-MMAP-OFF","MIMALLOC"];'),
        ('const CLR={"POOLED":"#4a7fcb","ADAPTIVE":"#2aaa6e","MIMALLOC":"#d05a2a"};',
         'const CLR={"POOLED":"#4a7fcb","ADAPTIVE":"#2aaa6e","ADAPTIVE-MMAP-OFF":"#2aaa6e","MIMALLOC":"#d05a2a"};'),
        ('borderColor:CLR[a],backgroundColor:CLR[a]+"22",borderWidth:2,',
         'borderColor:CLR[a],backgroundColor:CLR[a]+"22",borderWidth:2,borderDash:a==="ADAPTIVE-MMAP-OFF"?[6,4]:[],'),
        ('<span><span class="lsq" style="background:#2aaa6e"></span>ADAPTIVE</span>',
         '<span><span class="lsq" style="background:#2aaa6e"></span>ADAPTIVE (page store, mmap)</span>\n'
         '  <span><span class="lsq" style="background:repeating-linear-gradient(90deg,#2aaa6e 0 6px,transparent 6px 10px)"></span>ADAPTIVE (page store, mmap off, direct only)</span>')]:
        assert block.count(a) == 1, (thr, a)
        block = block.replace(a, b)
    assert "'" not in block[block.find('const D='):block.find('const BUFS')]
    return block
def frame(s, fid):
    i = s.index(f'<iframe id="{fid}"'); e = s.index('</iframe>', i)
    return i, e
for fid, thr in (('f2', 'eventloop'), ('f3', 'platform')):
    i, e = frame(s, fid)
    s = s[:i] + fill(s[i:e], thr) + s[e:]
for a, b in [
    ('<!-- <button class="nav-btn active" onclick="show(this,2)">Eventloop on x86</button> -->',
     '<button class="nav-btn active" onclick="show(this,2)">Eventloop on x86</button>'),
    ('<button class="nav-btn active" onclick="show(this,0)">Eventloop on ARM</button>',
     '<!-- <button class="nav-btn" onclick="show(this,0)">Eventloop on ARM</button> -->'),
    ('<!-- <button class="nav-btn" onclick="show(this,3)">Platform on x86</button> -->',
     '<button class="nav-btn" onclick="show(this,3)">Platform on x86</button>'),
    ('<button class="nav-btn" onclick="show(this,1)">Platform on ARM</button>',
     '<!-- <button class="nav-btn" onclick="show(this,1)">Platform on ARM</button> -->')]:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
s = s.replace('<!DOCTYPE html>', '<!DOCTYPE html>\n<!-- Format: neoionet/netty-allocator-benchmark-report 1.2.4-snap/benchmark.html (Apache-2.0); '
              'data: Netty franz1981/netty adaptive-page-store @ 34eff301a2, x86, 2026-10-08, see specification.md -->', 1)
open(f'{R}/benchmark.html', 'w').write(s)
print('ok', len(s))
