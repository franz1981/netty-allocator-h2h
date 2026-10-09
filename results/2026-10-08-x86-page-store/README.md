# lao's full matrix on the page store, x86, 2026-10-08

Charts in lao's report format: [benchmark.html](https://franz1981.github.io/netty-allocator-h2h/results/2026-10-08-x86-page-store/benchmark.html) ([specification](specification.md)); our own view: [index.html](https://franz1981.github.io/netty-allocator-h2h/results/2026-10-08-x86-page-store/index.html).
Same matrix as lao's 1.2.4-snap ARM report (netty/netty discussion #17485): `ByteBufAllocatorAllocPatternBenchmark`,
all params (3 patterns x 7 live counts x read-write on/off x direct/heap x POOLED/ADAPTIVE/MIMALLOC), 32 threads,
2 forks, 10x1 s warmup + 10x1 s measurement, event-loop and platform threads; plus ADAPTIVE direct with mmap off.

- Netty: franz1981/netty `adaptive-page-store` @ 34eff301a2; mimalloc port 1.2.4-SNAPSHOT (neoionet/netty-allocator 082a6d9).
- JDK 25.0.3 (mmap needs JDK 22+ and native access), flags: harness defaults + `-XX:MaxRAM=60g
  --enable-native-access=ALL-UNNAMED -XX:+ExitOnOutOfMemoryError`, `-prof gc`; platform: `-Djmh.executor=PLATFORM`;
  mmap off: `-Dio.netty.allocator.segmentRegionSize=0`.
- Ryzen 9 7950X, `numactl --cpunodebind=0 --preferred=0` (8 cores / 16 threads), 2.3 GHz, THP madvise, kernel 7.1.13.
- `run.sh` ran it; `gen.py` makes `cells.csv` (ns/op = JMH score; RSS = mean over forks of the last iteration's peak
  RSS; used = harness used-memory) and `index.html` from `page.tpl.html`.
