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

        // Skip lines until start
        std::string line;
        for (size_t i = 0; i < start; ++i) {
            if (!std::getline(file, line)) {
                return lines;
            }
        }

        // Read requested lines
        for (size_t i = 0; i < count; ++i) {
            if (!std::getline(file, line)) {
                break;
            }
            lines.push_back(line);
        }

        return lines;
    }

    size_t getLineCount() const {
        return lineCount;
    }

    bool hasChanged() const {
        struct stat currentStat;
        if (stat(filePath.c_str(), &currentStat) != 0) {
            return false;
        }
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
        struct stat fileStat;
        if (stat(filePath.c_str(), &fileStat) != 0) {
            throw std::runtime_error("Could not stat file: " + filePath);
        }
        lastModified = fileStat.st_mtime;

        // Count lines
        std::ifstream file(filePath);
        if (!file.is_open()) {
            throw std::runtime_error("Could not open file: " + filePath);
        }

        lineCount = 0;
        std::string line;
        while (std::getline(file, line)) {
            ++lineCount;
        }
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
