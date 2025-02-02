cmake_minimum_required(VERSION 3.15)
project(LogViewer)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Add pybind11 from the virtual environment
execute_process(
    COMMAND "${Python_EXECUTABLE}" -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
list(APPEND CMAKE_PREFIX_PATH "${PYBIND11_CMAKE_DIR}")
find_package(pybind11 CONFIG REQUIRED)

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
