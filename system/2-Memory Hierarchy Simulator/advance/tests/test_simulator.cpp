#include "simulator.h"

#include <cmath>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

int failures = 0;

void expect(bool condition, const std::string& message) {
    if (!condition) {
        ++failures;
        std::cerr << "[FAIL] " << message << '\n';
    }
}

void expect_counts(const memory_sim::SimulationResult& result,
                   std::size_t total,
                   std::size_t hits,
                   std::size_t misses,
                   const std::string& context) {
    expect(result.total_accesses == total, context + ": total_accesses");
    expect(result.hits == hits, context + ": hits");
    expect(result.misses == misses, context + ": misses");
    expect(result.hits + result.misses == result.total_accesses,
           context + ": hits + misses must equal total");
}

void expect_invalid_argument(const std::function<void()>& action,
                             const std::string& context) {
    try {
        action();
        expect(false, context + ": expected std::invalid_argument");
    } catch (const std::invalid_argument&) {
        // Expected.
    } catch (...) {
        expect(false, context + ": wrong exception type");
    }
}

void test_readme_example() {
    const std::vector<int> pages{1, 2, 3, 1, 4, 2, 5};
    const auto fifo = memory_sim::simulate_fifo(3, pages);
    const auto lru = memory_sim::simulate_lru(3, pages);
    const auto clock = memory_sim::simulate_clock(3, pages);

    expect_counts(fifo, 7, 2, 5, "README FIFO");
    expect_counts(lru, 7, 1, 6, "README LRU");
    expect_counts(clock, 7, 2, 5, "README CLOCK");

    expect(fifo.steps[4].eviction_happened && fifo.steps[4].evicted_page == 1,
           "FIFO should evict page 1 for page 4");
    expect(fifo.steps[4].cache == std::vector<int>({2, 3, 4}),
           "FIFO state after loading page 4");

    expect(lru.steps[3].cache == std::vector<int>({2, 3, 1}),
           "LRU hit should move page 1 to most-recent position");
    expect(lru.steps[4].eviction_happened && lru.steps[4].evicted_page == 2,
           "LRU should evict page 2 for page 4");
    expect(lru.steps.back().cache == std::vector<int>({4, 2, 5}),
           "LRU final state");

    expect(clock.steps[2].clock_hand == 0, "CLOCK hand should wrap after filling");
    expect(clock.steps[3].clock_hand == 0, "CLOCK hand must not move on hit");
    expect(clock.steps[4].eviction_happened && clock.steps[4].evicted_page == 1,
           "CLOCK should evict page 1 for page 4");
    expect(clock.steps[4].cache == std::vector<int>({4, 2, 3}),
           "CLOCK state after loading page 4");
    expect(clock.steps[4].reference_bits == std::vector<int>({1, 0, 0}),
           "CLOCK reference bits after its first replacement");
    expect(clock.steps[4].clock_hand == 1,
           "CLOCK hand after its first replacement");
    expect(clock.steps.back().cache == std::vector<int>({4, 2, 5}),
           "CLOCK final cache slots");
    expect(clock.steps.back().reference_bits == std::vector<int>({1, 0, 1}),
           "CLOCK final reference bits");
    expect(clock.steps.back().clock_hand == 0, "CLOCK final hand position");
}

void test_empty_sequence() {
    const std::vector<int> pages;
    const std::vector<memory_sim::SimulationResult> results{
        memory_sim::simulate_fifo(3, pages),
        memory_sim::simulate_lru(3, pages),
        memory_sim::simulate_clock(3, pages),
    };

    for (const auto& result : results) {
        expect_counts(result, 0, 0, 0, result.algorithm + " empty sequence");
        expect(result.steps.empty(), result.algorithm + " empty sequence has no steps");
        expect(result.hit_rate() == 0.0,
               result.algorithm + " empty sequence safely returns zero hit rate");
    }
}

void test_capacity_one_and_repeated_page() {
    const std::vector<int> pages{4, 4, 5};
    const std::vector<memory_sim::SimulationResult> results{
        memory_sim::simulate_fifo(1, pages),
        memory_sim::simulate_lru(1, pages),
        memory_sim::simulate_clock(1, pages),
    };

    for (const auto& result : results) {
        expect_counts(result, 3, 1, 2, result.algorithm + " capacity one");
        expect(!result.steps[1].eviction_happened,
               result.algorithm + " repeated page should not evict");
        expect(result.steps[2].eviction_happened && result.steps[2].evicted_page == 4,
               result.algorithm + " should evict page 4 for page 5");
        expect(result.steps[2].cache == std::vector<int>({5}),
               result.algorithm + " final cache with capacity one");
    }
}

void test_all_pages_fit() {
    const std::vector<int> pages{0, 1, 2, 0, 1, 2};
    const std::vector<memory_sim::SimulationResult> results{
        memory_sim::simulate_fifo(3, pages),
        memory_sim::simulate_lru(3, pages),
        memory_sim::simulate_clock(3, pages),
    };

    for (const auto& result : results) {
        expect_counts(result, 6, 3, 3, result.algorithm + " all pages fit");
        for (const auto& step : result.steps) {
            expect(!step.eviction_happened,
                   result.algorithm + " should not evict when all pages fit");
        }
        expect(std::abs(result.hit_rate() - 0.5) < 1e-12,
               result.algorithm + " hit rate should be 0.5");
    }
}

void test_cycle_exceeding_capacity() {
    const std::vector<int> pages{1, 2, 3, 1, 2, 3};
    expect_counts(memory_sim::simulate_fifo(2, pages), 6, 0, 6,
                  "FIFO cycle exceeding capacity");
    expect_counts(memory_sim::simulate_lru(2, pages), 6, 0, 6,
                  "LRU cycle exceeding capacity");
    expect_counts(memory_sim::simulate_clock(2, pages), 6, 0, 6,
                  "CLOCK cycle exceeding capacity");
}

void test_belady_anomaly() {
    const std::vector<int> pages{1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5};
    const auto capacity_three = memory_sim::simulate_fifo(3, pages);
    const auto capacity_four = memory_sim::simulate_fifo(4, pages);

    expect_counts(capacity_three, 12, 3, 9, "Belady capacity 3");
    expect_counts(capacity_four, 12, 2, 10, "Belady capacity 4");
    expect(capacity_four.misses > capacity_three.misses,
           "Belady sequence should have more misses with capacity 4");
}

void test_invalid_input() {
    expect_invalid_argument(
        [] { static_cast<void>(memory_sim::simulate_fifo(0, {1})); },
        "FIFO zero capacity");
    expect_invalid_argument(
        [] { static_cast<void>(memory_sim::simulate_lru(-1, {1})); },
        "LRU negative capacity");
    expect_invalid_argument(
        [] { static_cast<void>(memory_sim::simulate_clock(2, {1, -2})); },
        "CLOCK negative page");
}

}  // namespace

int main() {
    test_readme_example();
    test_empty_sequence();
    test_capacity_one_and_repeated_page();
    test_all_pages_fit();
    test_cycle_exceeding_capacity();
    test_belady_anomaly();
    test_invalid_input();

    if (failures != 0) {
        std::cerr << failures << " test assertion(s) failed.\n";
        return 1;
    }

    std::cout << "All simulator tests passed.\n";
    return 0;
}
