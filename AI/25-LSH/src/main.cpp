#include "lsh.h"
#include "mnist.h"

#include <chrono>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

int main(int argc, char** argv) {
    try {
        const std::filesystem::path data_directory =
            argc > 1 ? argv[1] : std::filesystem::path("test/data");

        const MnistDataset train = load_mnist(
            (data_directory / "train-images.idx3-ubyte").string(),
            (data_directory / "train-labels.idx1-ubyte").string());
        const MnistDataset test = load_mnist(
            (data_directory / "t10k-images.idx3-ubyte").string(),
            (data_directory / "t10k-labels.idx1-ubyte").string());

        if (train.rows != test.rows || train.cols != test.cols) {
            throw std::runtime_error("training and test dimensions differ");
        }

        const int dimension = train.rows * train.cols;
        const LshConfig config{16, 12, 20, 42};
        LshIndex index(config);

        const auto build_start = std::chrono::steady_clock::now();
        index.build(train.images, train.count, dimension);
        const auto build_end = std::chrono::steady_clock::now();

        int correct = 0;
        long long total_candidates = 0;
        const auto query_start = std::chrono::steady_clock::now();
        for (int i = 0; i < test.count; ++i) {
            const std::int16_t* image =
                test.images.data() + static_cast<std::size_t>(i) * dimension;
            const LshResult result = index.query(image);
            if (result.index >= 0 &&
                train.labels[result.index] == test.labels[i]) {
                ++correct;
            }
            total_candidates += result.candidate_count;
        }
        const auto query_end = std::chrono::steady_clock::now();

        const double build_seconds =
            std::chrono::duration<double>(build_end - build_start).count();
        const double query_seconds =
            std::chrono::duration<double>(query_end - query_start).count();

        std::cout << "Training images: " << train.count << '\n'
                  << "Test images: " << test.count << '\n'
                  << "LSH tables: " << config.table_count
                  << ", bits per table: " << config.bits_per_table << '\n'
                  << std::fixed << std::setprecision(2)
                  << "Average candidates: "
                  << static_cast<double>(total_candidates) / test.count << '\n'
                  << "Correct: " << correct << " / " << test.count << '\n'
                  << "Accuracy: "
                  << 100.0 * static_cast<double>(correct) / test.count << "%\n"
                  << "Build time: " << build_seconds << " s\n"
                  << "Query time: " << query_seconds << " s\n";
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
