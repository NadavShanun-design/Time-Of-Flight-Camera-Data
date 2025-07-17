#include <QMainWindow>
#include "main_window.h"
#include <QApplication>
#include <QStyleFactory>
#include <QMessageBox>
#include <QFileDialog>
#include <QPixmap>
#include <QImageReader>
#include <QTextEdit>
#include <QSplitter>
#include <QLabel>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QStatusBar>
#include <QToolBar>
#include <QMenuBar>
#include <QAction>
#include <QWidget>
#include <QFileInfo>
#include <QDebug>
#include <QPalette>
#include <QColor>
#include "tof_raw_packet.h"
#include "tof_processor.h"
#include <QTimer>
#include <QTabWidget>
#include <QPushButton>
#include <QTextEdit>
#include <QImage>
#include <QPixmap>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QLabel>
#include <QDebug>
#include <cmath>
#include "color_map.h"
#include "ply_loader.h" // Added for PLYLoader

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    // Set modern Fusion style and dark palette
    QApplication::setStyle(QStyleFactory::create("Fusion"));
    QPalette darkPalette;
    darkPalette.setColor(QPalette::Window, QColor(30, 32, 36));
    darkPalette.setColor(QPalette::WindowText, Qt::white);
    darkPalette.setColor(QPalette::Base, QColor(24, 26, 28));
    darkPalette.setColor(QPalette::AlternateBase, QColor(44, 47, 51));
    darkPalette.setColor(QPalette::ToolTipBase, Qt::white);
    darkPalette.setColor(QPalette::ToolTipText, Qt::white);
    darkPalette.setColor(QPalette::Text, Qt::white);
    darkPalette.setColor(QPalette::Button, QColor(44, 47, 51));
    darkPalette.setColor(QPalette::ButtonText, Qt::white);
    darkPalette.setColor(QPalette::BrightText, Qt::red);
    darkPalette.setColor(QPalette::Highlight, QColor(0, 122, 204));
    darkPalette.setColor(QPalette::HighlightedText, Qt::white);
    QApplication::setPalette(darkPalette);

    setWindowTitle("ToF Simulator - High-Tech GUI");
    resize(1200, 800);

    setupUI();
    setupMenus();
    setupToolbar();
    setupStatusBar();
}

MainWindow::~MainWindow() {}

void MainWindow::setupUI() {
    mainSplitter = new QSplitter(this);
    mainSplitter->setOrientation(Qt::Horizontal);

    // Control panel
    controlPanel = new QWidget(this);
    QVBoxLayout *controlLayout = new QVBoxLayout(controlPanel);
    startButton = new QPushButton("Start Simulation", this);
    stopButton = new QPushButton("Stop Simulation", this);
    fpsLabel = new QLabel("FPS: 0", this);
    controlLayout->addWidget(startButton);
    controlLayout->addWidget(stopButton);
    controlLayout->addWidget(fpsLabel);
    controlLayout->addStretch();
    controlPanel->setLayout(controlLayout);

    // Tabbed view for 2D/3D
    tabWidget = new QTabWidget(this);
    // Depth map tab
    depthMapLabel = new QLabel(this);
    depthMapLabel->setAlignment(Qt::AlignCenter);
    tabWidget->addTab(depthMapLabel, "Depth Map");
    // Amplitude map tab
    amplitudeMapLabel = new QLabel(this);
    amplitudeMapLabel->setAlignment(Qt::AlignCenter);
    tabWidget->addTab(amplitudeMapLabel, "Amplitude Map");
    // 3D point cloud tab
    pointCloudViewer = new PointCloudViewer(this);
    tabWidget->addTab(pointCloudViewer, "3D Point Cloud");

    // Packet log
    packetLog = new QTextEdit(this);
    packetLog->setReadOnly(true);
    packetLog->setMaximumHeight(120);

    // Layout
    QWidget *rightPanel = new QWidget(this);
    QVBoxLayout *rightLayout = new QVBoxLayout(rightPanel);
    rightLayout->addWidget(tabWidget);
    rightLayout->addWidget(packetLog);
    rightPanel->setLayout(rightLayout);

    mainSplitter->addWidget(controlPanel);
    mainSplitter->addWidget(rightPanel);
    mainSplitter->setStretchFactor(0, 0);
    mainSplitter->setStretchFactor(1, 1);
    setCentralWidget(mainSplitter);

    // Simulation defaults
    simTimer = new QTimer(this);
    simFPS = 10;
    simWidth = 64;
    simHeight = 64;
    simNoise = 10.0f;
    simAmplitude = 2000.0f;
    simSphereRadius = 0.7f;
    simSphereCenterZ = 1.5f;
    frameCounter = 0;
    running = false;

    connect(startButton, &QPushButton::clicked, this, &MainWindow::startSimulation);
    connect(stopButton, &QPushButton::clicked, this, &MainWindow::stopSimulation);
    connect(simTimer, &QTimer::timeout, this, &MainWindow::onSimulationTick);
}

