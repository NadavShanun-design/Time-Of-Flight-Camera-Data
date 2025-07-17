#pragma once
#include <QMainWindow>
#include <QAction>
#include <QMenuBar>
#include <QToolBar>
#include <QStatusBar>
#include <QSplitter>
#include <QLabel>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QWidget>
#include <QFileDialog>
#include <QMessageBox>
#include "point_cloud_viewer.h"
#include <QTimer>
#include <QTabWidget>
#include <QImage>
#include <QTextEdit>
#include "tof_raw_packet.h"
#include "tof_processor.h"

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void openToFImage();
    void openPointCloud();
    void generateSyntheticToF();
    void about();
    void startSimulation();
    void stopSimulation();
    void onSimulationTick();

private:
    void setupUI();
    void setupMenus();
    void setupToolbar();
    void setupStatusBar();
    void update2DViews(const ToFProcessedData& data);
    void update3DView(const ToFProcessedData& data);
    void logPacket(const ToFRawPacket& pkt);

    // UI Components
    QSplitter *mainSplitter;
    QTabWidget *tabWidget;
    QLabel *depthMapLabel;
    QLabel *amplitudeMapLabel;
    QWidget *imageWidget;
    QWidget *pointCloudWidget;
    PointCloudViewer *pointCloudViewer;
    QTextEdit *packetLog;
    QWidget *controlPanel;
    QPushButton *startButton;
    QPushButton *stopButton;
    QLabel *fpsLabel;

    // Simulation
    QTimer *simTimer;
    int simFPS;
    uint32_t frameCounter;
    uint32_t simWidth, simHeight;
    float simNoise;
    float simAmplitude;
    float simSphereRadius;
    float simSphereCenterZ;
    bool running;

    QAction *openImageAction;
    QAction *openPointCloudAction;
    QAction *generateToFAction;
    QAction *exitAction;
    QAction *aboutAction;
}; 