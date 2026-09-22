import json,re,sys,math,collections
E='/home/forked_franz/IdeaProjects/netty-bench/results/h2h-merged-x86-2026-09-22'
def rss(path):
    out={}; bench=pat=live=alloc=None
    for line in open(path,errors='replace'):
        if line.startswith('# Benchmark:'): bench=line.strip().split('.')[-1]
        m=re.match(r'# Parameters: \(MAX_LIVE_BUFFERS = (\d+), allocatorType = (\w+), enableReadWrite = (\w+), sizePattern = (\w+)',line)
        if m: live,alloc,rw,pat=int(m.group(1)),m.group(2),m.group(3),m.group(4); live=live if rw=='true' else None
        m=re.search(r'cRSS-pRSS:\[(\d+), (\d+)\]',line)
        if m and live: out.setdefault((pat,bench,live,alloc),[]).append(int(m.group(2)))
    return out
cells={}  # (pattern,threads,bench,live) -> alloc -> (ns, rss)
for thr in ('eventloop','platform'):
    for f in (f'JMH-{thr}',f'JMH-ecommerce-{thr}'):
        r=rss(f'{E}/{f}.data')
        for e in json.load(open(f'{E}/{f}.json')):
            p=e['params']
            if p['enableReadWrite']!='true' or 'primaryMetric' not in e: continue
            bench=e['benchmark'].split('.')[-1].replace('Allocation',''); live=int(p['MAX_LIVE_BUFFERS'])
            k=(p['sizePattern'],thr,bench,live); rr=r.get((p['sizePattern'],e['benchmark'].split('.')[-1],live,p['allocatorType']))
            cells.setdefault(k,{})[p['allocatorType']]=(e['primaryMetric']['score'],max(rr) if rr else None)
rows=[]
for k,v in sorted(cells.items()):
    if 'ADAPTIVE' in v and 'MIMALLOC' in v:
        a,m=v['ADAPTIVE'],v['MIMALLOC']; rows.append((k,a[0]/m[0],a[1]/m[1] if a[1] and m[1] else None,a,m))
def geo(xs): xs=[x for x in xs if x]; return math.exp(sum(map(math.log,xs))/len(xs)) if xs else float('nan')
print('cells',len(rows))
print('%-28s %5s %8s %8s %8s %8s %6s %6s'%('group','n','lat_geo','rss_geo','lat_max','rss_max','>1.10','<0.90'))
groups=collections.OrderedDict()
for k,l,r,a,m in rows:
    for g in ('ALL',f'{k[1]} {k[2]}',k[0]): groups.setdefault(g,[]).append((l,r))
for g,xs in groups.items():
    ls=[l for l,_ in xs]; rs=[r for _,r in xs]
    print('%-28s %5d %8.3f %8.3f %8.2f %8.2f %6d %6d'%(g,len(xs),geo(ls),geo(rs),max(ls),max(x for x in rs if x),sum(l>1.10 for l in ls),sum(l<0.90 for l in ls)))
print('\nADAPTIVE / MIMALLOC per cell, latency > 1.10 or RSS > 1.25:')
for k,l,r,a,m in rows:
    if l>1.10 or (r and r>1.25): print('  %-12s %-9s %-6s %6d  lat %5.2f (%5.0f vs %5.0f)  rss %5.2f (%5s vs %5s)'%(*k,l,a[0],m[0],r or float('nan'),a[1],m[1]))
print('\nADAPTIVE ahead by > 10% on latency:')
for k,l,r,a,m in rows:
    if l<0.90: print('  %-12s %-9s %-6s %6d  lat %5.2f (%5.0f vs %5.0f)  rss %5.2f'%(*k,l,a[0],m[0],r or float('nan')))
json.dump([dict(pattern=k[0],threads=k[1],buffers=k[2],live=k[3],lat_ratio=l,rss_ratio=r,adaptive_ns=a[0],adaptive_rss=a[1],mimalloc_ns=m[0],mimalloc_rss=m[1]) for k,l,r,a,m in rows],open(f'{E}/ratios.json','w'),indent=1)
