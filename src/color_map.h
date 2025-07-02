#pragma once
#include <cstdint>

struct RGB {
    uint8_t r, g, b;
};

// Map a value in [vmin, vmax] to a Jet color
RGB jetColorMap(float value, float vmin, float vmax); 