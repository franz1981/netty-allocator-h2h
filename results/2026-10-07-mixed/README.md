# Mixed memory test, 2026-10-07, x86 (Ryzen 9 7950X, NUMA node 0), JDK 25

Test: `MixedMemoryTest` on [franz1981/netty-allocator `mixed-memory-test`](https://github.com/franz1981/netty-allocator/tree/mixed-memory-test) (see its README).
Interactive charts: [index.html](https://franz1981.github.io/netty-allocator-h2h/results/2026-10-07-mixed/index.html). One run per build and scenario.

Every build: `numactl --cpunodebind=0 --membind=0 java --enable-native-access=ALL-UNNAMED -Dtouch=true -Dio.netty.leakDetection.level=disabled -Xms2g -Xmx2g -XX:+AlwaysPreTouch -XX:MaxDirectMemorySize=16g MixedMemoryTest <allocator> 8 16 32 4 60 <scenario args>`

| build | allocator | extra flag | code |
| :--- | :--- | :--- | :--- |
| page store, mmap | `adaptive` | - | [franz1981/netty `adaptive-page-store`](https://github.com/franz1981/netty/tree/adaptive-page-store) (19a1da597e) |
| page store, malloc | `adaptive` | `-Dio.netty.allocator.segmentRegionSize=0` | same |
| PR #17151 | `adaptive` | - | [netty/netty#17151](https://github.com/netty/netty/pull/17151) at 1f303f34f9 |
| mimalloc | `mimalloc` | - | neoionet/netty-allocator 082a6d9 (1.2.4-SNAPSHOT) |

| scenario | args after `60` |
| :--- | :--- |
| default | `0` |
| burst2 | `0 active 30` |
| trickle | `1000` |
| silent | `0 silent` |

`summary.csv`: RSS above the run's idle baseline, MiB; `runs/<scenario>-<build>.log`: the raw output.
