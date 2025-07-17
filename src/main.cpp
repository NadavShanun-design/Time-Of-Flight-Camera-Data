#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <iomanip>
#include <thread>
#include <QApplication>
#include "tof_data_generator.h"
#include "color_map.h"
#include "ply_loader.h"
#include "analysis.hpp"
#include "main_window.h"

// Save a color image to PPM format (simple image format)
void savePPM(const std::string& filename, const std::vector<RGB>& pixels, size_t width, size_t height) {
    std::ofstream file(filename, std::ios::binary);
    if (!file) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        return;
    }
    file << "P6\n" << width << " " << height << "\n255\n";
    for (const auto& pixel : pixels) {
        file.write(reinterpret_cast<const char*>(&pixel), 3);
    }
    std::cout << "Saved color-mapped ToF image to " << filename << std::endl;
}

void run_cli_experiment() {
    // Experiment parameters
    const std::vector<float> ranges_to_test = {0.5f, 1.0f, 1.5f, 2.0f, 2.5f, 3.0f, 4.0f, 5.0f};
    const int samples_per_range = 100;
    const size_t num_pixels = 64;
    const float noise_A = 0.001f;
    const float noise_B = 0.005f;

    ToFDataGenerator tofGen;
    tofGen.setNoiseParameters(noise_A, noise_B);

    std::vector<RangeErrorStats> results;
    std::cout << "Running Range Error Characterization...\n";
    std::cout << "--------------------------------------------------\n";
    std::cout << "| True Range (m) | Mean Error (m) | Uncertainty (m) |\n";
    std::cout << "--------------------------------------------------\n";

    // CSV output
    std::ofstream csv("results.csv");
    csv << "true_range_m,mean_error_m,std_dev_m\n";

    for (float d_true : ranges_to_test) {
        RangeMeasurement meas;
        meas.true_distance = d_true;
        for (int i = 0; i < samples_per_range; ++i) {
            std::vector<float> frame = tofGen.generateFrameForTarget(d_true, num_pixels);
            float avg = std::accumulate(frame.begin(), frame.end(), 0.0f) / frame.size();
            meas.measured_distances.push_back(avg);
        }
        RangeErrorStats stats = analyzeMeasurements(meas);
        results.push_back(stats);
        std::cout << "| " << std::fixed << std::setw(13) << std::setprecision(2) << stats.true_distance
                  << " | " << std::setw(14) << std::setprecision(5) << stats.mean_error
                  << " | " << std::setw(15) << std::setprecision(5) << stats.std_dev_error << " |\n";
        csv << stats.true_distance << "," << stats.mean_error << "," << stats.std_dev_error << "\n";
    }
    std::cout << "--------------------------------------------------\n";
    std::cout << "Characterization Complete.\n";
    csv.close();
}

int main(int argc, char *argv[]) {
    // Start CLI experiment in a separate thread
    std::thread cli_thread(run_cli_experiment);

    // Start Qt GUI
    QApplication app(argc, argv);
    MainWindow w;
    w.show();
    int gui_result = app.exec();

    // Wait for CLI thread to finish
    cli_thread.join();
    return gui_result;
} 