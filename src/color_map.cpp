#include "color_map.h"
#include <algorithm>

RGB jetColorMap(float value, float vmin, float vmax) {
    float v = (value - vmin) / (vmax - vmin);
    v = std::max(0.0f, std::min(1.0f, v));
    float r = 0, g = 0, b = 0;
    if (v < 0.25f) {
        r = 0;
        g = 4 * v;
        b = 1;
    } else if (v < 0.5f) {
        r = 0;
        g = 1;
        b = 1 + 4 * (0.25f - v);
    } else if (v < 0.75f) {
        r = 4 * (v - 0.5f);
        g = 1;
        b = 0;
    } else {
        r = 1;
        g = 1 + 4 * (0.75f - v);
        b = 0;
    }
    r = std::max(0.0f, std::min(1.0f, r));
    g = std::max(0.0f, std::min(1.0f, g));
    b = std::max(0.0f, std::min(1.0f, b));
    return RGB{static_cast<uint8_t>(r * 255), static_cast<uint8_t>(g * 255), static_cast<uint8_t>(b * 255)};
} 