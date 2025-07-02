#include "tof_data_generator.h"
#include <random>

ToFDataGenerator::ToFDataGenerator(size_t width, size_t height, size_t numFrames)
    : width_(width), height_(height), numFrames_(numFrames) {
    generateFrames();
}

void ToFDataGenerator::generateFrames() {
    frames_.clear();
    std::mt19937 rng(42);
    std::uniform_int_distribution<int> noise(-20, 20);
    for (size_t f = 0; f < numFrames_; ++f) {
        std::vector<uint16_t> frame(width_ * height_);
        for (size_t y = 0; y < height_; ++y) {
            for (size_t x = 0; x < width_; ++x) {
                // Gradient + frame-dependent offset + noise
                int value = (int)(1000 + 10 * x + 5 * y + 100 * f + noise(rng));
                if (value < 0) value = 0;
                if (value > 65535) value = 65535;
                frame[y * width_ + x] = static_cast<uint16_t>(value);
            }
        }
        frames_.push_back(std::move(frame));
    }
}

std::vector<uint8_t> ToFDataGenerator::getFramePacket(size_t frameIdx, size_t offset, size_t length) const {
    std::vector<uint8_t> packet;
    if (frameIdx >= frames_.size()) return packet;
    const auto& frame = frames_[frameIdx];
    size_t end = std::min(offset + length, frame.size());
    for (size_t i = offset; i < end; ++i) {
        uint16_t v = frame[i];
        packet.push_back(static_cast<uint8_t>(v & 0xFF));
        packet.push_back(static_cast<uint8_t>((v >> 8) & 0xFF));
    }
    return packet;
} 