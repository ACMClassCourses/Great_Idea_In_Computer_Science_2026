#include "lsh.h"
#include "mnist.h"

#include <algorithm>
#include <chrono>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

// ──────────────────────────────────────────────────────────────────────────
//  辅助函数：暴力搜索（用于跟 LSH 对比）
// ──────────────────────────────────────────────────────────────────────────
// 这个函数遍历全部训练图片找最近邻，是"正确答案"。
// LSH 应该跟它结果接近，但速度快得多。
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

// 把图片打印成 ASCII 艺术
void print_ascii(const std::int16_t* img, int rows, int cols) {
    for (int r = 0; r < rows; ++r) {
        for (int c = 0; c < cols; ++c) {
            int p = img[r * cols + c];
            std::cout << (p > 200 ? '@' : p > 128 ? '#' :
                          p >  64 ? '.' : ' ');
        }
        std::cout << '\n';
    }
}

// ──────────────────────────────────────────────────────────────────────────
//  主程序
// ──────────────────────────────────────────────────────────────────────────
int main(int argc, char** argv) {
    try {
        // ── 参数解析 ──
        // 基础用法：./lsh_advanced [数据目录]
        //
        // 挑战任务 3：支持更多命令行参数
        //   ./lsh_advanced [数据目录] [-L 表数] [-K 位数] [-k knn] [-seed 种子]
        //   提示：遍历 argv，遇到 -L 就读下一个参数当整数
        //         参考函数：std::stoi

        std::string data_dir = "../test/data";
        int knn_k = 1;            // 1 = 用 1-NN，>1 = 用 k-NN（需要实现 query_knn）
        bool show_details = true;  // 是否打印前几张的详情
        int test_limit = 0;       // 0 = 测全部，>0 = 只测前 N 张

        for (int i = 1; i < argc; ++i) {
            std::string arg = argv[i];
            if (arg == "-k" && i + 1 < argc) {
                knn_k = std::stoi(argv[++i]);
            } else if (arg == "-n" && i + 1 < argc) {
                test_limit = std::stoi(argv[++i]);
            } else if (arg == "--no-detail") {
                show_details = false;
            } else if (arg[0] != '-') {
                data_dir = arg;
            }
        }

        // ── 加载数据 ──
        std::cout << "读取 MNIST 数据集...\n";
        const MnistDataset train = load_mnist(
            data_dir + "/train-images.idx3-ubyte",
            data_dir + "/train-labels.idx1-ubyte");
        const MnistDataset test = load_mnist(
            data_dir + "/t10k-images.idx3-ubyte",
            data_dir + "/t10k-labels.idx1-ubyte");

        if (train.rows != test.rows || train.cols != test.cols) {
            throw std::runtime_error("训练集和测试集图片尺寸不一致");
        }

        const int dimension = train.rows * train.cols;
        std::cout << "训练集: " << train.count << " 张\n"
                  << "测试集: " << test.count << " 张\n"
                  << "图片尺寸: " << train.rows << " x " << train.cols
                  << "\n\n";

        // ── 展示一张测试图 ──
        if (show_details) {
            std::cout << "第一张测试图片（标签 = "
                      << int(test.labels[0]) << "）：\n";
            print_ascii(test.images.data(), train.rows, train.cols);
            std::cout << "\n";
        }

        // ── 建立 LSH 索引 ──
        LshConfig config;  // 默认: L=16, K=12
        std::cout << "建立 LSH 索引（L=" << config.table_count
                  << ", K=" << config.bits_per_table << "）...\n";
        LshIndex index(config);

        auto build_start = std::chrono::steady_clock::now();
        index.build(train.images, train.count, dimension);
        auto build_end = std::chrono::steady_clock::now();

        std::cout << "索引建立完成，耗时 "
                  << std::chrono::duration<double>(build_end - build_start).count()
                  << " 秒\n\n";

        // ── 查询测试集 ──
        int num_to_test = (test_limit > 0) ?
            std::min(test_limit, test.count) : test.count;

        int correct = 0;
        long long total_candidates = 0;

        // 挑战任务 2 相关：如果 knn_k > 1，需要 query_knn 已实现
        bool use_knn = (knn_k > 1);
        if (use_knn) {
            std::cout << "使用 k-NN 模式（k=" << knn_k << "）\n";
            std::cout << "注意：需要你实现 query_knn()，否则会出错\n\n";
        } else {
            std::cout << "使用 1-NN 模式\n\n";
        }

        std::cout << "开始识别 " << num_to_test << " 张测试图片...\n";
        auto query_start = std::chrono::steady_clock::now();

        for (int i = 0; i < num_to_test; ++i) {
            const std::int16_t* image =
                test.images.data() + std::size_t(i) * dimension;

            int predicted = -1;

            if (use_knn) {
                // ── 挑战任务 2：k-NN 多数投票 ──
                KnnResult knn = index.query_knn(image, knn_k);
                total_candidates += knn.candidate_count;

                // 多数投票：看 k 个近邻的标签哪个出现最多
                if (!knn.indices.empty()) {
                    int votes[10] = {};
                    for (int id : knn.indices) {
                        if (id >= 0 && id < train.count) {
                            votes[train.labels[id]]++;
                        }
                    }
                    int best_label = 0, best_votes = -1;
                    for (int l = 0; l < 10; ++l) {
                        if (votes[l] > best_votes) {
                            best_votes = votes[l];
                            best_label = l;
                        }
                    }
                    predicted = best_label;
                }
            } else {
                // 1-NN：直接取最近邻的标签
                LshResult result = index.query(image);
                total_candidates += result.candidate_count;
                if (result.index >= 0) {
                    predicted = train.labels[result.index];
                }
            }

            bool right = (predicted == int(test.labels[i]));
            if (right) ++correct;

            // 前 5 张打印详情
            if (show_details && i < 5) {
                std::cout << "  图 " << std::setw(5) << i
                          << "：真实=" << int(test.labels[i])
                          << "，预测=" << predicted
                          << (right ? " ✓" : " ✗") << "\n";
            }
        }

        auto query_end = std::chrono::steady_clock::now();

        // ── 输出结果 ──
        double query_seconds =
            std::chrono::duration<double>(query_end - query_start).count();

        std::cout << "\n========== 结果 ==========\n";
        std::cout << "模式: " << (use_knn ? "k-NN (k=" : "1-NN")
                  << (use_knn ? std::to_string(knn_k) + ")" : "") << "\n";
        std::cout << "测试数: " << num_to_test << "\n";
        std::cout << "正确数: " << correct << " / " << num_to_test << "\n";
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "准确率: " << 100.0 * correct / num_to_test << "%\n";
        std::cout << "平均候选: "
                  << double(total_candidates) / num_to_test << "\n";
        std::cout << "查询耗时: " << query_seconds << " 秒\n";
        std::cout << "平均每张: "
                  << query_seconds / num_to_test * 1000 << " 毫秒\n";

        // ── 挑战任务 3（选做）：跟暴力搜索对比 ──
        // 取前 100 张测试图做暴力搜索对比
        // 如果取消下面注释，会看到暴力搜索慢得多但准确率更高

        // TODO（选做）：取消下面注释，对比 LSH 和暴力搜索
        // int brute_correct = 0;
        // for (int i = 0; i < 100 && i < num_to_test; ++i) {
        //     const std::int16_t* img =
        //         test.images.data() + std::size_t(i) * dimension;
        //     int id = brute_force_nn(train.images, train.count, dimension, img);
        //     if (train.labels[id] == test.labels[i]) ++brute_correct;
        // }
        // std::cout << "\n暴力搜索（前 100 张）: " << brute_correct
        //           << " / 100 正确\n";

    } catch (const std::exception& error) {
        std::cerr << "\n出错了: " << error.what() << '\n';
        std::cerr << "用法: " << argv[0]
                  << " [数据目录] [-k knn值] [-n 测试数量] [--no-detail]\n";
        std::cerr << "如果在 advanced/ 下运行，试试: ./lsh_advanced ../test/data\n";
        return 1;
    }
    return 0;
}
