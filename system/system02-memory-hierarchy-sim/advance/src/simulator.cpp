#include "simulator.h"

#include <stdexcept>

namespace memory_sim {

StepResult::StepResult()
    : page(0),
      hit(false),
      eviction_happened(false),
      evicted_page(0),
      has_clock_state(false),
      clock_hand(0) {}

SimulationResult::SimulationResult(const std::string& algorithm_name)
    : algorithm(algorithm_name), total_accesses(0), hits(0), misses(0) {}

double SimulationResult::hit_rate() const {
    if (total_accesses == 0) {
        return 0.0;
    }
    return static_cast<double>(hits) / static_cast<double>(total_accesses);
}

void validate_input(int capacity, const std::vector<int>& pages) {
    if (capacity <= 0) {
        throw std::invalid_argument("缓存容量必须是正整数");
    }
    for (const int page : pages) {
        if (page < 0) {
            throw std::invalid_argument("页面编号必须是非负整数");
        }
    }
}

}  // namespace memory_sim
