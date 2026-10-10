#pragma once

#include <cstdint>
#include <string>

inline uint64_t splitmix64(uint64_t x) {
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

inline uint64_t fnv1a(const std::string& s) {
    uint64_t h = 14695981039346656037ULL;
    for (unsigned char c : s) {
        h ^= c;
        h *= 1099511628211ULL;
    }
    return h;
}

inline uint64_t hash64(const std::string& s) {
    return splitmix64(fnv1a(s));
}

inline uint64_t bucketIndex(uint64_t hash, int p) {
    return hash >> (64 - p);
}

inline uint8_t rho(uint64_t hash, int p) {
    uint64_t remaining = hash << p;
    uint8_t rank = 1;

    for (int i = 0; i < 64 - p; ++i) {
        if ((remaining & (1ULL << 63)) != 0) {
            return rank;
        }
        ++rank;
        remaining <<= 1;
    }

    return rank;
}

inline double hllAlpha(uint64_t m) {
    if (m == 16) return 0.673;
    if (m == 32) return 0.697;
    if (m == 64) return 0.709;
    return 0.7213 / (1.0 + 1.079 / static_cast<double>(m));
}
