# netty-allocator-h2h

Head-to-head measurements of Netty's `AdaptivePoolingAllocator` (the PR
[netty/netty#17151](https://github.com/netty/netty/pull/17151) branch) against the mimalloc Java port
([neoionet/netty-allocator](https://github.com/neoionet/netty-allocator)), on that project's own harness.
Raw JMH JSON, per-iteration RSS logs, the script that reduces them and the resulting page, one directory per round.

| round | page | data |
|---|---|---|
| 2026-09-22, x86 (Ryzen 9 7950X, one NUMA node, 2300 MHz, JDK 21) | [results/2026-09-22-x86/index.html](https://htmlpreview.github.io/?https://github.com/franz1981/netty-allocator-h2h/blob/main/results/2026-09-22-x86/index.html) | [results/2026-09-22-x86/](results/2026-09-22-x86/) |

How each round was produced is in the page header; `compare.py` regenerates the numbers from the JSON and `.data` files.
