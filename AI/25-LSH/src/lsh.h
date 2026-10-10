#ifndef LSH_H
#define LSH_H

#include <cstdint>
#include <vector>

struct LshConfig {
    int table_count = 16;
    int bits_per_table = 12;
    int min_candidates = 20;
    std::uint32_t seed = 42;
};

struct LshResult {
    int index = -1;
    std::int64_t squared_distance = 0;
    int candidate_count = 0;
};

class LshIndex {
public:
    explicit LshIndex(LshConfig config = {});

    void build(const std::vector<std::int16_t>& points,
               int point_count,
               int dimension);

    LshResult query(const std::int16_t* point);

    int point_count() const { return point_count_; }
    int dimension() const { return dimension_; }

private:
    struct Table {
        std::vector<std::int16_t> planes;
        std::vector<std::vector<int>> buckets;
    };

    std::uint32_t signature(const Table& table,
                            const std::int16_t* point) const;
    void add_bucket(const Table& table, std::uint32_t signature);

    LshConfig config_;
    const std::vector<std::int16_t>* points_ = nullptr;
    int point_count_ = 0;
    int dimension_ = 0;
    std::vector<Table> tables_;
    std::vector<int> seen_;
    std::vector<int> candidates_;
    int query_mark_ = 0;
};

#endif
