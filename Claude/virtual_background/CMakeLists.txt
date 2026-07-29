cmake_minimum_required(VERSION 3.16)
project(VirtualBackground)

set(CMAKE_CXX_STANDARD 17)

# MediaPipeのインクルードとライブラリ
find_package(OpenCV REQUIRED)

add_executable(virtual_bg virtual_background.cpp)
target_link_libraries(virtual_bg OpenCV::OpenCV_CORE OpenCV::OpenCV_VIDEOIO 
                                 OpenCV::OpenCV_IMGPROC mediapipe)
