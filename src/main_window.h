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

private:
    void setupUI();
    void setupMenus();
    void setupToolbar();
    void setupStatusBar();

    // UI Components
    QSplitter *mainSplitter;
    QLabel *imageLabel;
    PointCloudViewer *pointCloudViewer;
    QWidget *imageWidget;
    QWidget *pointCloudWidget;
    
    // Actions
    QAction *openImageAction;
    QAction *openPointCloudAction;
    QAction *generateToFAction;
    QAction *exitAction;
    QAction *aboutAction;
}; 