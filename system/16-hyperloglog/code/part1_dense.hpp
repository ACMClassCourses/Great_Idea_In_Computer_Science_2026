#pragma once

#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>
#include "hash.hpp"

constexpr size_t kHeaderSize = 16;

class DenseHLL {
    int p_;
    uint64_t m_;
    std::vector<uint8_t> data_;
    bool cache_valid_;
    double cached_estimate_;

    size_t payloadBytes() const {
        return m_ * 6 / 8;
    }

public:
    explicit DenseHLL(int p = 12)
        : p_(p),
          m_(1ULL << p),
          data_(m_ * 6 / 8 + 1, 0),
          cache_valid_(false),
          cached_estimate_(0.0) {
        if (p < 4 || p > 14) {
            throw std::invalid_argument("p must be in [4, 14]");
        }
    }

    // i: 要读取的寄存器下标，范围是 [0, m_)。
    // 返回值：第 i 个 6 位寄存器的值。
    uint8_t get(size_t i) const {
        // TODO: 根据 i 找到对应字节和位偏移，再取出 6 位。
        throw std::logic_error("TODO: DenseHLL::get");
    }

    // i: 要写入的寄存器下标。
    // value: 新的寄存器值，只允许使用 6 位。
    // 目标：只修改第 i 个寄存器，不能破坏相邻寄存器，并让缓存失效。
    void set(size_t i, uint8_t value) {
        // TODO: 找到对应位置，清掉旧 6 位，写入新值，再让缓存失效。
        throw std::logic_error("TODO: DenseHLL::set");
    }

    // value: 要加入 HLL 的原始字符串。
    // 目标：逻辑与 HLL0::add 相同，但寄存器必须通过 get/set 访问。
    void add(const std::string& value) {
        // TODO: 计算桶号和 rho，并在需要时调用 set。
        throw std::logic_error("TODO: DenseHLL::add");
    }

    // 返回值：当前基数估计值。
    // 目标：缓存有效时直接返回；否则重新计算并保存缓存。
    double estimate() {
        // TODO: 读取所有寄存器并计算估计值。
        throw std::logic_error("TODO: DenseHLL::estimate");
    }

    // 标记当前估计缓存无效。
    void invalidate() {
        cache_valid_ = false;
    }

    // other: 要合并进当前对象的另一个 DenseHLL。
    // 目标：p 必须相同；每个寄存器取最大值。
    void merge(const DenseHLL& other) {
        // TODO: 逐个读取两个对象的寄存器，必要时更新当前对象。
        throw std::logic_error("TODO: DenseHLL::merge");
    }

    // 返回值：项目规定格式的完整字节数组。
    // 目标：写入 16 字节头，再写入 dense 正文。
    std::vector<uint8_t> dump() const {
        // TODO: 按任务文档规定的格式序列化。
        throw std::logic_error("TODO: DenseHLL::dump");
    }

    // buf: dump() 生成的完整字节数组。
    // 返回值：从 buf 恢复得到的 DenseHLL。
    // 目标：先检查长度、标记和参数，再恢复正文。
    static DenseHLL load(const std::vector<uint8_t>& buf) {
        // TODO: 检查并解析头部，创建对象，再复制正文。
        throw std::logic_error("TODO: DenseHLL::load");
    }

    uint64_t m() const {
        return m_;
    }
};