void MainWindow::setupMenus() {
    QMenu *fileMenu = menuBar()->addMenu("&File");
    openImageAction = new QAction("Open ToF Image", this);
    openPointCloudAction = new QAction("Open Point Cloud", this);
    generateToFAction = new QAction("Generate Synthetic ToF", this);
    exitAction = new QAction("E&xit", this);
    fileMenu->addAction(openImageAction);
    fileMenu->addAction(openPointCloudAction);
    fileMenu->addAction(generateToFAction);
    fileMenu->addSeparator();
    fileMenu->addAction(exitAction);

    QMenu *helpMenu = menuBar()->addMenu("&Help");
    aboutAction = new QAction("About", this);
    helpMenu->addAction(aboutAction);

    connect(openImageAction, &QAction::triggered, this, &MainWindow::openToFImage);
    connect(openPointCloudAction, &QAction::triggered, this, &MainWindow::openPointCloud);
    connect(generateToFAction, &QAction::triggered, this, &MainWindow::generateSyntheticToF);
    connect(exitAction, &QAction::triggered, this, &QWidget::close);
    connect(aboutAction, &QAction::triggered, this, &MainWindow::about);
}

void MainWindow::setupToolbar() {
    QToolBar *toolbar = addToolBar("Main Toolbar");
    toolbar->setMovable(false);
    toolbar->addAction(openImageAction);
    toolbar->addAction(openPointCloudAction);
    toolbar->addAction(generateToFAction);
    toolbar->addSeparator();
    toolbar->addAction(aboutAction);
    toolbar->setStyleSheet("QToolBar { background: #181a1b; border: none; } QToolButton { color: #0af; font-weight: bold; } QToolButton:hover { background: #222; }");
}

void MainWindow::setupStatusBar() {
    statusBar()->showMessage("Ready");
    statusBar()->setStyleSheet("background: #181a1b; color: #0af; font-weight: bold;");
}

void MainWindow::openToFImage() {
    QString fileName = QFileDialog::getOpenFileName(this, "Open ToF Image", "", "PPM Images (*.ppm);;All Files (*)");
    if (!fileName.isEmpty()) {
        QImage img(fileName);
        if (img.isNull()) {
            QMessageBox::warning(this, "Open Image", "Failed to load image.");
            return;
        }
        // This part of the code was not updated in the new_code, so it remains as is.
        // imageLabel->setPixmap(QPixmap::fromImage(img).scaled(imageLabel->size(), Qt::KeepAspectRatio, Qt::SmoothTransformation));
        statusBar()->showMessage("Loaded ToF image: " + QFileInfo(fileName).fileName());
    }
}

void MainWindow::openPointCloud() {
    QString fileName = QFileDialog::getOpenFileName(this, "Open Point Cloud", "", "PLY Files (*.ply);;All Files (*)");
    if (fileName.isEmpty()) return;

    PLYLoader loader;
    if (!loader.loadPLY(fileName.toStdString())) {
        QMessageBox::warning(this, "Open Point Cloud", "Failed to load PLY file.");
        return;
    }
    const std::vector<Point3D>& points = loader.getPoints();
    if (points.empty()) {
        QMessageBox::warning(this, "Open Point Cloud", "PLY file contains no points.");
        return;
    }
    // Update 3D viewer
    pointCloudViewer->setPointCloud(points);
    statusBar()->showMessage("Loaded point cloud: " + QFileInfo(fileName).fileName());
    // Simulate packet streaming: send points in chunks (e.g., 100 points per packet)
    int packetSize = 100;
    int numPackets = (points.size() + packetSize - 1) / packetSize;
    for (int i = 0; i < numPackets; ++i) {
        int startIdx = i * packetSize;
        int endIdx = std::min<int>(startIdx + packetSize, points.size());
        int count = endIdx - startIdx;
        packetLog->append(QString("Packet %1: %2 points").arg(i + 1).arg(count));
        // Optionally, add a small delay for realism (not blocking UI)
        // QCoreApplication::processEvents();
    }
    packetLog->append(QString("Total points loaded: %1").arg(points.size()));
}

