#include "mnist.h"

#include <array>
#include <fstream>
#include <stdexcept>

namespace {

// 从文件流里读 4 个字节，拼成大端序 32 位整数
// MNIST 的 IDX 文件头用的是大端序（高位字节在前），
// 而普通 PC 是小端序，所以不能直接读 int，得手动拼。
std::uint32_t read_big_endian_u32(std::ifstream& input) {
    std::array<unsigned char, 4> bytes{};
    input.read(reinterpret_cast<char*>(bytes.data()), bytes.size());
    if (!input) {
        throw std::runtime_error("IDX 文件头读取失败");
    }
    return (std::uint32_t(bytes[0]) << 24) |
           (std::uint32_t(bytes[1]) << 16) |
           (std::uint32_t(bytes[2]) << 8)  |
            std::uint32_t(bytes[3]);
}

}  // namespace

MnistDataset load_mnist(const std::string& image_path,
                        const std::string& label_path) {
    std::ifstream image_file(image_path, std::ios::binary);
    std::ifstream label_file(label_path, std::ios::binary);
    if (!image_file || !label_file) {
        throw std::runtime_error("无法打开 MNIST 文件，请检查路径");
    }

    // 读文件头
    const std::uint32_t image_magic = read_big_endian_u32(image_file);
    const int image_count = int(read_big_endian_u32(image_file));
    const int rows = int(read_big_endian_u32(image_file));
    const int cols = int(read_big_endian_u32(image_file));
    const std::uint32_t label_magic = read_big_endian_u32(label_file);
    const int label_count = int(read_big_endian_u32(label_file));

    // 校验：图片 magic=2051，标签 magic=2049，数量必须一致
    if (image_magic != 2051 || label_magic != 2049 ||
        image_count != label_count) {
        throw std::runtime_error("MNIST 文件格式不正确");
    }

    // 一次性读入全部像素和标签
    const std::size_t pixel_count =
        std::size_t(image_count) * rows * cols;
    std::vector<unsigned char> bytes(pixel_count);
    std::vector<std::uint8_t> labels(label_count);
    image_file.read(reinterpret_cast<char*>(bytes.data()), bytes.size());
    label_file.read(reinterpret_cast<char*>(labels.data()), labels.size());
    if (!image_file || !label_file) {
        throw std::runtime_error("MNIST 文件内容不完整");
    }

    // 把 unsigned char 转成 int16_t（后面做乘法不会溢出）
    MnistDataset dataset;
    dataset.count = image_count;
    dataset.rows = rows;
    dataset.cols = cols;
    dataset.labels = std::move(labels);
    dataset.images.resize(pixel_count);
    for (std::size_t i = 0; i < pixel_count; ++i) {
        dataset.images[i] = bytes[i];
    }
    return dataset;
}
