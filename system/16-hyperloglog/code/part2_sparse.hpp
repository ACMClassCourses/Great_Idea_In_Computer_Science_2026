#pragma once

#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>
#include "part1_dense.hpp"

struct SparseEntry {
    uint32_t index;
    uint8_t value;
};

class SparseHLL {
    int p_;
    uint64_t m_;
    bool is_dense_;
    std::vector<SparseEntry> entries_;
    DenseHLL dense_data_;

    // 返回值：当前 sparse 正文编码后需要的字节数。
    size_t sparseBytes() const {
        // TODO: 按 ZERO、XZERO、VAL 的编码规则计算长度。
        throw std::logic_error("TODO: SparseHLL::sparseBytes");
    }

    size_t denseBytes() const {
        return m_ * 6 / 8;
    }

    // index: 要更新的寄存器下标。
    // value: 这个寄存器的新候选值。
    // 返回值：如果 sparse 内容真的发生变化则为 true，否则为 false。
    // 目标：entries_ 只保存非零寄存器，并始终按 index 递增。
    bool updateEntry(uint32_t index, uint8_t value) {
        // TODO: 查找 index；已有项取较大值，不存在时插入正确位置。
        throw std::logic_error("TODO: SparseHLL::updateEntry");
    }

public:
    explicit SparseHLL(int p = 12)
        : p_(p), m_(1ULL << p), is_dense_(false), dense_data_(p) {
        if (p < 4 || p > 14) {
            throw std::invalid_argument("p must be in [4, 14]");
        }
    }

    // value: 要加入 HLL 的原始字符串。
    // 目标：sparse 状态更新 entries_；dense 状态交给 dense_data_。
    // sparse 变得不划算时需要转换成 dense。
    void add(const std::string& value) {
        // TODO: 计算桶号和 rho，根据当前表示更新数据，并检查是否需要 promote。
        throw std::logic_error("TODO: SparseHLL::add");
    }

    // 返回值：当前基数估计值。
    // 目标：sparse 状态使用 entries_ 和空桶数计算；dense 状态复用 dense_data_。
    double estimate() {
        // TODO: 根据当前表示选择计算方式。
        throw std::logic_error("TODO: SparseHLL::estimate");
    }

    // other: 要合并进当前对象的另一个 SparseHLL。
    // 目标：正确处理 sparse+sparse、sparse+dense、dense+sparse、dense+dense。
    void merge(const SparseHLL& other) {
        // TODO: 根据两个对象当前的表示选择合并方式。
        throw std::logic_error("TODO: SparseHLL::merge");
    }

    // 目标：把 entries_ 中的所有非零寄存器写入 dense_data_，再切换表示。
    // 转换前后每个逻辑寄存器的值必须相同。
    void promote() {
        // TODO: 完整复制 sparse 状态，再设置 is_dense_。
        throw std::logic_error("TODO: SparseHLL::promote");
    }

    // 返回值：项目规定格式的完整字节数组。
    // 目标：sparse 时写稀疏格式；dense 时复用 DenseHLL 格式。
    std::vector<uint8_t> dump() const {
        // TODO: 根据当前表示选择编码方式。
        throw std::logic_error("TODO: SparseHLL::dump");
    }

    // buf: dump() 生成的完整字节数组。
    // 返回值：从 buf 恢复得到的 SparseHLL。
    // 目标：根据头部中的 encoding 恢复 sparse 或 dense 状态，并检查非法输入。
    static SparseHLL load(const std::vector<uint8_t>& buf) {
        // TODO: 解析头部，再按对应格式恢复对象。
        throw std::logic_error("TODO: SparseHLL::load");
    }

    size_t memBytes() const {
        return kHeaderSize + (is_dense_ ? denseBytes() : sparseBytes());
    }

    bool isDense() const {
        return is_dense_;
    }

    uint64_t m() const {
        return m_;
    }
};
