// File Monitor (Basic, Part 1) — Snapshot Diff
// Online Judge submission framework only.
//
// Completing this file does NOT finish the full Basic assignment. You must
// also implement the real-directory polling monitor described in
// basic/README.md from scratch.
//
// Your task: given two directory snapshots read from stdin, print the change
// log to stdout. Read "Task 1: OJ snapshot comparison" in basic/README.md
// carefully before you start.
//
// Only fill in the two TODO functions below. The main function and the I/O
// parsing are already provided — do NOT modify them.
//
// Compile: g++ -std=c++17 -O2 -o monitor monitor.cpp

#include <iostream>
#include <map>
#include <string>
#include <vector>

struct FileInfo {
    long long size;
    long long mtime;
};

struct RawEntry {
    std::string name;
    long long size;
    long long mtime;
    char type; // 'F' = regular file, 'D' = subdirectory
};

struct Change {
    std::string op;   // "CREATE", "DELETE" or "MODIFY"
    std::string name;
};

// TODO 1: Build a snapshot from raw directory entries.
//
// Convert the raw entries scanned from one directory into a lookup table:
// a map from file name to its metadata (size and last-modified time).
//
// Requirements:
//   - Only regular files (type == 'F') may appear in the snapshot.
//     subdirectory entries ('D') must be skipped entirely — the Basic
//    monitor does not recurse into subdirectories.
//   - The input may list entries in ANY order; your snapshot must not
//    depend on that order.
//
// Hints:
//   - std::map keeps its keys sorted automatically. Think about whether
//     that property is useful for the output ordering required later.
//   - Reference reading (std::map):
//     https://en.cppreference.com/w/cpp/container/map
std::map<std::string, FileInfo> buildSnapshot(const std::vector<RawEntry>& entries) {
    // TODO: your code here.
    return {};
}

// TODO 2: Compare two snapshots and produce the change log.
//
// Given the old snapshot and the new snapshot, return every change as a
// Change{op, name}. The rules:
//   - present in `newSnap` but not in `oldSnap`          -> "CREATE"
//   - present in `oldSnap` but not in `newSnap`          -> "DELETE"
//   - present in both, but size or mtime differs         -> "MODIFY"
//   - present in both with identical size and mtime      -> no output
//
// Requirements:
//   - The returned changes must be ordered by file name in lexicographic
//     (byte-wise, i.e. ASCII) order — this is what makes the log
//     reproducible. Note that 'A'..'Z' sort before 'a'..'z'.
//   - A rename is NOT a special case: it appears as DELETE of the old name
//     plus CREATE of the new name. Do not try to detect renames.
//   - Aim for O((N0 + N1) log(N0 + N1)) or better. Comparing the two
//     snapshots with nested linear scans will be too slow for the large
//     test points (up to 100,000 entries per snapshot).
//
// Hints:
//   - If your snapshots are stored in std::map, iterating over a map
//     visits names in sorted order. Can you produce the sorted log by
//     merging two ordered sequences in one pass?
//   - Reference reading (filesystem metadata concepts behind this task):
//     https://learn.microsoft.com/zh-cn/cpp/standard-library/file-system-navigation?view=msvc-170
std::vector<Change> diffSnapshots(const std::map<std::string, FileInfo>& oldSnap,
                                  const std::map<std::string, FileInfo>& newSnap) {
    // TODO: your code here.
    return {};
}

// ---------------- provided I/O below — do not modify ----------------

static std::vector<RawEntry> readEntries() {
    long long n;
    std::cin >> n;
    std::vector<RawEntry> entries;
    entries.reserve(n);
    for (long long i = 0; i < n; ++i) {
        RawEntry e;
        std::cin >> e.name >> e.size >> e.mtime >> e.type;
        entries.push_back(std::move(e));
    }
    return entries;
}

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    std::vector<RawEntry> oldEntries = readEntries();
    std::vector<RawEntry> newEntries = readEntries();

    std::map<std::string, FileInfo> oldSnap = buildSnapshot(oldEntries);
    std::map<std::string, FileInfo> newSnap = buildSnapshot(newEntries);

    for (const Change& c : diffSnapshots(oldSnap, newSnap)) {
        std::cout << c.op << ' ' << c.name << '\n';
    }
    return 0;
}
