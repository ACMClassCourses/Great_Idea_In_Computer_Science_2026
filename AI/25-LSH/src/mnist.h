#ifndef MNIST_H
#define MNIST_H

#include <cstdint>
#include <string>
#include <vector>

struct MnistDataset {
    int count = 0;
    int rows = 0;
    int cols = 0;
    std::vector<std::int16_t> images;
    std::vector<std::uint8_t> labels;
};

MnistDataset load_mnist(const std::string& image_path,
                        const std::string& label_path);

#endif
