#include "simulator.h"

#include <vector>

namespace memory_sim {

SimulationResult simulate_fifo(int capacity, const std::vector<int>& pages) {
    validate_input(capacity, pages);

    SimulationResult result("FIFO");
    std::vector<int> cache;
    cache.reserve(static_cast<std::size_t>(capacity));

    // TODO: adapt your completed Basic FIFO implementation to this interface.
    //       Update hit/miss counts and save every StepResult in result.steps.

    result.total_accesses = pages.size();
    return result;
}

}  // namespace memory_sim
