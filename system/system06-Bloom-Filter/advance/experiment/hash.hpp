#ifndef BLOOM_FILTER_HASH_HPP
#define BLOOM_FILTER_HASH_HPP

#include <cstdint>
#include <string>

inline std::uint64_t hash64(const std::string& text) {
    std::uint64_t value = 14695981039346656037ULL;
    for (std::size_t i = 0; i < text.size(); ++i) {
        value ^= static_cast<unsigned char>(text[i]);
        value *= 1099511628211ULL;
    }
    return value;
}

inline std::uint64_t splitmix64(std::uint64_t value) {
    value += 0x9e3779b97f4a7c15ULL;
    value = (value ^ (value >> 30)) * 0xbf58476d1ce4e5b9ULL;
    value = (value ^ (value >> 27)) * 0x94d049bb133111ebULL;
    return value ^ (value >> 31);
}

#endif
