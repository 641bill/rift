#!/usr/bin/env python3
"""Summarize macOS sample profiles into coarse work categories.

This is an L4 diagnostic helper. It parses the "Sort by top of stack" section
from macOS /usr/bin/sample reports and buckets top-frame samples by rough work
class so heap and checked-region profiles can be compared at the same level:
parser/hash/input, query mutator, allocation/init, GC/metadata, and runtime
noise. The buckets are heuristic and should not be used as headline timing.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable


CATEGORY_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    (
        "startup_or_idle",
        (
            r"\bkevent\b",
            r"\bthread_start\b",
            r"\b_dyld_start\b",
            r"\bstart\s+\(in dyld\)",
            r"ProcessExitChecker",
        ),
    ),
    (
        "parser_input_hash",
        (
            r"BenchmarkInputSupport",
            r"ByteLineReader",
            r"DelimitedByteFields",
            r"parseCurrentLine",
            r"parseMilliDecimal",
            r"stableHash",
            r"tokenHash",
            r"tokenSeparator",
            r"containsAscii",
            r"readLineFields",
            r"readLogLineFields",
            r"StringD6charAt",
            r"StringD6length",
            r"StringD6equals",
            r"tsvField",
            r"\bread\b",
            r"libz",
            r"zlibOps",
            r"scalanative_inflate",
            r"\binflate\b",
        ),
    ),
    (
        "token_handle_plumbing",
        (
            r"checkOpen",
            r"isOpen",
            r"stale",
            r"allocImpl",
            r"allocUncheckedImpl",
            r"RiftAllocator",
            r"HeapRoot",
            r"pageToken.*RegionFor",
            r"childRegion",
            r"childBucketRegion",
            r"regionFor",
        ),
    ),
    (
        "callback_ref_shape",
        (
            r"scala\.runtime\.(?:IntRef|LongRef|BooleanRef|ObjectRef|DoubleRef|FloatRef|CharRef|ShortRef|ByteRef)",
        ),
    ),
    (
        "traversal_cursor_capsule",
        (
            r"Cursor",
            r"cursor",
            r"drain",
            r"drainInto",
            r"AlertCapsule",
            r"appendChecked",
            r"closeRecords",
            r"StreamAppend",
            r"StreamWindow",
            r"StreamBucket",
            r"Bucket",
            r"Window",
        ),
    ),
    (
        "region_alloc_init",
        (
            r"scalanative_rift_",
            r"RiftRuntime",
            r"SafeZone",
            r"safezone",
            r"scalanative_zone_",
        ),
    ),
    (
        "safepoint_poll",
        (
            r"scalanative_GC_yield",
        ),
    ),
    (
        "heap_alloc_init",
        (
            r"Allocator_Alloc",
            r"scalanative_GC_alloc",
            r"ObjectMeta_SetAllocated",
        ),
    ),
    (
        "boxing_runtime",
        (
            r"scala\.scalanative\.runtime\.Boxes",
            r"\bBoxes\$",
            r"boxTo",
            r"unboxTo",
        ),
    ),
    (
        "gc_mark_sweep_metadata",
        (
            r"Marker_",
            r"Marker",
            r"Heap_IsWordInHeap",
            r"ObjectMeta_",
            r"Block_",
            r"Bytemap_",
            r"Stack_",
            r"Sweep",
        ),
    ),
    (
        "zeroing_memset",
        (
            r"_platform_memset",
            r"__memset",
            r"\bmemset\b",
        ),
    ),
    (
        "query_mutator",
        (
            r"BroomRetainedDataflowMatrixHelpers",
            r"StreamFlexDesignMatrixHelpers",
            r"TheodolitePowerRegionMatrixHelpers",
            r"DSPBenchRegionMatrixHelpers",
            r"LogHubRetainedSessionMatrixHelpers",
            r"FraudPredictorState",
            r"LogStatusState",
            r"StableState",
            r"MatrixHelpers",
            r"runHeap",
            r"runChecked",
            r"anonfun",
            r"generated",
            r"selected",
            r"\bmix",
            r"\bfold",
            r"uc4",
            r"process",
            r"Epoch",
            r"TopK",
            r"Bucket",
            r"Join",
            r"Aggregate",
        ),
    ),
]


SORT_HEADER = re.compile(r"^Sort by top of stack")
SAMPLE_LINE_PREFIX_COUNT = re.compile(r"^\s*(\d+)\s+(.+)$")
SAMPLE_LINE_SUFFIX_COUNT = re.compile(r"^\s*(.+?)\s+(\d+)\s*$")
QUERY_TOP_FRAME_PATTERNS = (
    r"LogHubRetainedSessionMatrixHelpers.*anonfun",
    r"StreamFlexDesignMatrixHelpers.*anonfun",
)
CALLBACK_REF_PATTERN = re.compile(
    r"scala\.runtime\.(?:IntRef|LongRef|BooleanRef|ObjectRef|DoubleRef|FloatRef|CharRef|ShortRef|ByteRef)",
    re.IGNORECASE,
)


def classify(symbol: str) -> str:
    if CALLBACK_REF_PATTERN.search(symbol):
        return "callback_ref_shape"
    # Munged Scala Native closure symbols include parameter type names. For
    # example, the checked LogHub/Wikimedia session-loop closure mentions
    # StreamingByteLineSource in its signature even when the top-frame work is
    # the session/query loop rather than the input reader. Classify those
    # closure top frames before the broad parser/input patterns.
    for pattern in QUERY_TOP_FRAME_PATTERNS:
        if re.search(pattern, symbol, re.IGNORECASE):
            return "query_mutator"
    for category, patterns in CATEGORY_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, symbol, re.IGNORECASE):
                return category
    return "other"


def parse_sorted_samples(path: Path) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    in_section = False
    for line in path.read_text(errors="replace").splitlines():
        if not in_section:
            if SORT_HEADER.search(line):
                in_section = True
            continue
        if not line.strip():
            break
        match = SAMPLE_LINE_PREFIX_COUNT.match(line)
        if match:
            rows.append((int(match.group(1)), match.group(2).strip()))
            continue
        match = SAMPLE_LINE_SUFFIX_COUNT.match(line)
        if match:
            rows.append((int(match.group(2)), match.group(1).strip()))
    return rows


def summarize(path: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for count, symbol in parse_sorted_samples(path):
        category = classify(symbol)
        counts[category] = counts.get(category, 0) + count
    return counts


def categories_from(summaries: Iterable[dict[str, int]]) -> list[str]:
    preferred = [category for category, _ in CATEGORY_PATTERNS] + ["other"]
    seen = set()
    for summary in summaries:
        seen.update(summary)
    return [category for category in preferred if category in seen]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seconds",
        type=float,
        default=5.0,
        help="sampling duration for samples/sec normalization; default: 5.0",
    )
    parser.add_argument("profiles", nargs="+", type=Path)
    args = parser.parse_args()

    summaries = [(path, summarize(path)) for path in args.profiles]
    categories = categories_from(summary for _, summary in summaries)

    print("profile\tcategory\tsamples\tsamples_per_sec\tpct_total\tpct_active_non_idle")
    for path, summary in summaries:
        total = sum(summary.values())
        active = total - summary.get("startup_or_idle", 0)
        for category in categories:
            count = summary.get(category, 0)
            pct_total = (count / total * 100.0) if total else 0.0
            pct_active = (count / active * 100.0) if active else 0.0
            print(
                f"{path.name}\t{category}\t{count}\t{count / args.seconds:.2f}\t"
                f"{pct_total:.2f}\t{pct_active:.2f}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
