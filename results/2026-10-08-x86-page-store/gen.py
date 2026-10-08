#!/usr/bin/env python3
"""gen.py: cells.csv + index.html from JMH-{eventloop,platform,nommap-eventloop,nommap-platform}.{json,data}.
Per cell (2 forks): ns/op = JMH combined score; RSS = mean over forks of peak RSS (pRSS) at the last iteration;
used = the allocator's used memory at the last iteration (lao's report computes the same columns)."""
import json, os, re, statistics

R = os.path.dirname(os.path.abspath(__file__))
FILES = [('eventloop', 'eventloop', ''), ('platform', 'platform', ''),
         ('nommap-eventloop', 'eventloop', '_MMAP_OFF'), ('nommap-platform', 'platform', '_MMAP_OFF')]
PAR = re.compile(r'# Parameters: \(MAX_LIVE_BUFFERS = (\d+), allocatorType = (\w+), enableReadWrite = (\w+), '
                 r'sizePattern = (\w+)\)')


def side(path):
    """(bench, live, alloc, rw, pattern) -> ([pRSS of each fork's last iteration], [used ...])."""
    out, key, pending = {}, None, None

    def flush():
        if pending:
            k, rss, used = pending
            out.setdefault(k, ([], []))
            out[k][0].append(rss)
            out[k][1].append(used)

    for line in open(path, errors='replace'):
        if line.startswith('# Benchmark:'):
            bench = line.strip().split('.')[-1]
        m = PAR.match(line)
        if m:
            key = (bench, int(m.group(1)), m.group(2), m.group(3), m.group(4))
        if line.startswith('# Fork:'):
            flush()
            pending = None
        m = re.search(r'cRSS-pRSS:\[(\d+), (\d+)\]', line)
        if m:
            pending = (key, int(m.group(2)), pending[2] if pending and pending[0] == key else None)
        m = re.search(r'used-memory:\[(\d+)\]', line)
        if m and pending:
            pending = (pending[0], pending[1], int(m.group(1)))
    flush()
    return out


rows = []
for name, thr, suffix in FILES:
    sc = side(f'{R}/JMH-{name}.data')
    for e in json.load(open(f'{R}/JMH-{name}.json')):
        p = e['params']
        bench = e['benchmark'].split('.')[-1]
        k = (bench, int(p['MAX_LIVE_BUFFERS']), p['allocatorType'], p['enableReadWrite'], p['sizePattern'])
        r, u = sc.get(k, ([], []))
        rows.append(dict(threads=thr, method=bench.replace('Allocation', ''), live=k[1], alloc=k[2] + suffix,
                         rw=k[3], pattern=k[4], ns=round(e['primaryMetric']['score'], 1),
                         rss=round(statistics.mean(r)) if r else None,
                         used=round(statistics.mean(x for x in u if x is not None)) if any(x is not None for x in u)
                         else None, forks=len(r)))

with open(f'{R}/cells.csv', 'w') as f:
    cols = ['threads', 'method', 'pattern', 'rw', 'live', 'alloc', 'ns', 'rss', 'used', 'forks']
    f.write(','.join(cols) + '\n')
    for r in sorted(rows, key=lambda r: tuple(str(r[c]) for c in cols[:6])):
        f.write(','.join(str(r[c]) for c in cols) + '\n')

bad = [r for r in rows if r['forks'] != 2 or r['rss'] is None]
print(f'{len(rows)} cells, {len(bad)} without 2 forks of RSS')
open(f'{R}/data.json', 'w').write(json.dumps(
    [[r['threads'], r['method'], r['live'], r['alloc'], r['rw'], r['pattern'], r['ns'], r['rss'], r['used']]
     for r in rows], separators=(',', ':')))
