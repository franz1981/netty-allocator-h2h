#!/bin/bash
# Full lao matrix (ByteBufAllocatorAllocPatternBenchmark, all default params: 3 patterns x 7 live x rw on/off x direct/heap
# x POOLED/ADAPTIVE/MIMALLOC) on Netty 34eff301a2 (page store, mmap default), event-loop and platform threads, plus
# ADAPTIVE direct with mmap off (-Dio.netty.allocator.segmentRegionSize=0). JDK 25, 32 threads, 2 forks (as lao 1.2.4-snap), 10x1 s + 10x1 s.
set -u
R=$(cd "$(dirname "$0")" && pwd)
J=/home/forked_franz/.sdkman/candidates/java/25.0.3-tem/bin/java
H=/home/forked_franz/IdeaProjects/netty-bench/results/page-store-large-x86-2026-09-30/h2h   # holds e-commerce.jfr
[ "$(cat $R/head.jar.commit)" = 34eff301a2 ] || { echo "jar commit mismatch"; exit 2; }
COMMON=(-t 32 -f 2 -wi 10 -i 10 -w 1 -r 1 -prof gc -jvmArgsAppend -XX:MaxRAM=60g
        -jvmArgsAppend --enable-native-access=ALL-UNNAMED -jvmArgsAppend -XX:+ExitOnOutOfMemoryError)
{ $J -version 2>&1; uname -r; cat /sys/kernel/mm/transparent_hugepage/enabled; lscpu | grep -E 'Model name|^CPU\(s\)|NUMA node0'; date; } > $R/environment.txt
cd $H
run() { # name, benchmark regex, extra args...
  local n=$1 b=$2; shift 2
  echo "$(date '+%F %T') START $n" >> $R/progress.log; local T0=$(date +%s)
  numactl --cpunodebind=0 --preferred=0 $J -jar $R/head.jar "$b" "${COMMON[@]}" "$@" \
    -rf json -rff $R/JMH-$n.json > $R/JMH-$n.data 2>&1
  local rc=$?
  echo "$(date '+%F %T') END $n rc=$rc elapsed=$(( $(date +%s) - T0 ))s runs=$(grep -c '^# Parameters' $R/JMH-$n.data) oom=$(grep -c 'Terminating due to java.lang.OutOfMemoryError' $R/JMH-$n.data) unsafe-flag=$(grep -c 'sun-misc-unsafe-memory-access' $R/JMH-$n.data)" >> $R/progress.log
}
run eventloop ByteBufAllocatorAllocPatternBenchmark
run platform ByteBufAllocatorAllocPatternBenchmark -jvmArgsAppend -Djmh.executor=PLATFORM
run nommap-eventloop ByteBufAllocatorAllocPatternBenchmark.directAllocation -p allocatorType=ADAPTIVE -jvmArgsAppend -Dio.netty.allocator.segmentRegionSize=0
run nommap-platform ByteBufAllocatorAllocPatternBenchmark.directAllocation -p allocatorType=ADAPTIVE -jvmArgsAppend -Dio.netty.allocator.segmentRegionSize=0 -jvmArgsAppend -Djmh.executor=PLATFORM
