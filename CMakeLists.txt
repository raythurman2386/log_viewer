cmake_minimum_required(VERSION 3.15)
project(LogViewer)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Include FetchContent
include(FetchContent)

# Fetch pybind11
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11
    GIT_TAG        v2.11.1
)
FetchContent_MakeAvailable(pybind11)

# Add source files
set(SOURCES
    src/cpp/file_loader/file_loader.cpp
    src/cpp/file_loader/file_loader.hpp
    src/cpp/bindings/bindings.cpp
)

# Create the pybind11 module
pybind11_add_module(logviewer_cpp ${SOURCES})

# Include directories
target_include_directories(logviewer_cpp PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/cpp
)
