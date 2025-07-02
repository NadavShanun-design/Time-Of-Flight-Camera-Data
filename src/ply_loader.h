#pragma once
#include <string>
#include <vector>
#include <fstream>
#include <iostream>

struct Point3D {
    float x, y, z;
    Point3D(float x = 0, float y = 0, float z = 0) : x(x), y(y), z(z) {}
};

struct PLYInfo {
    int numPoints;
    int numFaces;
    bool hasColor;
    float minX, maxX, minY, maxY, minZ, maxZ;
    std::string format; // "ascii", "binary_little_endian", "binary_big_endian"
};

class PLYLoader {
public:
    PLYLoader();
    ~PLYLoader();
    
    bool loadPLY(const std::string& filename);
    bool getPLYInfo(const std::string& filename, PLYInfo& info);
    const std::vector<Point3D>& getPoints() const { return points; }
    const PLYInfo& getInfo() const { return info; }
    
private:
    bool readHeader(std::ifstream& file);
    bool readPoints(std::ifstream& file);
    
    std::vector<Point3D> points;
    PLYInfo info;
}; 