// ============================================================================
//  LSH 近似最近邻检索 —— 基础版（单文件）
// ============================================================================
//
//  这个程序做什么？
//    1. 读取 MNIST 数据集（6万张训练图 + 1万张测试图，每张 28×28 像素）
//    2. 用 LSH（局部敏感哈希）给训练图片建索引
//    3. 对每张测试图片，用 LSH 快速找到最相似的训练图片
//    4. 用找到的那张训练图片的标签来"猜"测试图片是哪个数字
//    5. 输出猜对的准确率
//
//  LSH 的核心思想（一句话）：
//    把相似的图片扔进同一个"桶"里，查询时只搜这些桶，不用翻全部 6 万张。
//
//  你需要写的代码：
//    TODO 1：squared_distance() —— 算两张图片的距离（约 5 行）
//    TODO 2：多探测查询 —— 候选太少时查相邻桶（约 4 行）
//    两个 TODO 都有详细提示和参考答案（注释里），卡住了可以看。
//
//  编译运行：
//    g++ -std=c++17 -O2 -o lsh_basic lsh_basic.cpp
//    ./lsh_basic ../test/data
//
// ============================================================================

#include <cstdint>      // int16_t, uint32_t 等固定宽度整数
#include <fstream>      // 文件读取
#include <iostream>     // 输入输出
#include <limits>       // 数值上限
#include <random>       // 随机数
#include <string>       // 字符串
#include <vector>       // 动态数组

// ──────────────────────────────────────────────────────────────────────────
//  第一部分：MNIST 数据集读取（已实现，不用改）
// ──────────────────────────────────────────────────────────────────────────
// MNIST 的图片和标签都存在二进制文件里（IDX 格式）。
// 文件头里的整数是大端序（高位在前），而我们的电脑是小端序，
// 所以需要手动按字节拼出整数。

std::uint32_t read_big_endian_u32(std::ifstream& f) {
    unsigned char b[4];
    f.read(reinterpret_cast<char*>(b), 4);
    if (!f) throw std::runtime_error("文件读取失败");
    return (std::uint32_t(b[0]) << 24) |
           (std::uint32_t(b[1]) << 16) |
           (std::uint32_t(b[2]) << 8)  |
            std::uint32_t(b[3]);
}

struct MnistDataset {
    int count = 0;
    int rows = 0;
    int cols = 0;
    std::vector<std::int16_t> images;
    std::vector<std::uint8_t> labels;
};

MnistDataset load_mnist(const std::string& image_path,
                        const std::string& label_path) {
    std::ifstream img_file(image_path, std::ios::binary);
    std::ifstream lbl_file(label_path, std::ios::binary);
    if (!img_file || !lbl_file) {
        throw std::runtime_error("打不开 MNIST 文件，检查路径");
    }

    std::uint32_t img_magic = read_big_endian_u32(img_file);
    int count = int(read_big_endian_u32(img_file));
    int rows  = int(read_big_endian_u32(img_file));
    int cols  = int(read_big_endian_u32(img_file));
    std::uint32_t lbl_magic = read_big_endian_u32(lbl_file);
    int lbl_count = int(read_big_endian_u32(lbl_file));

    if (img_magic != 2051 || lbl_magic != 2049 || count != lbl_count) {
        throw std::runtime_error("MNIST 文件格式不对");
    }

    std::size_t pixel_count = std::size_t(count) * rows * cols;
    std::vector<unsigned char> raw_bytes(pixel_count);
    std::vector<std::uint8_t> labels(lbl_count);
    img_file.read(reinterpret_cast<char*>(raw_bytes.data()), pixel_count);
    lbl_file.read(reinterpret_cast<char*>(labels.data()), lbl_count);
    if (!img_file || !lbl_file) {
        throw std::runtime_error("MNIST 文件内容不完整");
    }

    MnistDataset ds;
    ds.count = count;
    ds.rows = rows;
    ds.cols = cols;
    ds.labels = std::move(labels);
    ds.images.resize(pixel_count);
    for (std::size_t i = 0; i < pixel_count; ++i) {
        ds.images[i] = raw_bytes[i];
    }
    return ds;
}

// ──────────────────────────────────────────────────────────────────────────
//  第二部分：LSH 索引
// ──────────────────────────────────────────────────────────────────────────
// 用"随机超平面 LSH"：
//   - 随机生成一个向量（超平面），跟图片做点积
//   - 点积 >= 0 → 哈希位是 1
//   - 点积 <  0 → 哈希位是 0
//   - 多个超平面得到多个位，拼成一个整数 = 桶号

struct LshConfig {
    int table_count = 8;
    int bits_per_table = 8;
    int min_candidates = 20;
    std::uint32_t seed = 42;
};

struct LshResult {
    int index = -1;
    std::int64_t squared_distance = 0;
    int candidate_count = 0;
};

struct LshTable {
    std::vector<std::int16_t> planes;
    std::vector<std::vector<int>> buckets;
};

