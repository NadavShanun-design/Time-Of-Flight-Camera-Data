#include "ply_loader.h"
#include <sstream>
#include <algorithm>
#include <vector>
#include <cstdint>
#include <iostream>
#include <cstring>

struct PropertyInfo {
    std::string type;
    std::string name;
};

PLYLoader::PLYLoader() {
    info = {0, 0, false, 0, 0, 0, 0, 0, 0, ""};
}

PLYLoader::~PLYLoader() {}

bool PLYLoader::loadPLY(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open PLY file: " << filename << std::endl;
        return false;
    }
    std::cout << "[PLYLoader] Opened file: " << filename << std::endl;
    if (!readHeader(file)) {
        std::cerr << "Error: Could not read PLY header" << std::endl;
        return false;
    }
    std::cout << "[PLYLoader] Header parsed. Format: " << info.format << ", numPoints: " << info.numPoints << ", numFaces: " << info.numFaces << std::endl;
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

// Store property info for each element
static std::vector<PropertyInfo> vertexProperties;

bool PLYLoader::readHeader(std::ifstream& file) {
    std::string line;
    std::vector<std::string> headerLines;
    vertexProperties.clear();
    bool inVertexElement = false;
    // Read magic number (skip BOM and whitespace)
    std::getline(file, line);
    // Remove BOM if present
    if (!line.empty() && (unsigned char)line[0] == 0xEF) {
        // UTF-8 BOM: 0xEF 0xBB 0xBF
        if (line.size() >= 3 && (unsigned char)line[1] == 0xBB && (unsigned char)line[2] == 0xBF) {
            line = line.substr(3);
        }
    }
    // Trim whitespace
    line.erase(0, line.find_first_not_of(" \t\r\n"));
    line.erase(line.find_last_not_of(" \t\r\n") + 1);
    if (line != "ply") {
        std::cerr << "Error: Not a valid PLY file (first line: '" << line << "')" << std::endl;
        return false;
    }
    headerLines.push_back(line);
    // Read format
    std::getline(file, line);
    headerLines.push_back(line);
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
        headerLines.push_back(line);
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
                inVertexElement = true;
            } else {
                inVertexElement = false;
                if (elementType == "face") {
                    iss >> info.numFaces;
                }
            }
        } else if (token == "property" && inVertexElement) {
            std::string propType, propName;
            iss >> propType >> propName;
            vertexProperties.push_back({propType, propName});
            if (propName == "red" || propName == "green" || propName == "blue") {
                info.hasColor = true;
            }
        }
    }
    std::cout << "[PLYLoader] Parsed header lines:" << std::endl;
    for (const auto& l : headerLines) std::cout << l << std::endl;
    std::cout << "[PLYLoader] Vertex properties:" << std::endl;
    for (const auto& p : vertexProperties) std::cout << "  " << p.type << " " << p.name << std::endl;
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
    } else if (info.format == "binary_little_endian") {
        std::streampos pos = file.tellg();
        std::cout << "[PLYLoader] File position after header: " << pos << std::endl;
        int propCount = static_cast<int>(vertexProperties.size());
        int xIdx = -1, yIdx = -1, zIdx = -1;
        for (int i = 0; i < propCount; ++i) {
            if (vertexProperties[i].name == "x") xIdx = i;
            if (vertexProperties[i].name == "y") yIdx = i;
            if (vertexProperties[i].name == "z") zIdx = i;
        }
        if (xIdx == -1 || yIdx == -1 || zIdx == -1) {
            std::cerr << "Error: x, y, z properties not found in PLY vertex properties." << std::endl;
            return false;
        }
        for (int i = 0; i < info.numPoints; ++i) {
            std::vector<float> props(propCount);
            for (int j = 0; j < propCount; ++j) {
                if (vertexProperties[j].type == "float" || vertexProperties[j].type == "float32") {
                    float v;
                    file.read(reinterpret_cast<char*>(&v), sizeof(float));
                    props[j] = v;
                } else if (vertexProperties[j].type == "uchar" || vertexProperties[j].type == "uint8") {
                    uint8_t v;
                    file.read(reinterpret_cast<char*>(&v), sizeof(uint8_t));
                } else if (vertexProperties[j].type == "int" || vertexProperties[j].type == "int32") {
                    int32_t v;
                    file.read(reinterpret_cast<char*>(&v), sizeof(int32_t));
                } else {
                    char skip[4];
                    file.read(skip, 4);
                }
            }
            float x = props[xIdx];
            float y = props[yIdx];
            float z = props[zIdx];
            points.emplace_back(x, y, z);
            if (i < 5) std::cout << "[PLYLoader] Vertex " << i << ": " << x << ", " << y << ", " << z << std::endl;
            if (i == 5) std::cout << "..." << std::endl;
            if (i == info.numPoints - 1) std::cout << "[PLYLoader] Last vertex: " << x << ", " << y << ", " << z << std::endl;
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
        std::cerr << "Error: Only ASCII and binary_little_endian PLY supported for now." << std::endl;
        return false;
    }
    std::cout << "[PLYLoader] Loaded " << points.size() << " points." << std::endl;
    return true;
} 