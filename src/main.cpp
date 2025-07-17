#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
#include "tof_data_generator.h"
#include "color_map.h"
#include "ply_loader.h"
#include <QApplication>
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

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    MainWindow w;
    w.show();
    return app.exec();
} 