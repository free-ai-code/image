cmake_minimum_required(VERSION 3.10)
project(ImageResizerC++ CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# OpenCVパッケージの検索
find_package(OpenCV REQUIRED)

include_directories(${OpenCV_INCLUDE_DIRS})

# 実行ファイルの定義
add_executable(resizer main.cpp)

# OpenCVライブラリのリンク
target_link_libraries(resizer ${OpenCV_LIBS})
