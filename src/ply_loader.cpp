#include "ply_loader.h"
#include <sstream>
#include <algorithm>

PLYLoader::PLYLoader() {
    info = {0, 0, false, 0, 0, 0, 0, 0, 0, ""};
}

PLYLoader::~PLYLoader() {
}

bool PLYLoader::loadPLY(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open PLY file: " << filename << std::endl;
        return false;
    }
    
    if (!readHeader(file)) {
        std::cerr << "Error: Could not read PLY header" << std::endl;
        return false;
    }
    
    if (!readPoints(file)) {
        std::cerr << "Error: Could not read PLY points" << std::endl;
        return false;
    }
    
    file.close();
    return true;
}

bool PLYLoader::getPLYInfo(const std::string& filename, PLYInfo& info) {
    std::ifstream file(filename, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open PLY file: " << filename << std::endl;
        return false;
    }
    
    if (!readHeader(file)) {
        std::cerr << "Error: Could not read PLY header" << std::endl;
        return false;
    }
    
    info = this->info;
    file.close();
    return true;
}

bool PLYLoader::readHeader(std::ifstream& file) {
    std::string line;
    
    // Read magic number
    std::getline(file, line);
    if (line != "ply") {
        std::cerr << "Error: Not a valid PLY file" << std::endl;
        return false;
    }
    
    // Read format
    std::getline(file, line);
    if (line.find("format ascii") != std::string::npos) {
        info.format = "ascii";
    } else if (line.find("format binary_little_endian") != std::string::npos) {
        info.format = "binary_little_endian";
    } else if (line.find("format binary_big_endian") != std::string::npos) {
        info.format = "binary_big_endian";
    } else {
        std::cerr << "Error: Unsupported PLY format" << std::endl;
        return false;
    }
    
    // Read header until end_header
    while (std::getline(file, line)) {
        if (line == "end_header") {
            break;
        }
        
        std::istringstream iss(line);
        std::string token;
        iss >> token;
        
        if (token == "element") {
            std::string elementType;
            iss >> elementType;
            if (elementType == "vertex") {
                iss >> info.numPoints;
            } else if (elementType == "face") {
                iss >> info.numFaces;
            }
        } else if (token == "property") {
            std::string propType, propName;
            iss >> propType >> propName;
            if (propName == "red" || propName == "green" || propName == "blue") {
                info.hasColor = true;
            }
        }
    }
    
    return true;
}

bool PLYLoader::readPoints(std::ifstream& file) {
    points.clear();
    points.reserve(info.numPoints);
    
    if (info.format == "ascii") {
        // Read ASCII format
        for (int i = 0; i < info.numPoints; ++i) {
            float x, y, z;
            file >> x >> y >> z;
            points.emplace_back(x, y, z);
            
            // Update bounding box
            if (i == 0) {
                info.minX = info.maxX = x;
                info.minY = info.maxY = y;
                info.minZ = info.maxZ = z;
            } else {
                info.minX = std::min(info.minX, x);
                info.maxX = std::max(info.maxX, x);
                info.minY = std::min(info.minY, y);
                info.maxY = std::max(info.maxY, y);
                info.minZ = std::min(info.minZ, z);
                info.maxZ = std::max(info.maxZ, z);
            }
        }
    } else {
        // For binary format, just read a few points for demo
        std::cout << "Binary PLY format detected. Reading first 1000 points for demo..." << std::endl;
        int pointsToRead = std::min(1000, info.numPoints);
        
        for (int i = 0; i < pointsToRead; ++i) {
            float x, y, z;
            file.read(reinterpret_cast<char*>(&x), sizeof(float));
            file.read(reinterpret_cast<char*>(&y), sizeof(float));
            file.read(reinterpret_cast<char*>(&z), sizeof(float));
            points.emplace_back(x, y, z);
            
            // Update bounding box
            if (i == 0) {
                info.minX = info.maxX = x;
                info.minY = info.maxY = y;
                info.minZ = info.maxZ = z;
            } else {
                info.minX = std::min(info.minX, x);
                info.maxX = std::max(info.maxX, x);
                info.minY = std::min(info.minY, y);
                info.maxY = std::max(info.maxY, y);
                info.minZ = std::min(info.minZ, z);
                info.maxZ = std::max(info.maxZ, z);
            }
        }
    }
    
    return true;
} 