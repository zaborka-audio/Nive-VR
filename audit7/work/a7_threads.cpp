// AUDIT 7: idle cost of the EQ coefficient worker threads (4 per FourBandDSP instance).
#include "FourBandDSP.h"
#include <cstdio>
#include <vector>
#include <memory>
#include <thread>
#include <chrono>
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <mmsystem.h>
#pragma comment(lib, "winmm.lib")
static double cpuSeconds() { FILETIME c, e, k, u; GetProcessTimes(GetCurrentProcess(), &c, &e, &k, &u); ULARGE_INTEGER a, b; a.LowPart = k.dwLowDateTime; a.HighPart = k.dwHighDateTime; b.LowPart = u.dwLowDateTime; b.HighPart = u.dwHighDateTime; return (a.QuadPart + b.QuadPart) * 1e-7; }
int main() {
    for (int hires = 0; hires < 2; ++hires) {
        if (hires) timeBeginPeriod(1);      // what most DAWs do
        std::vector<std::unique_ptr<FourBandDSP>> v; EqControls ec{};
        const auto t0 = std::chrono::steady_clock::now();
        for (int i = 0; i < 100; ++i) { v.push_back(std::make_unique<FourBandDSP>()); v.back()->prepare(48000, ec); }
        const double tPrep = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
        const double c0 = cpuSeconds(); std::this_thread::sleep_for(std::chrono::seconds(4)); const double c1 = cpuSeconds();
        std::printf("timer resolution %s: 100 idle EQ instances (400 worker threads): prepare %.0f ms total, idle CPU %.2f %% of one core\n", hires ? "1 ms (timeBeginPeriod)" : "default", 1000 * tPrep, 100 * (c1 - c0) / 4.0);
        const auto t1 = std::chrono::steady_clock::now(); v.clear();
        std::printf("  destroying 100 instances: %.0f ms\n", 1000 * std::chrono::duration<double>(std::chrono::steady_clock::now() - t1).count());
        if (hires) timeEndPeriod(1);
    }
    return 0;
}
