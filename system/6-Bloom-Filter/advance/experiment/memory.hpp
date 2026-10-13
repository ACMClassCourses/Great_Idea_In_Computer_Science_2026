#ifndef BLOOM_FILTER_MEMORY_HPP
#define BLOOM_FILTER_MEMORY_HPP

#include <cstddef>
#include <cstdint>
#include <vector>

class Memory {
public:
    explicit Memory(std::size_t byte_count)
        : data_(byte_count, 0) {
    }

    std::uint8_t read(std::size_t index) const {
        return data_.at(index);
    }

    void write(std::size_t index, std::uint8_t value) {
        data_.at(index) = value;
    }

    std::size_t size() const {
        return data_.size();
    }

private:
    std::vector<std::uint8_t> data_;
};

#endif
