cmake_minimum_required(VERSION 3.10)
project(ToFSimulator)
set(CMAKE_CXX_STANDARD 17)

find_package(Qt5 COMPONENTS Widgets REQUIRED)
set(CMAKE_AUTOMOC ON)

add_executable(ToFSimulator 
    src/main.cpp 
    src/mock_star_api.cpp 
    src/tof_data_generator.cpp 
    src/color_map.cpp
    src/ply_loader.cpp
    src/main_window.cpp
)

target_link_libraries(ToFSimulator Qt5::Widgets) 