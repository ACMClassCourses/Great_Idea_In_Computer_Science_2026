#include "simulator.h"

#include <vector>

namespace memory_sim {

SimulationResult simulate_clock(int capacity, const std::vector<int>& pages) {
    validate_input(capacity, pages);

    SimulationResult result("CLOCK");
    const std::size_t slot_count = static_cast<std::size_t>(capacity);
    std::vector<int> slots(slot_count, -1);
    std::vector<int> reference_bits(slot_count, 0);
    std::size_t occupied = 0;
    std::size_t hand = 0;

    for (const int page : pages) {
        StepResult step;
        step.page = page;
        step.has_clock_state = true;
        step.clock_hand = hand;

        // TODO 1: 判断 page 是否命中，并按规则更新访问位。
        // TODO 2: 处理空位或从 hand 开始扫描，完成淘汰和装入。
        // TODO 3: 保存缓存、访问位、指针和本步结果。
        step.cache.assign(slots.begin(), slots.begin() + occupied);
        step.reference_bits.assign(reference_bits.begin(),
                                   reference_bits.begin() + occupied);

        result.steps.push_back(step);
    }

    result.total_accesses = pages.size();
    return result;
}

}  // namespace memory_sim
