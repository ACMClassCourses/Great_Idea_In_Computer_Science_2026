#include "simulator.h"

#include <vector>

namespace memory_sim {

SimulationResult simulate_lru(int capacity, const std::vector<int>& pages) {
    validate_input(capacity, pages);

    SimulationResult result("LRU");
    // 缓存从左到右表示“最久未使用”到“最近使用”。
    std::vector<int> cache;
    cache.reserve(static_cast<std::size_t>(capacity));

    for (const int page : pages) {
        StepResult step;
        step.page = page;

        // TODO 1: 查找 page，命中后将它更新为最近使用的页面。
        // TODO 2: 未命中时更新统计；缓存已满时淘汰最久未使用的页面。
        // TODO 3: 保存访问后的完整缓存状态和本步结果。

        result.steps.push_back(step);
    }

    result.total_accesses = pages.size();
    return result;
}

}  // namespace memory_sim