void MainWindow::generateSyntheticToF() {
    QMessageBox::information(this, "Generate Synthetic ToF", "This will generate a synthetic ToF image (feature coming soon).");
}

void MainWindow::about() {
    QMessageBox::about(this, "About ToF Simulator GUI",
        "<b>ToF Simulator</b><br>High-tech, interactive GUI for Time-of-Flight data visualization.<br><br>"
        "<b>Features:</b><ul>"
        "<li>Real-time ToF image loading and visualization</li>"
        "<li>3D point cloud viewer</li>"
        "<li>Modern, clean, high-tech design</li>"
        "<li>Extensible for hardware and new formats</li>"
        "</ul><br>"
        "<i>Built with Qt and C++</i>");
}

void MainWindow::startSimulation() {
    if (!running) {
        simTimer->start(1000 / simFPS);
        running = true;
        fpsLabel->setText(QString("FPS: %1").arg(simFPS));
        packetLog->append("Simulation started.");
    }
}

void MainWindow::stopSimulation() {
    if (running) {
        simTimer->stop();
        running = false;
        packetLog->append("Simulation stopped.");
    }
}

void MainWindow::onSimulationTick() {
    // Generate a new ToFRawPacket
    ToFRawPacket pkt = generateFakeToFRawPacket(simWidth, simHeight, simSphereRadius, simSphereCenterZ, simAmplitude, simNoise, frameCounter++);
    logPacket(pkt);
    // Process packet
    ToFProcessedData data = ToFProcessor::processPacket(pkt);
    // Update 2D views
    update2DViews(data);
    // Update 3D view
    update3DView(data);
}

void MainWindow::update2DViews(const ToFProcessedData& data) {
    // Depth map
    float dmin = 0.0f, dmax = 0.0f;
    for (float d : data.distance_map) {
        if (!std::isnan(d)) {
            if (dmin == 0.0f || d < dmin) dmin = d;
            if (d > dmax) dmax = d;
        }
    }
    QImage depthImg(data.width, data.height, QImage::Format_RGB888);
    for (uint32_t y = 0; y < data.height; ++y) {
        for (uint32_t x = 0; x < data.width; ++x) {
            size_t idx = y * data.width + x;
            float d = data.distance_map[idx];
            RGB color = std::isnan(d) ? RGB{20, 0, 40} : jetColorMap(d, dmin, dmax);
            depthImg.setPixel(x, y, qRgb(color.r, color.g, color.b));
        }
    }
    depthMapLabel->setPixmap(QPixmap::fromImage(depthImg).scaled(depthMapLabel->size(), Qt::KeepAspectRatio, Qt::SmoothTransformation));
    // Amplitude map
    float amin = 0.0f, amax = 0.0f;
    for (float a : data.amplitude_map) {
        if (amin == 0.0f || a < amin) amin = a;
        if (a > amax) amax = a;
    }
    QImage ampImg(data.width, data.height, QImage::Format_RGB888);
    for (uint32_t y = 0; y < data.height; ++y) {
        for (uint32_t x = 0; x < data.width; ++x) {
            size_t idx = y * data.width + x;
            float a = data.amplitude_map[idx];
            uint8_t v = static_cast<uint8_t>(255.0f * (a - amin) / (amax - amin + 1e-6f));
            ampImg.setPixel(x, y, qRgb(v, v, v));
        }
    }
    amplitudeMapLabel->setPixmap(QPixmap::fromImage(ampImg).scaled(amplitudeMapLabel->size(), Qt::KeepAspectRatio, Qt::SmoothTransformation));
}

void MainWindow::update3DView(const ToFProcessedData& data) {
    std::vector<Point3D> points;
    float fx = data.width / 2.0f;
    float fy = data.height / 2.0f;
    float cx = data.width / 2.0f - 0.5f;
    float cy = data.height / 2.0f - 0.5f;
    for (uint32_t y = 0; y < data.height; ++y) {
        for (uint32_t x = 0; x < data.width; ++x) {
            size_t idx = y * data.width + x;
            float d = data.distance_map[idx];
            if (!std::isnan(d)) {
                float Z = d;
                float X = (x - cx) * Z / fx;
                float Y = (y - cy) * Z / fy;
                points.emplace_back(X, Y, Z);
            }
        }
    }
    pointCloudViewer->setPointCloud(points);
}

void MainWindow::logPacket(const ToFRawPacket& pkt) {
    packetLog->append(QString("Frame %1: %2x%3").arg(pkt.frame_counter).arg(pkt.width).arg(pkt.height));
} 