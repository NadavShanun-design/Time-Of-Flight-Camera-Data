cmake_minimum_required(VERSION 3.10)
project(ToFSimulator)
set(CMAKE_CXX_STANDARD 17)

find_package(Qt6 COMPONENTS Widgets REQUIRED)
set(CMAKE_AUTOMOC ON)

add_executable(ToFSimulator 
    src/main.cpp 
    src/mock_star_api.cpp 
    src/tof_data_generator.cpp 
    src/color_map.cpp
    src/ply_loader.cpp
    src/main_window.cpp
    src/tof_raw_packet.cpp
    src/tof_processor.cpp
    src/point_cloud_viewer.cpp
)

target_link_libraries(ToFSimulator Qt6::Widgets) 