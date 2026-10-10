#ifndef LSH_H
#define LSH_H

#include <cstdint>
#include <utility>
#include <vector>

// LSH 的配置参数
struct LshConfig {
    int table_count = 16;       // L：哈希表数量（多 → 更准但更慢）
    int bits_per_table = 12;    // K：每张表的哈希位数（多 → 桶更细，筛选更强）
    int min_candidates = 20;    // 候选太少时触发相邻桶查询
    std::uint32_t seed = 42;    // 随机种子（固定 → 结果可复现）
};

// 1-NN 查询结果
struct LshResult {
    int index = -1;                      // 最近的训练图片编号
    std::int64_t squared_distance = 0;   // 距离平方
    int candidate_count = 0;             // 检查了多少张候选
};

// k-NN 查询结果（挑战任务用）
struct KnnResult {
    std::vector<int> indices;             // k 个最近邻的训练图片编号
    std::vector<std::int64_t> distances;  // 对应的距离平方
    int candidate_count = 0;              // 候选总数
};

class LshIndex {
public:
    explicit LshIndex(LshConfig config = {});

    // 建立索引
    void build(const std::vector<std::int16_t>& points,
               int point_count,
               int dimension);

    // 1-NN 查询：返回最近的 1 张训练图片
    LshResult query(const std::int16_t* point);

    // ── 挑战任务 1：k-NN 查询 ──
    // 返回最近的 k 张训练图片，用于多数投票分类
    // 提示：跟 query() 类似，只是在候选里找前 k 个而不是前 1 个
    //       可以先复制 query() 的代码，再把"找最小"改成"维护一个长度 k 的列表"
    KnnResult query_knn(const std::int16_t* point, int k);

    int point_count() const { return point_count_; }
    int dimension() const { return dimension_; }

private:
    struct Table {
        std::vector<std::int16_t> planes;
        std::vector<std::vector<int>> buckets;
    };

    std::uint32_t signature(const Table& table,
                            const std::int16_t* point) const;
    void add_bucket(const Table& table, std::uint32_t bucket_id);

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
