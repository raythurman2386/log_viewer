#include "file_loader.hpp"
#include <fstream>
#include <sys/stat.h>
#include <memory>
#include <stdexcept>

#ifdef _WIN32
#include <windows.h>
#endif

class FileLoader::Impl {
public:
	Impl(const std::string& filePath) : filePath(filePath) {
		updateFileInfo();
	}

	std::vector<std::string> readLines(size_t start, size_t count) {
		std::vector<std::string> lines;
		std::ifstream file(filePath);

		if (!file.is_open()) {
			throw std::runtime_error("Could not open file: " + filePath);
		}

		file.seekg(std::ios::beg);
		std::string line;
		size_t currentLine = 0;

		while (currentLine < start && std::getline(file, line)) {
			++currentLine;
		}

		while (count-- > 0 && std::getline(file, line)) {
			lines.push_back(line);
		}

		return lines;
	}


	size_t getLineCount(bool forceUpdate = false) {
		if (forceUpdate) {
			updateFileInfo();
		}
		return lineCount;
	}


	bool hasChanged() const {
#ifdef _WIN32
		struct _stat64 currentStat;
		if (_stat64(filePath.c_str(), &currentStat) != 0) {
			return true; // File is inaccessible, assume changed
		}
#else
		struct stat currentStat;
		if (stat(filePath.c_str(), &currentStat) != 0) {
			return true; // File is inaccessible, assume changed
		}
#endif
		return currentStat.st_mtime != lastModified;
	}

	void reload() {
		updateFileInfo();
	}

private:
	std::string filePath;
	time_t lastModified;
	size_t lineCount;

	void updateFileInfo() {
#ifdef _WIN32
		struct _stat64 fileStat;
		if (_stat64(filePath.c_str(), &fileStat) != 0) {
			throw std::runtime_error("Could not stat file: " + filePath);
		}
#else
		struct stat fileStat;
		if (stat(filePath.c_str(), &fileStat) != 0) {
			throw std::runtime_error("Could not stat file: " + filePath);
		}
#endif

		std::ifstream file(filePath);
		if (!file) {
			throw std::runtime_error("Could not open file: " + filePath);
		}

		time_t newModified = fileStat.st_mtime;
		size_t newLineCount = 0;
		std::string line;

		while (std::getline(file, line)) {
			++newLineCount;
		}

		lastModified = newModified;
		lineCount = newLineCount;
	}
};

FileLoader::FileLoader(const std::string& filePath) : pImpl(std::make_unique<Impl>(filePath)) {}

FileLoader::~FileLoader() = default;

std::vector<std::string> FileLoader::readLines(size_t start, size_t count) {
	return pImpl->readLines(start, count);
}

size_t FileLoader::getLineCount() const {
	return pImpl->getLineCount();
}

bool FileLoader::hasChanged() const {
	return pImpl->hasChanged();
}

void FileLoader::reload() {
	pImpl->reload();
}
