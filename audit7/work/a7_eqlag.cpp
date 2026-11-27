// AUDIT 7: coefficient hand-over of the EQ model (worker thread) - real-time versus offline (faster than real time) rendering.
#include "FourBandDSP.h"
#include <cstdio>
#include <vector>
#include <thread>
#include <chrono>
static const double kPi = 3.14159265358979323846;
int main() {
    const double fs = 48000, f = 5807; const int blk = 256;
    for (int mode = 0; mode < 3; ++mode) {
        EqControls flat{}; EqControls boost{}; boost[3].gain = 1.0;
        FourBandDSP eq; eq.prepare(fs, flat);
        std::vector<float> l(blk); std::vector<double> env; long long i0 = 0;
        const auto t0 = std::chrono::steady_clock::now();
        // 50 ms flat, then the HF gain knob jumps to +max; print the tone amplitude every 256 samples (5.3 ms)
        for (int b = 0; b < 60; ++b) {
            for (int j = 0; j < blk; ++j) l[j] = 0.05f * (float)std::sin(2 * kPi * f * (i0 + j) / fs);
            float* d[1] = {l.data()}; eq.process(d, 1, blk, b < 9 ? flat : boost, true, 0, 0); i0 += blk;
            double pk = 0; for (float v : l) pk = std::max(pk, (double)std::abs(v)); env.push_back(20 * std::log10(pk / 0.05));
            if (mode == 1) std::this_thread::sleep_until(t0 + std::chrono::microseconds((long long)(1e6 * i0 / fs)));   // paced like a live host
            if (mode == 2) std::this_thread::sleep_for(std::chrono::milliseconds(20));                                 // slow host (worker always in time)
        }
        const double wall = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
        std::printf("%s (wall %.3f s for %.3f s of audio)\n  gain at 5.8 kHz per 5.3 ms block after the knob step: ", mode == 0 ? "offline, as fast as possible" : (mode == 1 ? "paced to real time" : "slower than real time"), wall, i0 / fs);
        for (int b = 9; b < 60; ++b) std::printf("%.1f ", env[b]);
        std::printf("\n");
    }
    return 0;
}
