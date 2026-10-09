#### 1. Allocators:
- [PooledByteBufAllocator](https://github.com/franz1981/netty/blob/34eff301a22d1337c96b70a950e3918dca35dcdc/buffer/src/main/java/io/netty/buffer/PooledByteBufAllocator.java).
- [AdaptivePoolingAllocator](https://github.com/franz1981/netty/blob/34eff301a22d1337c96b70a950e3918dca35dcdc/buffer/src/main/java/io/netty/buffer/AdaptivePoolingAllocator.java) with the page store, mmap on (default) and off (`-Dio.netty.allocator.segmentRegionSize=0`, direct only).
- MiMallocByteBufAllocator: netty-allocator 1.2.4.Final-SNAPSHOT (neoionet/netty-allocator 082a6d9).

#### 2. Server:
- x86: AMD Ryzen 9 7950X, run on NUMA node 0 only (`numactl --cpunodebind=0 --preferred=0`: 8 cores / 16 threads), CPU ceiling 2.3 GHz, kernel 7.1.13, THP `madvise`.

#### 3. Thread types:
- `Event loop thread` (`FastThreadLocalThread`) and `Platform thread` (`-Djmh.executor=PLATFORM`).

#### 4. Threads count:
- `32` threads.

#### 5. Java:
- `OpenJDK 25.0.3` (Temurin). JDK 22+ is needed for mmap (FFM).

#### 6. JVM args:
- `-XX:InitialRAMPercentage=40.0 -XX:MaxRAMPercentage=40.0 -Dio.netty.leakDetection.level=disabled -dsa -da` (harness defaults)
- `-XX:MaxRAM=60g` (same memory as the 60 GB ARM server), `--enable-native-access=ALL-UNNAMED`, `-XX:+ExitOnOutOfMemoryError`, `-prof gc`

#### 7. Data / 8. Benchmark code:
- `ByteBufAllocatorAllocPatternBenchmark`, patterns SOCKET_PROXY, API_GATEWAY, E_COMMERCE; 2 forks, 10 x 1 s warmup, 10 x 1 s measurement.

#### 9. Code base:
- Netty [franz1981/netty@34eff301a2](https://github.com/franz1981/netty/tree/34eff301a22d1337c96b70a950e3918dca35dcdc) (branch `adaptive-page-store`).

#### 10. Max live buffers per thread:
- `MAX_LIVE_BUFFERS`: [128, 1024, 4096, 8192, 16384, 32768, 65536].

#### 11. Switch on read-write:
- `enableReadWrite`: true and false.

RSS and used memory per cell: mean over the 2 forks of the last iteration's values, as in the 1.2.4-snap report. Raw JMH output: `JMH-*.data` / `JMH-*.json`.
