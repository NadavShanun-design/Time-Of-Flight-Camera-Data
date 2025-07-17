#pragma once
#include <vector>
#include <cstdint>
#include <cmath>

// Four-phase raw ToF packet structure
struct ToFRawPacket {
    uint32_t frame_counter;
    uint32_t width;
    uint32_t height;
    // Four phase-shifted frames (I0, I90, I180, I270)
    std::vector<uint16_t> frame_I0;
    std::vector<uint16_t> frame_I90;
    std::vector<uint16_t> frame_I180;
    std::vector<uint16_t> frame_I270;
};

// Generate a synthetic ToF packet simulating a sphere in the center
// Amplitude and phase are encoded as per ToF physics
ToFRawPacket generateFakeToFRawPacket(uint32_t width, uint32_t height, float sphere_radius_m = 0.7f, float sphere_center_z = 1.5f, float amplitude = 2000.0f, float noise_std = 10.0f, uint32_t frame_counter = 0); 