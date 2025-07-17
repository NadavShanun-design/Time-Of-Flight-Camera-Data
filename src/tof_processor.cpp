#include "tof_processor.h"
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

ToFProcessedData ToFProcessor::processPacket(const ToFRawPacket& packet, float amplitude_threshold, float unambiguous_range_m) {
    ToFProcessedData out;
    out.width = packet.width;
    out.height = packet.height;
    size_t num_pixels = packet.width * packet.height;
    out.distance_map.resize(num_pixels);
    out.amplitude_map.resize(num_pixels);
    for (size_t i = 0; i < num_pixels; ++i) {
        float I0 = static_cast<float>(packet.frame_I0[i]);
        float I90 = static_cast<float>(packet.frame_I90[i]);
        float I180 = static_cast<float>(packet.frame_I180[i]);
        float I270 = static_cast<float>(packet.frame_I270[i]);
        // Amplitude calculation
        float amp = 0.5f * std::sqrt((I270 - I90) * (I270 - I90) + (I180 - I0) * (I180 - I0));
        out.amplitude_map[i] = amp;
        // Phase calculation
        float phase = std::atan2(I90 - I270, I0 - I180);
        // Distance calculation
        float d = (phase / (2.0f * static_cast<float>(M_PI))) * unambiguous_range_m;
        if (d < 0) d += unambiguous_range_m; // wrap negative phase
        // Mark invalid if amplitude too low
        if (amp < amplitude_threshold) {
            out.distance_map[i] = NAN;
        } else {
            out.distance_map[i] = d;
        }
    }
    return out;
} 