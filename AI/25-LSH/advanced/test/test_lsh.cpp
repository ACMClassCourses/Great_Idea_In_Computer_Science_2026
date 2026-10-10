// ============================================================================
//  test_lsh.cpp —— LSH 测试用例
// ============================================================================
//
//  编译运行：
//    g++ -std=c++17 -O2 -Isrc src/mnist.cpp src/lsh.cpp test/test_lsh.cpp -o test/test_lsh
//    ./test/test_lsh ../test/data
//
//  如果你用 solution/lsh_complete.cpp 替代 lsh.cpp：
//    g++ -std=c++17 -O2 -Isrc src/mnist.cpp solution/lsh_complete.cpp test/test_lsh.cpp -o test/test_lsh
//    ./test/test_lsh ../test/data
//
// ============================================================================

#include "lsh.h"
#include "mnist.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

// 简单的断言宏：条件不满足就抛异常
void require(bool cond, const std::string& msg) {
    if (!cond) throw std::runtime_error(msg);
}

// 暴力搜索：遍历所有点找最近邻（作为标准答案）
int brute_force_nn(const std::vector<std::int16_t>& points,
                   int count, int dimension,
                   const std::int16_t* query) {
    int best_id = -1;
    std::int64_t best_dist = std::numeric_limits<std::int64_t>::max();
    for (int id = 0; id < count; ++id) {
        std::int64_t dist = 0;
        for (int d = 0; d < dimension; ++d) {
            std::int64_t diff = std::int64_t(query[d]) -
                points[std::size_t(id) * dimension + d];
            dist += diff * diff;
        }
        if (dist < best_dist) {
            best_dist = dist;
            best_id = id;
        }
    }
    return best_id;
}

// ──────────────────────────────────────────────────────────────────────────
//  测试 1：自查询（查训练集里的图片，应该找到自己）
// ──────────────────────────────────────────────────────────────────────────
void test_self_query() {
    std::cout << "测试 1：自查询...\n";
    // 10 个 2 维点
    const std::vector<std::int16_t> points = {
        100, 0,  95, 10,  80, 30,   0, 100, -100, 0,
          0, -100, -80, 30,  60, -20, 120, 5,  -20, 110};
    LshIndex index({12, 8, 4, 7});  // L=12, K=8, min=4, seed=7
    index.build(points, 10, 2);

    // 查每个训练点，结果应该是自己（距离=0）
    for (int id = 0; id < 10; ++id) {
        LshResult r = index.query(points.data() + id * 2);
        require(r.index == id, "自查询：没找到自己");
        require(r.squared_distance == 0, "自查询：距离不为 0");
    }

    // 查一个近邻点，应该找到最近的
    const std::int16_t query[] = {97, 8};
    int exact = brute_force_nn(points, 10, 2, query);
    LshResult r = index.query(query);
    require(r.index == exact, "自查询：最近邻不正确");
    require(r.candidate_count < 10, "自查询：候选没减少");

    std::cout << "  [通过] 10 个 2 维点，自查询和近邻查询都正确\n\n";
}

// ──────────────────────────────────────────────────────────────────────────
//  测试 2：大规模 2 维点集（检查召回率和筛选效果）
// ──────────────────────────────────────────────────────────────────────────
void test_large_2d() {
    std::cout << "测试 2：大规模 2 维点集...\n";
    constexpr int count = 30000;
    constexpr int query_count = 1000;

    // 生成 3 万个随机 2 维点（极坐标随机）
    std::vector<std::int16_t> points(std::size_t(count) * 2);
    std::mt19937 rng(123);
    std::uniform_real_distribution<double> angle(0.0, 6.283185307179586);
    std::uniform_int_distribution<int> radius(1000, 28000);

    for (int i = 0; i < count; ++i) {
        double a = angle(rng);
        int r = radius(rng);
        points[std::size_t(i) * 2] =
            static_cast<std::int16_t>(std::lround(r * std::cos(a)));
        points[std::size_t(i) * 2 + 1] =
            static_cast<std::int16_t>(std::lround(r * std::sin(a)));
    }

    LshIndex index({16, 12, 20, 42});
    index.build(points, count, 2);

    // 查 1000 个带噪声的近邻点
    int exact_matches = 0;
    long long total_candidates = 0;
    std::uniform_int_distribution<int> select(0, count - 1);
    std::uniform_int_distribution<int> noise(-3, 3);

    for (int i = 0; i < query_count; ++i) {
        int src = select(rng);
        std::int16_t query[] = {
            static_cast<std::int16_t>(points[std::size_t(src) * 2] + noise(rng)),
            static_cast<std::int16_t>(points[std::size_t(src) * 2 + 1] + noise(rng))};
        int exact = brute_force_nn(points, count, 2, query);
        LshResult r = index.query(query);
        exact_matches += (r.index == exact);
        total_candidates += r.candidate_count;
    }

    double recall = double(exact_matches) / query_count;
    double avg_candidates = double(total_candidates) / query_count;

    require(recall >= 0.98, "召回率太低（<98%）");
    require(avg_candidates < count * 0.25, "候选集太大（筛选效果差）");

    std::cout << "  [通过] 3 万点召回率=" << recall * 100
              << "%，平均候选=" << avg_candidates << "\n\n";
}

