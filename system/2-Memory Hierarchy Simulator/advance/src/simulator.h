#ifndef MEMORY_HIERARCHY_SIMULATOR_H
#define MEMORY_HIERARCHY_SIMULATOR_H

#include <cstddef>
#include <string>
#include <vector>

namespace memory_sim {

struct StepResult {
    int page;                         // 本次访问的页面
    bool hit;                         // 是否命中
    bool eviction_happened;           // 是否发生了淘汰
    int evicted_page;                 // 被淘汰的页面
    std::vector<int> cache;           // 访问后的缓存
    std::vector<int> reference_bits;  // CLOCK 的访问位
    bool has_clock_state;             // 是否包含 CLOCK 状态
    std::size_t clock_hand;           // CLOCK 指针位置

    StepResult();
};

struct SimulationResult {
    std::string algorithm;            // 算法名称
    std::vector<StepResult> steps;    // 每次访问的结果
    std::size_t total_accesses;       // 总访问次数
    std::size_t hits;                 // 命中次数
    std::size_t misses;               // 未命中/缺页次数

    explicit SimulationResult(const std::string& algorithm_name);
    double hit_rate() const;
};

void validate_input(int capacity, const std::vector<int>& pages);

SimulationResult simulate_fifo(int capacity, const std::vector<int>& pages);
SimulationResult simulate_lru(int capacity, const std::vector<int>& pages);
SimulationResult simulate_clock(int capacity, const std::vector<int>& pages);

}  // namespace memory_sim

#endif