// ╔══════════════════════════════════════════════════════════════════════╗
// ║  TODO 1：实现平方欧氏距离函数（必做，约 5 行代码）                      ║
// ╚══════════════════════════════════════════════════════════════════════╝
// 计算两张图片 a 和 b 之间的平方欧氏距离。
//
// 公式：distance = (a[0]-b[0])² + (a[1]-b[1])² + ... + (a[dim-1]-b[dim-1])²
//
// 提示：
//   1. 定义一个 int64_t 变量 dist = 0 用来累加
//   2. 用 for 循环遍历每一维 d（从 0 到 dim-1）
//   3. 算差值：diff = int64_t(a[d]) - b[d]
//      （转成 int64_t 是防止两个大数相减溢出）
//   4. 累加：dist += diff * diff
//   5. 循环结束后 return dist
//
// 如果你没写这个函数（return 0），所有图片看起来"一样近"，
// 准确率会降到 10% 左右（等于瞎猜）。写对了应该 95% 以上。
//
std::int64_t squared_distance(const std::int16_t* a,
                              const std::int16_t* b, int dim) {
    // ===== 在这里写你的代码 =====


    // ===== 参考答案（实在卡住了取消下面的注释看一眼，然后自己重写）=====
    // std::int64_t dist = 0;
    // for (int d = 0; d < dim; ++d) {
    //     std::int64_t diff = std::int64_t(a[d]) - b[d];
    //     dist += diff * diff;
    // }
    // return dist;

    return 0;  // ← 删掉这行，换成你的实现
}

class LshIndex {
public:
    LshConfig config;
    const std::vector<std::int16_t>* points = nullptr;
    int point_count = 0;
    int dimension = 0;
    std::vector<LshTable> tables;
    std::vector<int> seen;
    std::vector<int> candidates;
    int query_mark = 0;

    // 计算桶号（签名）——已实现，不用改
    std::uint32_t signature(const LshTable& table,
                            const std::int16_t* point) const {
        std::uint32_t value = 0;
        for (int bit = 0; bit < config.bits_per_table; ++bit) {
            const std::int16_t* plane =
                table.planes.data() + std::size_t(bit) * dimension;
            std::int64_t dot = 0;
            for (int d = 0; d < dimension; ++d) {
                dot += std::int64_t(point[d]) * plane[d];
            }
            if (dot >= 0) {
                value |= std::uint32_t(1) << bit;
            }
        }
        return value;
    }

    // 建索引——已实现，不用改
    void build(const std::vector<std::int16_t>& pts,
               int count, int dim) {
        points = &pts;
        point_count = count;
        dimension = dim;

        std::size_t bucket_count = std::size_t(1) << config.bits_per_table;
        tables.clear();
        tables.resize(config.table_count);

        std::mt19937 rng(config.seed);
        std::uniform_int_distribution<int> rand_weight(-127, 127);

        for (LshTable& table : tables) {
            table.planes.resize(std::size_t(config.bits_per_table) * dimension);
            for (std::int16_t& w : table.planes) {
                do { w = std::int16_t(rand_weight(rng)); } while (w == 0);
            }
            table.buckets.clear();
            table.buckets.resize(bucket_count);
            for (int id = 0; id < point_count; ++id) {
                const std::int16_t* img =
                    points->data() + std::size_t(id) * dimension;
                table.buckets[signature(table, img)].push_back(id);
            }
        }

        seen.assign(point_count, 0);
        candidates.clear();
        candidates.reserve(point_count);
        query_mark = 0;
    }

    // 把一个桶里的图片编号加入候选（去重）——已实现，不用改
    void add_bucket(const LshTable& table, std::uint32_t bucket_id) {
        for (int id : table.buckets[bucket_id]) {
            if (seen[id] != query_mark) {
                seen[id] = query_mark;
                candidates.push_back(id);
            }
        }
    }

    // 查询：找到跟 point 最相似的训练图片
    LshResult query(const std::int16_t* point) {
        ++query_mark;
        candidates.clear();

        // 第一步：在每张表里找到对应桶，收集候选（已实现）
        std::vector<std::uint32_t> sigs(tables.size());
        for (std::size_t i = 0; i < tables.size(); ++i) {
            sigs[i] = signature(tables[i], point);
            add_bucket(tables[i], sigs[i]);
        }

        // ╔════════════════════════════════════════════════════════════════╗
        // ║  TODO 2：多探测——候选太少时查相邻桶（必做，约 4 行代码）          ║
        // ╚════════════════════════════════════════════════════════════════╝
        // 当候选数 < min_candidates 时，去查每张表里"差 1 位"的相邻桶。
        //
        // 提示：
        //   1. 外层 for 循环遍历每张表：for (size_t i = 0; i < tables.size(); ++i)
        //   2. 内层 for 循环遍历每个位：for (int bit = 0; bit < config.bits_per_table; ++bit)
        //   3. 相邻桶号 = sigs[i] ^ (uint32_t(1) << bit)
        //      （XOR 翻转第 bit 位，就是把 0 变 1、1 变 0）
        //   4. 调用 add_bucket(tables[i], 相邻桶号)
        //
        // 如果你没写这段，候选太少时可能找不到近邻，准确率会降到 80% 左右。
        // 写对了应该 95% 以上。
        //
        if (int(candidates.size()) < config.min_candidates) {
            // ===== 在这里写你的代码 =====


            // ===== 参考答案（实在卡住了取消注释看一眼）=====
            // for (std::size_t i = 0; i < tables.size(); ++i) {
            //     for (int bit = 0; bit < config.bits_per_table; ++bit) {
            //         add_bucket(tables[i], sigs[i] ^ (std::uint32_t(1) << bit));
            //     }
            // }
        }

        // 第三步：在候选里找距离最近的（已实现，调用了你写的 squared_distance）
        LshResult result;
        result.candidate_count = int(candidates.size());
        result.squared_distance = std::numeric_limits<std::int64_t>::max();

        for (int id : candidates) {
            const std::int16_t* cand =
                points->data() + std::size_t(id) * dimension;
            // 这里调用了 TODO 1 的函数
            std::int64_t dist = squared_distance(point, cand, dimension);
            if (dist < result.squared_distance) {
                result.squared_distance = dist;
                result.index = id;
            }
        }
        return result;
    }
};