// ──────────────────────────────────────────────────────────────────────────
//  测试 3：MNIST 数据集（检查准确率和候选数）
// ──────────────────────────────────────────────────────────────────────────
void test_mnist(const std::string& data_dir) {
    std::cout << "测试 3：MNIST 数据集...\n";
    const MnistDataset train = load_mnist(
        data_dir + "/train-images.idx3-ubyte",
        data_dir + "/train-labels.idx1-ubyte");
    const MnistDataset test = load_mnist(
        data_dir + "/t10k-images.idx3-ubyte",
        data_dir + "/t10k-labels.idx1-ubyte");

    require(train.count == 60000 && test.count == 10000,
            "MNIST 数量不对");
    require(train.rows == 28 && train.cols == 28 &&
            test.rows == 28 && test.cols == 28,
            "MNIST 图片尺寸不对");

    const int dimension = train.rows * train.cols;
    LshIndex index({16, 12, 20, 42});
    index.build(train.images, train.count, dimension);

    int correct = 0;
    int missing = 0;
    long long total_candidates = 0;
    for (int i = 0; i < test.count; ++i) {
        LshResult r = index.query(
            test.images.data() + std::size_t(i) * dimension);
        if (r.index < 0) { ++missing; continue; }
        correct += (train.labels[r.index] == test.labels[i]);
        total_candidates += r.candidate_count;
    }

    double accuracy = double(correct) / test.count;
    double avg_candidates = double(total_candidates) / test.count;

    require(missing == 0, "有测试图片没找到候选");
    require(accuracy >= 0.90, "MNIST 准确率低于 90%");
    require(avg_candidates < train.count * 0.50,
            "MNIST 候选集太大");

    std::cout << "  [通过] 准确率=" << accuracy * 100
              << "%，平均候选=" << avg_candidates << "\n\n";
}

// ──────────────────────────────────────────────────────────────────────────
//  测试 4：k-NN 查询（检查返回的 k 个结果是否正确排序）
//  注意：这个测试需要 query_knn 已实现
// ──────────────────────────────────────────────────────────────────────────
void test_knn() {
    std::cout << "测试 4：k-NN 查询...\n";
    const std::vector<std::int16_t> points = {
        100, 0,  95, 10,  80, 30,   0, 100, -100, 0,
          0, -100, -80, 30,  60, -20, 120, 5,  -20, 110};
    LshIndex index({12, 8, 4, 7});
    index.build(points, 10, 2);

    const std::int16_t query[] = {97, 8};
    const int k = 3;

    try {
        KnnResult knn = index.query_knn(query, k);

        // 返回空结果 = 还没实现，跳过
        if (knn.indices.empty()) {
            std::cout << "  [跳过] query_knn 还没实现（返回了空结果）\n";
            std::cout << "  （完成挑战任务 1 后此测试才会通过）\n\n";
            return;
        }

        require(int(knn.indices.size()) <= k, "k-NN 返回数量超过 k");

        // 距离应该是递增的
        for (std::size_t i = 1; i < knn.distances.size(); ++i) {
            require(knn.distances[i] >= knn.distances[i - 1],
                    "k-NN 距离没有递增排序");
        }

        // 第一个应该跟暴力搜索结果一致
        int exact = brute_force_nn(points, 10, 2, query);
        require(knn.indices[0] == exact, "k-NN 第一个不是最近邻");

        std::cout << "  [通过] k=" << k << "，返回 "
                  << knn.indices.size() << " 个结果，距离递增\n\n";
    } catch (const std::logic_error&) {
        std::cout << "  [跳过] query_knn 还没实现\n";
        std::cout << "  （完成挑战任务 1 后此测试才会通过）\n\n";
    }
}

}  // namespace

int main(int argc, char** argv) {
    try {
        std::string data_dir = (argc > 1) ? argv[1] : "../test/data";

        test_self_query();
        test_large_2d();
        test_mnist(data_dir);
        test_knn();

        std::cout << "========================================\n";
        std::cout << "所有测试通过！\n";
        std::cout << "========================================\n";
    } catch (const std::exception& e) {
        std::cerr << "\n[失败] " << e.what() << '\n';
        return 1;
    }
    return 0;
}
