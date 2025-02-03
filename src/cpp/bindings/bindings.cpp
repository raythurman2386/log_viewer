#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../file_loader/file_loader.hpp"

namespace py = pybind11;

PYBIND11_MODULE(logviewer_cpp, m) {
	m.doc() = "Log Viewer C++ bindings";

	py::class_<FileLoader>(m, "FileLoader")
	.def(py::init<const std::string&>())
	.def("read_lines", &FileLoader::readLines, "Read a specific number of lines from the file")
	.def("get_line_count", &FileLoader::getLineCount, "Get total number of lines in the file")
	.def("has_changed", &FileLoader::hasChanged, "Check if file has been modified")
	.def("reload", &FileLoader::reload, "Reload file content if changed");
}
