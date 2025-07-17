#pragma once
#include <vector>
#include <cmath>

struct RangeMeasurement {
    float true_distance;
    std::vector<float> measured_distances; // All measurements for a given true distance
};

struct RangeErrorStats {
    float true_distance;
    float mean_error; // Bias
    float std_dev_error; // Uncertainty/Precision
};

inline RangeErrorStats analyzeMeasurements(const RangeMeasurement& data) {
    size_t N = data.measured_distances.size();
    float sum_error = 0.0f;
    for (float d_measured : data.measured_distances) {
        sum_error += (d_measured - data.true_distance);
    }
    float mean_error = (N > 0) ? (sum_error / N) : 0.0f;
    float sum_sq = 0.0f;
    float mean_measured = 0.0f;
    for (float d_measured : data.measured_distances) {
        mean_measured += d_measured;
    }
    mean_measured = (N > 0) ? (mean_measured / N) : 0.0f;
    for (float d_measured : data.measured_distances) {
        float diff = d_measured - mean_measured;
        sum_sq += diff * diff;
    }
    float std_dev = (N > 1) ? std::sqrt(sum_sq / (N - 1)) : 0.0f;
    return RangeErrorStats{data.true_distance, mean_error, std_dev};
} 