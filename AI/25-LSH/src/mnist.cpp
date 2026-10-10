#include "mnist.h"

#include <array>
#include <fstream>
#include <stdexcept>

namespace {

std::uint32_t read_big_endian_u32(std::ifstream& input) {
    std::array<unsigned char, 4> bytes{};
    input.read(reinterpret_cast<char*>(bytes.data()), bytes.size());
    if (!input) {
        throw std::runtime_error("invalid IDX header");
    }
    return (static_cast<std::uint32_t>(bytes[0]) << 24) |
           (static_cast<std::uint32_t>(bytes[1]) << 16) |
           (static_cast<std::uint32_t>(bytes[2]) << 8) |
           static_cast<std::uint32_t>(bytes[3]);
}

}  // namespace

MnistDataset load_mnist(const std::string& image_path,
                        const std::string& label_path) {
    std::ifstream image_file(image_path, std::ios::binary);
    std::ifstream label_file(label_path, std::ios::binary);
    if (!image_file || !label_file) {
        throw std::runtime_error("cannot open MNIST files");
    }

    const std::uint32_t image_magic = read_big_endian_u32(image_file);
    const int image_count = static_cast<int>(read_big_endian_u32(image_file));
    const int rows = static_cast<int>(read_big_endian_u32(image_file));
    const int cols = static_cast<int>(read_big_endian_u32(image_file));
    const std::uint32_t label_magic = read_big_endian_u32(label_file);
    const int label_count = static_cast<int>(read_big_endian_u32(label_file));

    if (image_magic != 2051 || label_magic != 2049 ||
        image_count != label_count) {
        throw std::runtime_error("invalid MNIST files");
    }

    const std::size_t pixel_count =
        static_cast<std::size_t>(image_count) * rows * cols;
    std::vector<unsigned char> bytes(pixel_count);
    std::vector<std::uint8_t> labels(label_count);
    image_file.read(reinterpret_cast<char*>(bytes.data()), bytes.size());
    label_file.read(reinterpret_cast<char*>(labels.data()), labels.size());
    if (!image_file || !label_file) {
        throw std::runtime_error("incomplete MNIST files");
    }

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
