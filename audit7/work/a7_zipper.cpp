// AUDIT 7: block-rate parameter steps (no smoothing) - make-up gain automation, and L/C switch click.
#include "DynamicsCircuit.h"
#include <cstdio>
#include <vector>
static const double kPi = 3.14159265358979323846;
int main() {
    using namespace vrdyn;
    for (int blk : {64, 512, 2048}) {
        DynamicsProcessor p; p.prepare(48000); Controls c; c.lcIn = true; c.cThreshold = 1.0; c.cRatio = 0.5;
        const int n = 48000; std::vector<float> l(n), r(n), ideal(n);
        const double a = 0.05;
        for (int i = 0; i < n; ++i) l[i] = r[i] = (float)(a * std::sin(2 * kPi * 1000 * i / 48000.0));
        for (int i = 0; i < n; ++i) ideal[i] = (float)(l[i] * std::pow(10.0, 30.0 * (0.5 * i / n) / 20.0));      // smooth 0 -> 15 dB in 1 s
        for (int i = 0; i < n; i += blk) { c.cGain = 0.5 * i / n; float* d[2] = {l.data() + i, r.data() + i}; p.process(d, nullptr, 2, std::min(blk, n - i), c); }
        double e = 0, s = 0, maxStep = 0; for (int i = 0; i < n; ++i) { e += ((double)l[i] - ideal[i]) * ((double)l[i] - ideal[i]); s += (double)ideal[i] * ideal[i]; }
        maxStep = 15.0 * blk / n;
        std::printf("make-up automated 0 -> 15 dB in 1 s, host block %4d: gain step %.3f dB every %.1f ms, error (stepped vs smooth) %.1f dB relative to the signal\n", blk, maxStep, 1000.0 * blk / 48000, 10 * std::log10(e / s));
    }
    return 0;
}
