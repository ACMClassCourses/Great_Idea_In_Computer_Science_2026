#include <iostream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

struct LossRule {
    std::string type;
    int id = 0;
    int attempt = 0;
};

struct Simulation {
    std::vector<std::string> messages;
    int rto = 4;
    int max_tick = 100;
    std::vector<LossRule> losses;
};

struct Result {
    bool success = false;
    int finish_tick = -1;
    std::vector<std::string> delivered;
    int data_sends = 0;
    int retransmissions = 0;
    int ack_sends = 0;
    int dropped = 0;
};

// TODO: 实现停止等待协议。建议自行定义 Event、发送方和接收方状态。
// 每个时刻必须先处理按加入顺序排列的到达事件，再检查超时。
Result simulate(const Simulation& simulation) {
    (void)simulation;
    throw std::logic_error("TODO: implement simulate");
}

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int test_count = 0;
    if (!(std::cin >> test_count) || test_count < 0) return 0;

    try {
        while (test_count-- > 0) {
            int message_count = 0;
            int loss_count = 0;
            Simulation simulation;
            std::cin >> message_count >> simulation.rto >> simulation.max_tick >> loss_count;
            if (!std::cin || message_count < 0 || simulation.rto <= 0 ||
                simulation.max_tick < 0 || loss_count < 0) {
                return 0;
            }

            simulation.messages.resize(message_count);
            for (std::string& message : simulation.messages) std::cin >> message;
            simulation.losses.resize(loss_count);
            for (LossRule& rule : simulation.losses) {
                std::cin >> rule.type >> rule.id >> rule.attempt;
            }

            const Result result = simulate(simulation);
            std::cout << "RESULT " << (result.success ? "SUCCESS" : "INCOMPLETE") << ' '
                      << result.finish_tick << ' ' << result.delivered.size() << ' '
                      << result.data_sends << ' ' << result.retransmissions << ' '
                      << result.ack_sends << ' ' << result.dropped;
            for (const std::string& message : result.delivered) std::cout << ' ' << message;
            std::cout << '\n';
        }
    } catch (const std::exception& error) {
        std::cerr << "Simulation error: " << error.what() << '\n';
        return 1;
    }
}
