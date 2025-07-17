#pragma once
#include <vector>
#include <cstdint>
#include <cmath>
#include "tof_raw_packet.h"

struct ToFProcessedData {
    uint32_t width;
    uint32_t height;
    std::vector<float> distance_map; // meters
    std::vector<float> amplitude_map; // arbitrary units
};

class ToFProcessor {
public:
    // Process a ToFRawPacket into amplitude and distance maps
    // If amplitude < threshold, set distance to NAN
    static ToFProcessedData processPacket(const ToFRawPacket& packet, float amplitude_threshold = 100.0f, float unambiguous_range_m = 15.0f);
}; 