// ──────────────────────────────────────────────────────────────────────────
//  第三部分：ASCII 艺术（已实现，不用改）
// ──────────────────────────────────────────────────────────────────────────
void print_ascii_art(const std::int16_t* img, int rows, int cols) {
    for (int r = 0; r < rows; ++r) {
        for (int c = 0; c < cols; ++c) {
            int pixel = img[r * cols + c];
            if      (pixel > 200) std::cout << '@';
            else if (pixel > 128) std::cout << '#';
            else if (pixel >  64) std::cout << '.';
            else                  std::cout << ' ';
        }
        std::cout << '\n';
    }
}

// ──────────────────────────────────────────────────────────────────────────
//  第四部分：主程序（已实现，不用改）
// ──────────────────────────────────────────────────────────────────────────
int main(int argc, char** argv) {
    try {
        std::string data_dir = (argc > 1) ? argv[1] : "../test/data";

        std::cout << "正在读取 MNIST 数据集...\n";
        MnistDataset train = load_mnist(
            data_dir + "/train-images.idx3-ubyte",
            data_dir + "/train-labels.idx1-ubyte");
        MnistDataset test = load_mnist(
            data_dir + "/t10k-images.idx3-ubyte",
            data_dir + "/t10k-labels.idx1-ubyte");

        int dimension = train.rows * train.cols;
        std::cout << "训练集: " << train.count << " 张\n"
                  << "测试集: " << test.count << " 张\n"
                  << "图片尺寸: " << train.rows << " x " << train.cols << "\n\n";

        std::cout << "第一张测试图片（标签是 " << int(test.labels[0])
                  << "）：\n";
        print_ascii_art(test.images.data(), train.rows, train.cols);
        std::cout << "\n";

        LshConfig config;
        std::cout << "正在建立 LSH 索引（" << config.table_count
                  << " 张表，每表 " << config.bits_per_table << " 位）...\n";
        LshIndex index;
        index.config = config;
        index.build(train.images, train.count, dimension);
        std::cout << "索引建立完成！\n\n";

        int test_limit = 1000;

        int correct = 0;
        long long total_candidates = 0;

        std::cout << "开始识别前 " << test_limit << " 张测试图片...\n";
        for (int i = 0; i < test_limit && i < test.count; ++i) {
            const std::int16_t* img =
                test.images.data() + std::size_t(i) * dimension;
            LshResult result = index.query(img);
            if (result.index >= 0 &&
                train.labels[result.index] == test.labels[i]) {
                ++correct;
            }
            total_candidates += result.candidate_count;

            if (i < 5) {
                int predicted = (result.index >= 0)
                    ? int(train.labels[result.index]) : -1;
                std::cout << "  测试图 " << i
                          << "：真实=" << int(test.labels[i])
                          << "，预测=" << predicted
                          << "，候选=" << result.candidate_count
                          << (predicted == int(test.labels[i]) ? " ✓" : " ✗")
                          << "\n";
            }
        }

        std::cout << "\n========== 结果 ==========\n";
        std::cout << "测试图片数: " << test_limit << "\n";
        std::cout << "正确识别: " << correct << " / " << test_limit << "\n";
        std::cout << "准确率: "
                  << 100.0 * correct / test_limit << "%\n";
        std::cout << "平均候选数: "
                  << double(total_candidates) / test_limit << "\n";
        std::cout << "(候选数越少说明 LSH 筛选越有效)\n";

        // TODO 3（选做）：修改 LshConfig 里的参数试试
        //   - 把 table_count 从 8 改成 16，准确率会怎样？
        //   - 把 bits_per_table 从 8 改成 12，候选数会怎样？
        //   - 把 seed 改成别的数，结果会变吗？为什么？
        //   记录你的实验结果，想想为什么

        // TODO 4（选做）：把 test_limit 从 1000 改成 10000，跑全部测试集

    } catch (const std::exception& e) {
        std::cerr << "出错了: " << e.what() << "\n";
        std::cerr << "提示：如果你在 basic/ 目录下运行，试试 ./lsh_basic ../test/data\n";
        return 1;
    }
    return 0;
}
