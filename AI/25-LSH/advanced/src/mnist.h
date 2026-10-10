#ifndef MNIST_H
#define MNIST_H

#include <cstdint>
#include <string>
#include <vector>

// MNIST 数据集（训练集或测试集）
struct MnistDataset {
    int count = 0;  // 图片数量
    int rows = 0;   // 每张图几行（28）
    int cols = 0;   // 每张图几列（28）
    std::vector<std::int16_t> images;  // 所有像素，连续存放
    std::vector<std::uint8_t> labels;  // 每张图对应的数字（0~9）
};

// 从 IDX 文件读取 MNIST 数据集
MnistDataset load_mnist(const std::string& image_path,
                        const std::string& label_path);

#endif
