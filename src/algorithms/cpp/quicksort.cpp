#include <chrono>
#include <fstream>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

#include "song.h"

std::vector<Song> load_datafile() {
    std::vector<Song> songs;
    std::ifstream file("data.csv");

    if (!file.is_open()) {
        std::cout << "error" << std::endl;
        return songs;
    }

    std::string line;
    std::getline(file, line);

    while (std::getline(file, line)) {
        Song temp;
        std::string field;
        std::vector<std::string> tokens;
        bool quotes = false;

        for (char ch : line) {
            if (ch == '"') {
                quotes = !quotes;
            } else if (ch == ',' && !quotes) {
                tokens.push_back(field);
                field.clear();
            } else {
                field += ch;
            }
        }

        tokens.push_back(field);
        if (tokens.size() < 12) {
            continue;
        }

        temp.name = tokens[1];
        temp.artist = tokens[2];
        temp.year = std::stoi(tokens[5]);
        temp.danceability = std::stof(tokens[7]);
        temp.energy = std::stof(tokens[8]);
        temp.loudness = std::stof(tokens[11]);
        songs.push_back(temp);
    }

    return songs;
}

int partition_danceability(std::vector<Song>& songs, int high, int low) {
    const int middle = low + (high - low) / 2;
    std::swap(songs[middle], songs[high]);
    const Song pivot = songs[high];
    int right = high - 1;
    int left = low;

    while (true) {
        while (left <= right && songs[left].danceability < pivot.danceability) {
            left += 1;
        }
        while (right >= left && songs[right].danceability > pivot.danceability) {
            right -= 1;
        }
        if (left >= right) {
            break;
        }
        std::swap(songs[left], songs[right]);
        left += 1;
        right -= 1;
    }

    std::swap(songs[left], songs[high]);
    return left;
}

int partition_energy(std::vector<Song>& songs, int high, int low) {
    const int middle = low + (high - low) / 2;
    std::swap(songs[middle], songs[high]);
    const Song pivot = songs[high];
    int right = high - 1;
    int left = low;

    while (true) {
        while (left <= right && songs[left].energy < pivot.energy) {
            left += 1;
        }
        while (right >= left && songs[right].energy > pivot.energy) {
            right -= 1;
        }
        if (left >= right) {
            break;
        }
        std::swap(songs[left], songs[right]);
        left += 1;
        right -= 1;
    }

    std::swap(songs[left], songs[high]);
    return left;
}

int partition_loudness(std::vector<Song>& songs, int high, int low) {
    const int middle = low + (high - low) / 2;
    std::swap(songs[middle], songs[high]);
    const Song pivot = songs[high];
    int right = high - 1;
    int left = low;

    while (true) {
        while (left <= right && songs[left].loudness < pivot.loudness) {
            left += 1;
        }
        while (right >= left && songs[right].loudness > pivot.loudness) {
            right -= 1;
        }
        if (left >= right) {
            break;
        }
        std::swap(songs[left], songs[right]);
        left += 1;
        right -= 1;
    }

    std::swap(songs[left], songs[high]);
    return left;
}

void quick_sort(std::vector<Song>& songs, const std::string& feature, int high, int low) {
    if (low >= high) {
        return;
    }

    int partition_index = 0;
    if (feature == "danceability") {
        partition_index = partition_danceability(songs, high, low);
    } else if (feature == "energy") {
        partition_index = partition_energy(songs, high, low);
    } else {
        partition_index = partition_loudness(songs, high, low);
    }

    quick_sort(songs, feature, partition_index - 1, low);
    quick_sort(songs, feature, high, partition_index + 1);
}

int main() {
    std::vector<Song> songs = load_datafile();
    const std::string feature = "danceability";

    auto start = std::chrono::high_resolution_clock::now();
    quick_sort(songs, feature, static_cast<int>(songs.size()) - 1, 0);
    auto stop = std::chrono::high_resolution_clock::now();

    const auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start);
    std::cout << "Time elapsed: " << elapsed.count() << " ms" << std::endl;
    return 0;
}
