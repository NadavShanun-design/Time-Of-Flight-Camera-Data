cmake_minimum_required(VERSION 3.10)
project(ToFSimulator)
set(CMAKE_CXX_STANDARD 17)

add_executable(ToFSimulator 
    src/main.cpp 
    src/mock_star_api.cpp 
    src/tof_data_generator.cpp 
    src/color_map.cpp
    src/ply_loader.cpp
) 