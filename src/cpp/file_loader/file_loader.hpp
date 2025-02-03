#pragma once

#include <string>
#include <vector>
#include <memory>

class FileLoader {
public:
	FileLoader(const std::string& filePath);
	~FileLoader();

	// Read a specific portion of the file
	std::vector<std::string> readLines(size_t start, size_t count);

	// Get total number of lines in file
	size_t getLineCount() const;

	// Check if file has been modified
	bool hasChanged() const;

	// Reload file content if changed
	void reload();

private:
	class Impl;
	std::unique_ptr<Impl> pImpl;
};
