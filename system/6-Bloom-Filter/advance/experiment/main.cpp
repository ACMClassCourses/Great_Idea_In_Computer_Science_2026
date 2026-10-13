#include "src.hpp"

#include <cstddef>
#include <iomanip>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>

std::string random_string(std::mt19937& generator, const std::string& prefix) {
    const std::string alphabet = "abcdefghijklmnopqrstuvwxyz0123456789";
    std::string text = prefix;
    for (int i = 0; i < 20; ++i) {
        text += alphabet[generator() % alphabet.size()];
    }
    return text;
}

std::vector<std::string> generate_strings(
    int count,
    const std::string& prefix,
    std::mt19937& generator) {
    std::vector<std::string> result;
    std::set<std::string> used;
    while (static_cast<int>(result.size()) < count) {
        std::string text = random_string(generator, prefix);
        if (used.insert(text).second) {
            result.push_back(text);
        }
    }
    return result;
}

void run_experiment(
    const std::string& group,
    int inserted_count,
    std::size_t bit_count,
    int hash_count,
    const std::vector<std::string>& inserted,
    const std::vector<std::string>& queries) {
    BloomFilter filter(bit_count, hash_count);
    std::set<std::string> exact;

    for (int i = 0; i < inserted_count; ++i) {
        filter.add(inserted[i]);
        exact.insert(inserted[i]);
    }

    int false_negatives = 0;
    for (int i = 0; i < inserted_count; ++i) {
        if (!filter.contains(inserted[i])) {
            ++false_negatives;
        }
    }

    int false_positives = 0;
    int negative_queries = 0;
    for (std::size_t i = 0; i < queries.size(); ++i) {
        if (exact.count(queries[i]) == 0) {
            ++negative_queries;
            if (filter.contains(queries[i])) {
                ++false_positives;
            }
        }
    }

    double rate = 100.0 * false_positives / negative_queries;
    std::size_t string_bytes = 0;
    for (int i = 0; i < inserted_count; ++i) {
        string_bytes += inserted[i].size();
    }
    std::cout << group << ","
              << inserted_count << ","
              << bit_count << ","
              << hash_count << ","
              << string_bytes << ","
              << filter.storage_bytes() << ","
              << negative_queries << ","
              << false_positives << ","
              << std::fixed << std::setprecision(4) << rate << ","
              << false_negatives << "\n";
}

bool basic_checks() {
    BloomFilter seven_bits(7, 3);
    BloomFilter eight_bits(8, 3);
    BloomFilter nine_bits(9, 3);
    if (seven_bits.storage_bytes() != 1
        || eight_bits.storage_bytes() != 1
        || nine_bits.storage_bytes() != 2) {
        return false;
    }

    BloomFilter first(1024, 4);
    BloomFilter second(1024, 4);
    first.add("apple");
    if (!first.contains("apple") || second.contains("apple")) {
        return false;
    }
    return true;
}

int main() {
    if (!basic_checks()) {
        return 1;
    }

    std::mt19937 generator(3261);
    std::vector<std::string> inserted =
        generate_strings(4000, "inserted_", generator);
    std::vector<std::string> queries =
        generate_strings(10000, "missing_", generator);

    std::cout << "group,n,m,k,string_bytes,bloom_bytes,negative_queries,"
                 "false_positives,false_positive_rate,false_negatives\n";

    const int bits_per_item[] = {4, 8, 12};
    const int hash_counts[] = {1, 4, 8};
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            run_experiment(
                "parameters",
                2000,
                2000 * bits_per_item[i],
                hash_counts[j],
                inserted,
                queries);
        }
    }

    const int inserted_counts[] = {500, 1000, 2000, 4000};
    for (int i = 0; i < 4; ++i) {
        run_experiment(
            "saturation",
            inserted_counts[i],
            8000,
            4,
            inserted,
            queries);
    }
    return 0;
}
