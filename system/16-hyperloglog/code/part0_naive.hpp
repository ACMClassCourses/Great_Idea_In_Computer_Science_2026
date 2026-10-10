#pragma once

#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>
#include "hash.hpp"

class HLL0 {
    int p_;
    uint64_t m_;
    std::vector<uint8_t> registers_;

public:
    explicit HLL0(int p = 12)
        : p_(p), m_(1ULL << p), registers_(m_, 0) {
        if (p < 4 || p > 14) {
            throw std::invalid_argument("p must be in [4, 14]");
        }
    }

    // value: 要加入 HLL 的原始字符串。
    // 目标：计算 hash、桶号和 rho，只在新的 rho 更大时更新寄存器。
    void add(const std::string& value) {
        // TODO:
        // 1. 用 hash64(value) 得到 64 位哈希值。
        // 2. 用 bucketIndex 得到桶号。
        // 3. 用 rho 得到 rank。
        // 4. 用较大值更新对应寄存器。
        throw std::logic_error("TODO: HLL0::add");
    }

    // 返回值：根据当前所有寄存器得到的基数估计值。
    // 目标：先算 HLL 原始估计；小基数时再做线性计数修正。
    double estimate() const {
        // TODO: 按任务文档中的公式计算 estimate。
        throw std::logic_error("TODO: HLL0::estimate");
    }

    // other: 要合并进当前对象的另一个 HLL0。
    // 目标：两个对象的 p 必须相同；每个位置的寄存器取最大值。
    void merge(const HLL0& other) {
        // TODO: 检查参数并逐个合并寄存器。
        throw std::logic_error("TODO: HLL0::merge");
    }

    uint64_t m() const {
        return m_;
    }
};
