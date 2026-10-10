#include "lsh.h"

#include <algorithm>
#include <limits>
#include <random>
#include <stdexcept>

LshIndex::LshIndex(LshConfig config) : config_(config) {}

std::uint32_t LshIndex::signature(const Table& table,
                                  const std::int16_t* point) const {
    std::uint32_t value = 0;
    for (int bit = 0; bit < config_.bits_per_table; ++bit) {
        const std::int16_t* plane =
            table.planes.data() + static_cast<std::size_t>(bit) * dimension_;
        std::int64_t dot = 0;
        for (int d = 0; d < dimension_; ++d) {
            dot += static_cast<std::int64_t>(point[d]) * plane[d];
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
        points.size() != static_cast<std::size_t>(point_count) * dimension) {
        throw std::invalid_argument("invalid point array");
    }
    if (config_.table_count <= 0 || config_.bits_per_table <= 0 ||
        config_.bits_per_table > 20) {
        throw std::invalid_argument("invalid LSH parameters");
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
            static_cast<std::size_t>(config_.bits_per_table) * dimension_);
        for (std::int16_t& value : table.planes) {
            do {
                value = static_cast<std::int16_t>(weight(random));
            } while (value == 0);
        }

        table.buckets.clear();
        table.buckets.resize(bucket_count);
        for (int id = 0; id < point_count_; ++id) {
            const std::int16_t* point =
                points.data() + static_cast<std::size_t>(id) * dimension_;
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
        throw std::logic_error("LSH index has not been built");
    }

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

    LshResult result;
    result.candidate_count = static_cast<int>(candidates_.size());
    result.squared_distance = std::numeric_limits<std::int64_t>::max();

    for (int id : candidates_) {
        const std::int16_t* candidate =
            points_->data() + static_cast<std::size_t>(id) * dimension_;
        std::int64_t distance = 0;
        for (int d = 0; d < dimension_; ++d) {
            const std::int64_t difference =
                static_cast<std::int64_t>(point[d]) - candidate[d];
            distance += difference * difference;
        }
        if (distance < result.squared_distance) {
            result.squared_distance = distance;
            result.index = id;
        }
    }

    return result;
}
