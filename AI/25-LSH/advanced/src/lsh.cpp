#include "lsh.h"

#include <algorithm>
#include <limits>
#include <random>
#include <stdexcept>

// ──────────────────────────────────────────────────────────────────────────
//  LSH 索引实现
// ──────────────────────────────────────────────────────────────────────────
// 这个文件实现了"随机超平面 LSH"。
//
// 核心流程：
//   build()  → 生成随机超平面，把训练图片分到各表的桶里
//   query()  → 算查询图片的桶号，收集候选，找最近的
//
// 你需要关注的挑战：
//   query_knn() → 目前是空的，需要你来实现（见文件末尾）

LshIndex::LshIndex(LshConfig config) : config_(config) {}

// 计算一张图片在某张表里的桶号（哈希签名）
// 原理：对每个随机超平面，算图片和超平面的点积
//       点积 >= 0 → 这一位是 1
//       点积 <  0 → 这一位是 0
//       K 个位拼成一个整数 = 桶号
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

// 建立索引
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

    // 用固定种子初始化随机数生成器（结果可复现）
    std::mt19937 random(config_.seed);
    std::uniform_int_distribution<int> weight(-127, 127);

    for (Table& table : tables_) {
        // 生成这张表的随机超平面（每维取 -127~127，不能是 0）
        table.planes.resize(
            std::size_t(config_.bits_per_table) * dimension_);
        for (std::int16_t& value : table.planes) {
            do {
                value = static_cast<std::int16_t>(weight(random));
            } while (value == 0);
        }

        // 分配桶并插入训练图片
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

// 把一个桶里的图片编号加入候选列表（去重）
void LshIndex::add_bucket(const Table& table, std::uint32_t bucket_id) {
    for (int id : table.buckets[bucket_id]) {
        if (seen_[id] != query_mark_) {
            seen_[id] = query_mark_;
            candidates_.push_back(id);
        }
    }
}

// 1-NN 查询：找最近的 1 张训练图片
LshResult LshIndex::query(const std::int16_t* point) {
    if (points_ == nullptr) {
        throw std::logic_error("索引还没建立，请先调用 build()");
    }

    // 更新查询标记（用于去重，避免重复清空数组）
    if (query_mark_ == std::numeric_limits<int>::max()) {
        std::fill(seen_.begin(), seen_.end(), 0);
        query_mark_ = 1;
    } else {
        ++query_mark_;
    }
    candidates_.clear();

    // 第一步：在每张表里找对应桶，收集候选
    std::vector<std::uint32_t> signatures(tables_.size());
    for (std::size_t i = 0; i < tables_.size(); ++i) {
        signatures[i] = signature(tables_[i], point);
        add_bucket(tables_[i], signatures[i]);
    }

    // 第二步：候选太少时，查相邻桶（翻转 1 位 = 汉明距离 1）
    // 这叫"多探测"（multi-probe），能明显提高准确率
    if (static_cast<int>(candidates_.size()) < config_.min_candidates) {
        for (std::size_t i = 0; i < tables_.size(); ++i) {
            for (int bit = 0; bit < config_.bits_per_table; ++bit) {
                add_bucket(tables_[i],
                           signatures[i] ^ (std::uint32_t{1} << bit));
            }
        }
    }

    // 第三步：在候选里找距离最小的（平方欧氏距离，不开根号）
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

// ══════════════════════════════════════════════════════════════════════════
//  挑战任务 1：实现 k-NN 查询
// ══════════════════════════════════════════════════════════════════════════
//
//  目标：在候选集合里找距离最小的 k 张训练图片，返回它们的编号和距离。
//
//  为什么需要 k-NN？
//    1-NN 只看最近的一张图，如果这张图恰好是噪声，就会判错。
//    k-NN 取最近 k 张图，看它们的标签哪个出现最多（多数投票），
//    相当于"多人投票"，更稳定。
//
//  提示：
//    1. 前半部分（收集候选）跟 query() 一模一样，可以直接复制
//    2. 后半部分需要维护"前 k 近"的列表，有几种做法：
//       a) 简单做法：把所有候选的 (id, distance) 存下来，
//          按 distance 排序，取前 k 个
//       b) 进阶做法：维护一个大小 k 的数组，遍历候选时保持有序
//       c) 最优做法：用 std::partial_sort 或 std::nth_element
//    3. 新手推荐做法 (a)，清晰易懂，不容易写错
//
//  保底方案：
//    如果实在写不出来，可以参考 solution/lsh_complete.cpp 里的实现。
//    或者直接用 query() 做 1-NN，程序一样能跑，只是少了 k-NN 功能。
//
KnnResult LshIndex::query_knn(const std::int16_t* point, int k) {
    if (points_ == nullptr) {
        throw std::logic_error("索引还没建立，请先调用 build()");
    }
    if (k <= 0) {
        throw std::invalid_argument("k 必须 >= 1");
    }

    // ── TODO：把下面的代码替换成你的实现 ──
    (void)point;  // 暂时没用，实现后删掉这行
    (void)k;      // 暂时没用，实现后删掉这行

    // 目前直接返回空结果，你改成返回 k 个最近的
    KnnResult result;
    result.candidate_count = 0;
    return result;

    // ── 实现思路 ──
    // 1. 跟 query() 一样收集候选（复制前面的多探测逻辑）
    // 2. 算出每个候选的距离
    // 3. 排序取前 k 个
    // 4. 填入 result.indices 和 result.distances
    //
    // 参考代码框架：
    //
    //   // 收集候选（同 query()）
    //   ... 更新 query_mark_，收集 exact bucket + multi-probe ...
    //
    //   // 算距离并排序
    //   std::vector<std::pair<std::int64_t, int>> scored;
    //   for (int id : candidates_) {
    //       // 算距离...
    //       scored.push_back({distance, id});
    //   }
    //   std::partial_sort(scored.begin(),
    //                     scored.begin() + std::min(k, int(scored.size())),
    //                     scored.end());
    //   // 取前 k 个
    //   result.candidate_count = int(candidates_.size());
    //   for (int i = 0; i < k && i < int(scored.size()); ++i) {
    //       result.indices.push_back(scored[i].second);
    //       result.distances.push_back(scored[i].first);
    //   }
    //   return result;
}
