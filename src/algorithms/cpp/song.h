#pragma once

#include <string>

struct Song {
    std::string name;
    std::string artist;
    int year = 0;
    float danceability = 0.0F;
    float energy = 0.0F;
    float loudness = 0.0F;
};
