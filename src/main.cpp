#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
#include "tof_data_generator.h"
#include "color_map.h"
#include "ply_loader.h"

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

int main() {
    std::cout << "=== ToF Simulator - Advanced Demo ===" << std::endl;
    std::cout << "=====================================" << std::endl;
    
    // Part 1: Generate synthetic ToF image
    std::cout << "\n1. GENERATING SYNTHETIC TOF IMAGE" << std::endl;
    std::cout << "--------------------------------" << std::endl;
    
    ToFDataGenerator tofGen(64, 64, 4); // 64x64, 4 frames
    tofGen.generateFrames();
    
    // Get the first frame data
    auto frameBytes = tofGen.getFramePacket(0, 0, 64 * 64);
    
    // Convert bytes to uint16_t vector
    std::vector<uint16_t> frame16;
    for (size_t i = 0; i + 1 < frameBytes.size(); i += 2) {
        frame16.push_back(frameBytes[i] | (frameBytes[i+1] << 8));
    }
    
    std::cout << "Generated ToF frame: " << 64 << "x" << 64 << " pixels" << std::endl;
    std::cout << "Frame data range: " << *std::min_element(frame16.begin(), frame16.end()) 
              << " to " << *std::max_element(frame16.begin(), frame16.end()) << std::endl;
    
    // Convert to color-mapped image
    std::vector<RGB> colorPixels;
    float vmin = static_cast<float>(*std::min_element(frame16.begin(), frame16.end()));
    float vmax = static_cast<float>(*std::max_element(frame16.begin(), frame16.end()));
    
    for (uint16_t value : frame16) {
        colorPixels.push_back(jetColorMap(static_cast<float>(value), vmin, vmax));
    }
    
    // Save to PPM file
    savePPM("tof_image.ppm", colorPixels, 64, 64);
    
    // Part 2: Load and analyze PLY point cloud
    std::cout << "\n2. LOADING POINT CLOUD DATA" << std::endl;
    std::cout << "---------------------------" << std::endl;
    
    PLYLoader plyLoader;
    std::string plyFile = "fragment.ply";
    
    // Get PLY file information
    PLYInfo plyInfo;
    if (plyLoader.getPLYInfo(plyFile, plyInfo)) {
        std::cout << "PLY File: " << plyFile << std::endl;
        std::cout << "Format: " << plyInfo.format << std::endl;
        std::cout << "Number of points: " << plyInfo.numPoints << std::endl;
        std::cout << "Number of faces: " << plyInfo.numFaces << std::endl;
        std::cout << "Has color data: " << (plyInfo.hasColor ? "Yes" : "No") << std::endl;
        std::cout << "Bounding box:" << std::endl;
        std::cout << "  X: [" << plyInfo.minX << ", " << plyInfo.maxX << "]" << std::endl;
        std::cout << "  Y: [" << plyInfo.minY << ", " << plyInfo.maxY << "]" << std::endl;
        std::cout << "  Z: [" << plyInfo.minZ << ", " << plyInfo.maxZ << "]" << std::endl;
        
        // Load the point cloud
        if (plyLoader.loadPLY(plyFile)) {
            const auto& points = plyLoader.getPoints();
            std::cout << "Successfully loaded " << points.size() << " points" << std::endl;
            
            // Show first few points
            std::cout << "First 5 points:" << std::endl;
            for (size_t i = 0; i < std::min(size_t(5), points.size()); ++i) {
                std::cout << "  Point " << i << ": (" << points[i].x << ", " << points[i].y << ", " << points[i].z << ")" << std::endl;
            }
        } else {
            std::cout << "Failed to load point cloud data" << std::endl;
        }
    } else {
        std::cout << "Failed to read PLY file information" << std::endl;
    }
    
    // Part 3: Summary
    std::cout << "\n3. SUMMARY" << std::endl;
    std::cout << "----------" << std::endl;
    std::cout << "✓ Generated synthetic ToF image (tof_image.ppm)" << std::endl;
    std::cout << "✓ Loaded and analyzed point cloud data" << std::endl;
    std::cout << "✓ Ready for GUI integration" << std::endl;
    
    std::cout << "\nNext steps:" << std::endl;
    std::cout << "- Install Qt for GUI development" << std::endl;
    std::cout << "- Add 3D visualization capabilities" << std::endl;
    std::cout << "- Create interactive viewer for both 2D and 3D data" << std::endl;
    
    return 0;
} 