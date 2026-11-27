// AUDIT 7: cost of one EQ coefficient set and state sizes.
#include "LFModel.h"
#include "CircuitModel.h"
#include <cstdio>
#include <chrono>
int main() {
    for (int band = 0; band < 4; ++band) {
        const int reps = 2000; volatile double sink = 0; int count = 0;
        const auto t0 = std::chrono::steady_clock::now();
        for (int i = 0; i < reps; ++i) { auto c = lf::Network(0.3 + 1e-4 * i, 0.4, false, false, band, 0.5).discrete(48000, 1000.0); sink = sink + c.direct; count = c.count; }
        const double us = 1e6 * std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count() / reps;
        std::printf("band %d: %d capacitor states, one coefficient set %.1f us (x%d modes per update)\n", band, count, us, (band == 1 || band == 2) ? 1 : 3);
    }
    std::printf("sizeof(lf::Coefficients) = %zu bytes, sizeof(lf::Network) = %zu bytes (stack)\n", sizeof(lf::Coefficients), sizeof(lf::Network));
    return 0;
}
