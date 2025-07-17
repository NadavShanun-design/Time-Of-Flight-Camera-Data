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

    // Image viewer placeholder
    imageWidget = new QWidget(this);
    QVBoxLayout *imageLayout = new QVBoxLayout(imageWidget);
    imageLabel = new QLabel("<h2 style='color:#0af'>ToF Image Viewer</h2><p>Load a ToF image to view it here.</p>");
    imageLabel->setAlignment(Qt::AlignCenter);
    imageLabel->setStyleSheet("background: #222; border-radius: 10px; padding: 20px; color: #fff;");
    imageLayout->addWidget(imageLabel);
    imageWidget->setLayout(imageLayout);

    // 3D Point cloud viewer placeholder
    pointCloudWidget = new QWidget(this);
    QVBoxLayout *cloudLayout = new QVBoxLayout(pointCloudWidget);
    QLabel *cloudLabel = new QLabel("<h2 style='color:#fa0'>3D Point Cloud Viewer</h2><p>Load a PLY file to view the 3D model here.</p>");
    cloudLabel->setAlignment(Qt::AlignCenter);
    cloudLabel->setStyleSheet("background: #222; border-radius: 10px; padding: 20px; color: #fff;");
    cloudLayout->addWidget(cloudLabel);
    pointCloudWidget->setLayout(cloudLayout);

    mainSplitter->addWidget(imageWidget);
    mainSplitter->addWidget(pointCloudWidget);
    mainSplitter->setStretchFactor(0, 1);
    mainSplitter->setStretchFactor(1, 1);
    setCentralWidget(mainSplitter);
}

void MainWindow::setupMenus() {
    QMenu *fileMenu = menuBar()->addMenu("&File");
    openImageAction = new QAction("Open ToF Image...", this);
    openPointCloudAction = new QAction("Open Point Cloud...", this);
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
        imageLabel->setPixmap(QPixmap::fromImage(img).scaled(imageLabel->size(), Qt::KeepAspectRatio, Qt::SmoothTransformation));
        statusBar()->showMessage("Loaded ToF image: " + QFileInfo(fileName).fileName());
    }
}

void MainWindow::openPointCloud() {
    QString fileName = QFileDialog::getOpenFileName(this, "Open Point Cloud", "", "PLY Files (*.ply);;All Files (*)");
    if (!fileName.isEmpty()) {
        // Placeholder: Show file name in the 3D viewer
        QLabel *cloudLabel = pointCloudWidget->findChild<QLabel *>();
        if (cloudLabel) {
            cloudLabel->setText("<h2 style='color:#fa0'>3D Point Cloud Viewer</h2><p>Loaded: " + QFileInfo(fileName).fileName() + "</p>");
        }
        statusBar()->showMessage("Loaded point cloud: " + QFileInfo(fileName).fileName());
    }
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