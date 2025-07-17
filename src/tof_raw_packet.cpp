#include "tof_raw_packet.h"
#include <random>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#ifndef M_PI_2
#define M_PI_2 1.57079632679489661923
#endif

ToFRawPacket generateFakeToFRawPacket(uint32_t width, uint32_t height, float sphere_radius_m, float sphere_center_z, float amplitude, float noise_std, uint32_t frame_counter) {
    ToFRawPacket pkt;
    pkt.frame_counter = frame_counter;
    pkt.width = width;
    pkt.height = height;
    size_t num_pixels = width * height;
    pkt.frame_I0.resize(num_pixels);
    pkt.frame_I90.resize(num_pixels);
    pkt.frame_I180.resize(num_pixels);
    pkt.frame_I270.resize(num_pixels);

    // Camera intrinsics (assume square pixels, center principal point)
    float fx = width / 2.0f;
    float fy = height / 2.0f;
    float cx = width / 2.0f - 0.5f;
    float cy = height / 2.0f - 0.5f;
    float unambiguous_range_m = 15.0f;

    std::random_device rd;
    std::mt19937 rng(rd());
    std::normal_distribution<float> noise_dist(0.0f, noise_std);

    for (uint32_t y = 0; y < height; ++y) {
        for (uint32_t x = 0; x < width; ++x) {
            size_t idx = y * width + x;
            // Project pixel to 3D (simulate a sphere in front of camera)
            float px = (x - cx) / fx;
            float py = (y - cy) / fy;
            float r2 = px * px + py * py;
            float d = -1.0f;
            float A = amplitude;
            // Sphere equation: (X^2 + Y^2 + (Z - center_z)^2) = r^2
            float under_sqrt = sphere_radius_m * sphere_radius_m - (px * sphere_radius_m) * (px * sphere_radius_m) - (py * sphere_radius_m) * (py * sphere_radius_m);
            if (under_sqrt > 0) {
                float z = sphere_center_z - std::sqrt(under_sqrt);
                d = std::sqrt((px * sphere_radius_m) * (px * sphere_radius_m) + (py * sphere_radius_m) * (py * sphere_radius_m) + (z - sphere_center_z) * (z - sphere_center_z));
                d += noise_dist(rng) * 0.001f; // Add small noise in meters
                A = amplitude;
            } else {
                // Background: flat plane at sphere_center_z + radius
                d = sphere_center_z + sphere_radius_m + noise_dist(rng) * 0.001f;
                A = amplitude * 0.2f;
            }
            // Phase encoding
            float phase = (d / unambiguous_range_m) * 2.0f * static_cast<float>(M_PI);
            // Clamp phase to [0, 2pi]
            while (phase < 0) phase += 2.0f * static_cast<float>(M_PI);
            while (phase > 2.0f * static_cast<float>(M_PI)) phase -= 2.0f * static_cast<float>(M_PI);
            // Four phase-shifted measurements
            float I0   = A / 2.0f * std::cos(phase) + A / 2.0f;
            float I90  = A / 2.0f * std::cos(phase - static_cast<float>(M_PI_2)) + A / 2.0f;
            float I180 = A / 2.0f * std::cos(phase - static_cast<float>(M_PI)) + A / 2.0f;
            float I270 = A / 2.0f * std::cos(phase - 3.0f * static_cast<float>(M_PI_2)) + A / 2.0f;
            // Add noise to each
            I0   += noise_dist(rng);
            I90  += noise_dist(rng);
            I180 += noise_dist(rng);
            I270 += noise_dist(rng);
            // Clamp to 16-bit
            pkt.frame_I0[idx]   = static_cast<uint16_t>(std::max(0.0f, std::min(65535.0f, I0)));
            pkt.frame_I90[idx]  = static_cast<uint16_t>(std::max(0.0f, std::min(65535.0f, I90)));
            pkt.frame_I180[idx] = static_cast<uint16_t>(std::max(0.0f, std::min(65535.0f, I180)));
            pkt.frame_I270[idx] = static_cast<uint16_t>(std::max(0.0f, std::min(65535.0f, I270)));
        }
    }
    return pkt;
} 