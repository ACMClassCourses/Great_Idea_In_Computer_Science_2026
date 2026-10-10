#include "lsh.h"
#include "mnist.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

void require(bool condition, const std::string& message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

int brute_force(const std::vector<std::int16_t>& points,
                int count,
                int dimension,
                const std::int16_t* query) {
    int best_id = -1;
    std::int64_t best_distance = std::numeric_limits<std::int64_t>::max();
    for (int id = 0; id < count; ++id) {
        std::int64_t distance = 0;
        for (int d = 0; d < dimension; ++d) {
            const std::int64_t difference =
                static_cast<std::int64_t>(query[d]) -
                points[static_cast<std::size_t>(id) * dimension + d];
            distance += difference * difference;
        }
        if (distance < best_distance) {
            best_distance = distance;
            best_id = id;
        }
    }
    return best_id;
}

void test_small_2d() {
    const std::vector<std::int16_t> points = {
        100, 0, 95, 10, 80, 30, 0, 100, -100, 0,
        0, -100, -80, 30, 60, -20, 120, 5, -20, 110};
    LshIndex index({12, 8, 4, 7});
    index.build(points, 10, 2);

    for (int id = 0; id < 10; ++id) {
        const LshResult result = index.query(points.data() + id * 2);
        require(result.index == id, "small 2D self-query failed");
        require(result.squared_distance == 0, "small 2D distance is not zero");
    }

    const std::int16_t query[] = {97, 8};
    const int exact = brute_force(points, 10, 2, query);
    const LshResult result = index.query(query);
    require(result.index == exact, "small 2D nearest-neighbor query failed");
    require(result.candidate_count < 10, "small 2D query did not filter points");
    std::cout << "[PASS] small 2D point set\n";
}

void test_large_2d() {
    constexpr int count = 30000;
    constexpr int query_count = 1000;
    std::vector<std::int16_t> points(static_cast<std::size_t>(count) * 2);
    std::mt19937 random(123);
    std::uniform_real_distribution<double> angle(0.0, 6.283185307179586);
    std::uniform_int_distribution<int> radius(1000, 28000);

    for (int i = 0; i < count; ++i) {
        const double a = angle(random);
        const int r = radius(random);
        points[static_cast<std::size_t>(i) * 2] =
            static_cast<std::int16_t>(std::lround(r * std::cos(a)));
        points[static_cast<std::size_t>(i) * 2 + 1] =
            static_cast<std::int16_t>(std::lround(r * std::sin(a)));
    }

    LshIndex index({16, 12, 20, 42});
    index.build(points, count, 2);

    int exact_matches = 0;
    long long total_candidates = 0;
    std::uniform_int_distribution<int> select(0, count - 1);
    std::uniform_int_distribution<int> noise(-3, 3);
    for (int i = 0; i < query_count; ++i) {
        const int source = select(random);
        const std::int16_t query[] = {
            static_cast<std::int16_t>(points[source * 2] + noise(random)),
            static_cast<std::int16_t>(points[source * 2 + 1] + noise(random))};
        const int exact = brute_force(points, count, 2, query);
        const LshResult result = index.query(query);
        exact_matches += result.index == exact;
        total_candidates += result.candidate_count;
    }

    const double recall = static_cast<double>(exact_matches) / query_count;
    const double average_candidates =
        static_cast<double>(total_candidates) / query_count;
    require(recall >= 0.98, "large 2D exact-neighbor recall is too low");
    require(average_candidates < count * 0.25,
            "large 2D candidate set is too large");
    std::cout << "[PASS] large 2D point set: recall=" << recall * 100.0
              << "%, average candidates=" << average_candidates << '\n';
}

void test_mnist(const std::filesystem::path& data_directory) {
    const MnistDataset train = load_mnist(
        (data_directory / "train-images.idx3-ubyte").string(),
        (data_directory / "train-labels.idx1-ubyte").string());
    const MnistDataset test = load_mnist(
        (data_directory / "t10k-images.idx3-ubyte").string(),
        (data_directory / "t10k-labels.idx1-ubyte").string());

    require(train.count == 60000 && test.count == 10000,
            "unexpected MNIST item count");
    require(train.rows == 28 && train.cols == 28 &&
                test.rows == 28 && test.cols == 28,
            "unexpected MNIST dimensions");

    const int dimension = train.rows * train.cols;
    LshIndex index({16, 12, 20, 42});
    index.build(train.images, train.count, dimension);

    int correct = 0;
    int missing = 0;
    long long total_candidates = 0;
    for (int i = 0; i < test.count; ++i) {
        const LshResult result = index.query(
            test.images.data() + static_cast<std::size_t>(i) * dimension);
        if (result.index < 0) {
            ++missing;
            continue;
        }
        correct += train.labels[result.index] == test.labels[i];
        total_candidates += result.candidate_count;
    }

    const double accuracy = static_cast<double>(correct) / test.count;
    const double average_candidates =
        static_cast<double>(total_candidates) / test.count;
    require(missing == 0, "MNIST query returned no candidate");
    require(accuracy >= 0.90, "MNIST accuracy is below 90%");
    require(average_candidates < train.count * 0.50,
            "MNIST candidate set is too large");
    std::cout << "[PASS] MNIST: accuracy=" << accuracy * 100.0
              << "%, average candidates=" << average_candidates << '\n';
}

}  // namespace

int main(int argc, char** argv) {
    try {
        test_small_2d();
        test_large_2d();
        test_mnist(argc > 1 ? argv[1] : std::filesystem::path("test/data"));
        std::cout << "All tests passed.\n";
    } catch (const std::exception& error) {
        std::cerr << "[FAIL] " << error.what() << '\n';
        return 1;
    }
    return 0;
}
