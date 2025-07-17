#pragma once
#include <vector>
#include <cstdint>

class ToFDataGenerator {
public:
    ToFDataGenerator(size_t width = 32, size_t height = 32, size_t numFrames = 4);
    // Generate synthetic ToF frames (distance values)
    void generateFrames();
    // Get a chunk of a frame as bytes (for packet simulation)
    std::vector<uint8_t> getFramePacket(size_t frameIdx, size_t offset, size_t length) const;
    // New: Generate a frame for a flat target at a given distance with realistic noise
    std::vector<float> generateFrameForTarget(float true_distance_meters, size_t num_pixels) const;
    // Noise parameters
    void setNoiseParameters(float A, float B);
    // Getters
    size_t getWidth() const { return width_; }
    size_t getHeight() const { return height_; }
    size_t getNumFrames() const { return numFrames_; }
private:
    size_t width_, height_, numFrames_;
    std::vector<std::vector<uint16_t>> frames_; // [frame][pixel]
    // Noise model parameters
    float noise_A_ = 0.001f;
    float noise_B_ = 0.005f;
}; 