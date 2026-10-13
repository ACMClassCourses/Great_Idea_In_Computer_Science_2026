#ifndef BLOOM_FILTER_SRC_HPP
#define BLOOM_FILTER_SRC_HPP

#include "hash.hpp"
#include "memory.hpp"

#include <cstddef>
#include <string>

class BloomFilter {
public:
    BloomFilter(std::size_t bit_count, int hash_count)
        : bit_count_(bit_count),
          hash_count_(hash_count),
          memory_(1) {
        // TODO: Allocate the bit array.
    }

    void add(const std::string& text) {
        (void)text;
        // TODO: Add one string.
    }

    bool contains(const std::string& text) const {
        (void)text;
        // TODO: Check one string.
        return false;
    }

    std::size_t storage_bytes() const {
        return memory_.size();
    }

private:
    std::size_t hash_position(const std::string& text, int number) const {
        (void)text;
        (void)number;
        // TODO: Compute one hash position.
        return 0;
    }

    void set_bit(std::size_t position) {
        (void)position;
        // TODO: Set one bit.
    }

    bool get_bit(std::size_t position) const {
        (void)position;
        // TODO: Read one bit.
        return false;
    }

    std::size_t bit_count_;
    int hash_count_;
    Memory memory_;
};

#endif
