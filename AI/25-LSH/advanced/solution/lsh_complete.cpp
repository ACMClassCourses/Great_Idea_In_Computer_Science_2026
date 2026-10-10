// ============================================================================
//  lsh_complete.cpp —— 完整参考实现（保底用）
// ============================================================================
//
//  这个文件是 lsh.cpp 的完整版本，包含 query_knn 的实现。
//
//  使用方式：
//    如果你完成了 lsh.cpp 里的 query_knn，正常编译即可：
//      g++ -std=c++17 -O2 -Isrc src/mnist.cpp src/lsh.cpp src/main.cpp -o lsh_advanced
//
//    如果 query_knn 写不出来，用这个文件替换 lsh.cpp 编译：
//      g++ -std=c++17 -O2 -Isrc src/mnist.cpp solution/lsh_complete.cpp src/main.cpp -o lsh_advanced
//
//  注意：这个文件和 lsh.cpp 不能同时编译（函数定义会重复）。
// ============================================================================

#include "lsh.h"

#include <algorithm>
#include <limits>
#include <random>
#include <stdexcept>
#include <utility>

LshIndex::LshIndex(LshConfig config) : config_(config) {}

std::uint32_t LshIndex::signature(const Table& table,
                                  const std::int16_t* point) const {
    std::uint32_t value = 0;
    for (int bit = 0; bit < config_.bits_per_table; ++bit) {
        const std::int16_t* plane =
            table.planes.data() + std::size_t(bit) * dimension_;
        std::int64_t dot = 0;
        for (int d = 0; d < dimension_; ++d) {
            dot += std::int64_t(point[d]) * plane[d];
        }
        if (dot >= 0) {
            value |= std::uint32_t{1} << bit;
        }
    }
    return value;
}

void LshIndex::build(const std::vector<std::int16_t>& points,
                     int point_count,
                     int dimension) {
    if (point_count <= 0 || dimension <= 0 ||
        points.size() != std::size_t(point_count) * dimension) {
        throw std::invalid_argument("数据参数不合法");
    }
    if (config_.table_count <= 0 || config_.bits_per_table <= 0 ||
        config_.bits_per_table > 20) {
        throw std::invalid_argument("LSH 参数不合法");
    }

    points_ = &points;
    point_count_ = point_count;
    dimension_ = dimension;
    const std::size_t bucket_count =
        std::size_t{1} << config_.bits_per_table;

    tables_.clear();
    tables_.resize(config_.table_count);

    std::mt19937 random(config_.seed);
    std::uniform_int_distribution<int> weight(-127, 127);

    for (Table& table : tables_) {
        table.planes.resize(
            std::size_t(config_.bits_per_table) * dimension_);
        for (std::int16_t& value : table.planes) {
            do {
                value = static_cast<std::int16_t>(weight(random));
            } while (value == 0);
        }

        table.buckets.clear();
        table.buckets.resize(bucket_count);
        for (int id = 0; id < point_count_; ++id) {
            const std::int16_t* point =
                points.data() + std::size_t(id) * dimension_;
            table.buckets[signature(table, point)].push_back(id);
        }
    }

    seen_.assign(point_count_, 0);
    candidates_.clear();
    candidates_.reserve(point_count_);
    query_mark_ = 0;
}

void LshIndex::add_bucket(const Table& table, std::uint32_t bucket_id) {
    for (int id : table.buckets[bucket_id]) {
        if (seen_[id] != query_mark_) {
            seen_[id] = query_mark_;
            candidates_.push_back(id);
        }
    }
}

LshResult LshIndex::query(const std::int16_t* point) {
    if (points_ == nullptr) {
        throw std::logic_error("索引还没建立，请先调用 build()");
    }

    if (query_mark_ == std::numeric_limits<int>::max()) {
        std::fill(seen_.begin(), seen_.end(), 0);
        query_mark_ = 1;
    } else {
        ++query_mark_;
    }
    candidates_.clear();

    // 收集候选（精确桶 + 多探测）
    std::vector<std::uint32_t> signatures(tables_.size());
    for (std::size_t i = 0; i < tables_.size(); ++i) {
        signatures[i] = signature(tables_[i], point);
        add_bucket(tables_[i], signatures[i]);
    }

    if (static_cast<int>(candidates_.size()) < config_.min_candidates) {
        for (std::size_t i = 0; i < tables_.size(); ++i) {
            for (int bit = 0; bit < config_.bits_per_table; ++bit) {
                add_bucket(tables_[i],
                           signatures[i] ^ (std::uint32_t{1} << bit));
            }
        }
    }

    // 找最近的 1 个
    LshResult result;
    result.candidate_count = static_cast<int>(candidates_.size());
    result.squared_distance = std::numeric_limits<std::int64_t>::max();

    for (int id : candidates_) {
        const std::int16_t* candidate =
            points_->data() + std::size_t(id) * dimension_;
        std::int64_t distance = 0;
        for (int d = 0; d < dimension_; ++d) {
            const std::int64_t diff =
                static_cast<std::int64_t>(point[d]) - candidate[d];
            distance += diff * diff;
        }
        if (distance < result.squared_distance) {
            result.squared_distance = distance;
            result.index = id;
        }
    }

    return result;
}

// ── k-NN 查询：找最近的 k 张训练图片 ──
KnnResult LshIndex::query_knn(const std::int16_t* point, int k) {
    if (points_ == nullptr) {
        throw std::logic_error("索引还没建立，请先调用 build()");
    }
    if (k <= 0) {
        throw std::invalid_argument("k 必须 >= 1");
    }

    // 前半部分跟 query() 完全一样：收集候选
    if (query_mark_ == std::numeric_limits<int>::max()) {
        std::fill(seen_.begin(), seen_.end(), 0);
        query_mark_ = 1;
    } else {
        ++query_mark_;
    }
    candidates_.clear();

    std::vector<std::uint32_t> signatures(tables_.size());
    for (std::size_t i = 0; i < tables_.size(); ++i) {
        signatures[i] = signature(tables_[i], point);
        add_bucket(tables_[i], signatures[i]);
    }

    if (static_cast<int>(candidates_.size()) < config_.min_candidates) {
        for (std::size_t i = 0; i < tables_.size(); ++i) {
            for (int bit = 0; bit < config_.bits_per_table; ++bit) {
                add_bucket(tables_[i],
                           signatures[i] ^ (std::uint32_t{1} << bit));
            }
        }
    }

    // 后半部分：算距离，取前 k 个
    // 用 pair<距离, 编号> 存所有候选
    std::vector<std::pair<std::int64_t, int>> scored;
    scored.reserve(candidates_.size());

    for (int id : candidates_) {
        const std::int16_t* candidate =
            points_->data() + std::size_t(id) * dimension_;
        std::int64_t distance = 0;
        for (int d = 0; d < dimension_; ++d) {
            const std::int64_t diff =
                static_cast<std::int64_t>(point[d]) - candidate[d];
            distance += diff * diff;
        }
        scored.emplace_back(distance, id);
    }

    // partial_sort 只排前 k 个，比全排序快
    int take = std::min(k, static_cast<int>(scored.size()));
    std::partial_sort(scored.begin(), scored.begin() + take, scored.end());

    // 填入结果
    KnnResult result;
    result.candidate_count = static_cast<int>(candidates_.size());
    result.indices.reserve(take);
    result.distances.reserve(take);
    for (int i = 0; i < take; ++i) {
        result.indices.push_back(scored[i].second);
        result.distances.push_back(scored[i].first);
    }

    return result;
}
