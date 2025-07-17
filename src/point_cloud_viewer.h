#pragma once
#include <QWidget>
#include <QVBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QSlider>
#include <QGroupBox>
#include <QHBoxLayout>
#include <string>
#include "ply_loader.h"

class PointCloudViewer : public QWidget {
    Q_OBJECT

public:
    PointCloudViewer(QWidget *parent = nullptr);
    ~PointCloudViewer();
    
    bool loadPointCloud(const std::string& filename);
    void setPointCloud(const std::vector<Point3D>& points); // New: live update
    void resetView();

private slots:
    void onResetViewClicked();
    void onPointSizeChanged(int value);

private:
    void setupUI();
    void updatePointCloudDisplay();
    
    // UI Components
    QVBoxLayout *mainLayout;
    QLabel *pointCloudLabel;
    QPushButton *resetViewButton;
    QSlider *pointSizeSlider;
    QGroupBox *controlsGroup;
    
    // Point cloud data
    std::string currentPointCloudFile;
    bool hasPointCloud;
    std::vector<Point3D> livePoints;
}; 