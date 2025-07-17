#include "point_cloud_viewer.h"
#include <QDebug>
#include <QString>

PointCloudViewer::PointCloudViewer(QWidget *parent)
    : QWidget(parent), hasPointCloud(false) {
    setupUI();
}

PointCloudViewer::~PointCloudViewer() {}

void PointCloudViewer::setPointCloud(const std::vector<Point3D>& points) {
    livePoints = points;
    hasPointCloud = !livePoints.empty();
    updatePointCloudDisplay();
}

void PointCloudViewer::updatePointCloudDisplay() {
    if (!livePoints.empty()) {
        pointCloudLabel->setText(QString("<b>Live Point Cloud:</b> %1 points").arg(livePoints.size()));
    } else if (!currentPointCloudFile.empty()) {
        pointCloudLabel->setText(QString("<b>Loaded from file:</b> %1").arg(QString::fromStdString(currentPointCloudFile)));
    } else {
        pointCloudLabel->setText("<b>No point cloud loaded.</b>");
    }
}

void PointCloudViewer::setupUI() {
    mainLayout = new QVBoxLayout(this);
    pointCloudLabel = new QLabel("<b>No point cloud loaded.</b>", this);
    pointCloudLabel->setAlignment(Qt::AlignCenter);
    resetViewButton = new QPushButton("Reset View", this);
    pointSizeSlider = new QSlider(Qt::Horizontal, this);
    pointSizeSlider->setRange(1, 10);
    pointSizeSlider->setValue(3);
    controlsGroup = new QGroupBox("Controls", this);
    QHBoxLayout *controlsLayout = new QHBoxLayout(controlsGroup);
    controlsLayout->addWidget(resetViewButton);
    controlsLayout->addWidget(pointSizeSlider);
    controlsGroup->setLayout(controlsLayout);
    mainLayout->addWidget(pointCloudLabel);
    mainLayout->addWidget(controlsGroup);
    setLayout(mainLayout);
    connect(resetViewButton, &QPushButton::clicked, this, &PointCloudViewer::onResetViewClicked);
    connect(pointSizeSlider, &QSlider::valueChanged, this, &PointCloudViewer::onPointSizeChanged);
}

void PointCloudViewer::resetView() {
    // Placeholder for resetting the 3D view
    qDebug() << "Resetting point cloud view.";
}

void PointCloudViewer::onResetViewClicked() {
    resetView();
}

void PointCloudViewer::onPointSizeChanged(int value) {
    // Placeholder for changing point size in the 3D view
    qDebug() << "Point size changed to" << value;
} 