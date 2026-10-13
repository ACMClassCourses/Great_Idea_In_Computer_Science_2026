#include "simulator.h"

#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

struct ProgramInput {
    int capacity;
    std::vector<int> pages;
};

ProgramInput read_input() {
    long long capacity = 0;
    long long access_count = 0;
    if (!(std::cin >> capacity >> access_count)) {
        throw std::invalid_argument("第一行应包含缓存容量 c 和访问次数 n");
    }
    if (capacity < 1 || capacity > 100 || access_count < 1 || access_count > 100) {
        throw std::invalid_argument("c 和 n 必须在 1 到 100 之间");
    }

    ProgramInput input;
    input.capacity = static_cast<int>(capacity);
    input.pages.reserve(static_cast<std::size_t>(access_count));
    for (long long index = 0; index < access_count; ++index) {
        long long page = 0;
        if (!(std::cin >> page)) {
            throw std::invalid_argument("页面编号数量少于 n");
        }
        if (page < 0 || page > std::numeric_limits<int>::max()) {
            throw std::invalid_argument("页面编号必须是 int 范围内的非负整数");
        }
        input.pages.push_back(static_cast<int>(page));
    }

    std::string extra;
    if (std::cin >> extra) {
        throw std::invalid_argument("页面编号数量多于 n");
    }
    return input;
}

void print_vector(const std::vector<int>& values) {
    std::cout << '[';
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 0) {
            std::cout << ", ";
        }
        std::cout << values[index];
    }
    std::cout << ']';
}

void print_result(const memory_sim::SimulationResult& result) {
    std::cout << "\n=== " << result.algorithm << " ===\n";
    if (result.steps.empty()) {
        std::cout << "访问序列为空。\n";
    }

    for (std::size_t index = 0; index < result.steps.size(); ++index) {
        const memory_sim::StepResult& step = result.steps[index];
        std::cout << "第 " << index + 1 << " 步 | 访问 " << step.page << " | "
                  << (step.hit ? "命中" : "未命中") << " | 淘汰: ";
        if (step.eviction_happened) {
            std::cout << step.evicted_page;
        } else {
            std::cout << "无";
        }
        std::cout << " | 缓存: ";
        print_vector(step.cache);

        if (step.has_clock_state) {
            std::cout << " | 访问位: ";
            print_vector(step.reference_bits);
            std::cout << " | 指针: " << step.clock_hand;
        }
        std::cout << '\n';
    }

    // TODO 1: 输出总访问、命中、未命中次数和命中率。
    // 空访问序列的命中率应显示“—”，不能发生除零。
}

void print_comparison(const std::vector<memory_sim::SimulationResult>& results) {
    // TODO 2: 输出 FIFO、LRU、CLOCK 的汇总对比表。
    (void)results;
}

}  // namespace

int main() {
    try {
        const ProgramInput input = read_input();
        memory_sim::validate_input(input.capacity, input.pages);

        std::vector<memory_sim::SimulationResult> results;
        results.push_back(memory_sim::simulate_fifo(input.capacity, input.pages));
        results.push_back(memory_sim::simulate_lru(input.capacity, input.pages));
        results.push_back(memory_sim::simulate_clock(input.capacity, input.pages));

        for (std::size_t index = 0; index < results.size(); ++index) {
            print_result(results[index]);
        }
        print_comparison(results);
    } catch (const std::exception& error) {
        std::cerr << "输入错误: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
