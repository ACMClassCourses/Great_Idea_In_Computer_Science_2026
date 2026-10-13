// Copy this file to main.cpp. Input and the fixed sampler are supplied;
// implement contribution bounding, NAIVE, and ALERT where marked.
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <random>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

double openUnit(std::mt19937_64& rng) {
    const long double denominator =
        static_cast<long double>(std::numeric_limits<std::uint64_t>::max()) + 1.0L;
    return static_cast<double>((static_cast<long double>(rng()) + 0.5L) / denominator);
}

double laplaceNoise(double scale, std::mt19937_64& rng) {
    if (scale == 0.0) return 0.0;
    const double u = openUnit(rng) - 0.5;
    const double magnitude = -scale * std::log1p(-2.0 * std::abs(u));
    return u < 0.0 ? -magnitude : magnitude;
}

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    std::size_t eventCount;
    std::uint64_t seed;
    if (!(std::cin >> eventCount >> seed)) return 0;

    // TODO 1: build topic -> distinct student set.
    std::unordered_map<int, std::unordered_set<std::uint64_t>> studentsByTopic;
    for (std::size_t i = 0; i < eventCount; ++i) {
        std::uint64_t student;
        int topic;
        std::cin >> student >> topic;
        // TODO
    }

    std::string mode;
    double threshold, epsilon;
    std::size_t maxHits;
    std::cin >> mode >> threshold >> maxHits >> epsilon;
    std::size_t queryCount;
    std::cin >> queryCount;
    std::vector<int> topics(queryCount);
    for (int& topic : topics) std::cin >> topic;

    // TODO 2: NAIVE -- split epsilon equally across all queries.
    // TODO 3: ALERT -- noisy threshold, noisy queries, refresh after a hit.
    // TODO 4: print BELOW/ALERT/FINISHED for every query position.
    return 0;
}
