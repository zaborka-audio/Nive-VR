// AUDIT 7: HF behaviour of the EQ model versus sample rate (bilinear cramping), and low-rate stability.
#include "FourBandDSP.h"
#include <cstdio>
#include <vector>
static const double kPi = 3.14159265358979323846;
static double tone(const std::vector<double>& x, double fs, double f) {
    double re = 0, im = 0, wsum = 0; const size_t n = x.size();
    for (size_t i = 0; i < n; ++i) { const double w = 0.5 - 0.5 * std::cos(2 * kPi * i / (n - 1)); re += w * x[i] * std::cos(2 * kPi * f * i / fs); im -= w * x[i] * std::sin(2 * kPi * f * i / fs); wsum += w; }
    return 2.0 * std::sqrt(re * re + im * im) / wsum;
}
int main() {
    const double freqs[] = {1000, 3000, 5800, 8000, 10000, 12000, 15000, 18000, 20000};
    auto resp = [&](double fs, const EqControls& ec, const char* name) {
        std::printf("  fs %6.0f %-28s", fs, name);
        for (double f : freqs) {
            if (f > 0.46 * fs) { std::printf("    --  "); continue; }
            FourBandDSP eq; eq.prepare(fs, ec); const int n = (int)(0.25 * fs); std::vector<float> l(n); for (int i = 0; i < n; ++i) l[i] = 0.05f * (float)std::sin(2 * kPi * f * i / fs);
            float* d[1] = {l.data()}; eq.process(d, 1, n, ec, true, 0, 0);
            std::vector<double> x(l.begin() + (int)(0.15 * fs), l.end()); bool bad = false; double mx = 0; for (double v : x) { if (!std::isfinite(v)) bad = true; mx = std::max(mx, std::abs(v)); }
            if (bad) std::printf("   NaN  "); else std::printf(" %+6.2f ", 20 * std::log10(tone(x, fs, f) / 0.05));
        }
        std::printf("\n");
    };
    std::printf("  %-40s", "freq Hz:"); for (double f : freqs) std::printf(" %6.0f ", f); std::printf("\n");
    EqControls hfb{}; hfb[3].gain = 1.0;                          // HF bell, mid frequency (5.8 kHz), +max
    EqControls hfc{}; hfc[3].gain = 0.0;
    EqControls hfq{}; hfq[3].gain = 1.0; hfq[3].hiq = true;
    EqControls hfs{}; hfs[3].gain = 1.0; hfs[3].shelf = true;
    EqControls hmf{}; hmf[2].gain = 1.0; hmf[2].position = 1.0; hmf[2].q = 0.0;      // HMF 8.7 kHz broad
    EqControls hf12{}; hf12[3].gain = 0.75; hf12[3].position = 0.85;                  // HF ~12 kHz +9 dB
    for (double fs : {44100.0, 48000.0, 88200.0, 96000.0, 192000.0, 384000.0}) resp(fs, hfb, "HF bell 5.8k +max");
    for (double fs : {48000.0, 96000.0, 384000.0}) resp(fs, hfc, "HF bell 5.8k -max");
    for (double fs : {48000.0, 96000.0, 384000.0}) resp(fs, hfq, "HF bell 5.8k +max Hi-Q");
    for (double fs : {48000.0, 96000.0, 384000.0}) resp(fs, hfs, "HF shelf 5.8k +max");
    for (double fs : {48000.0, 96000.0, 384000.0}) resp(fs, hmf, "HMF 8.7k +max Q pot 0");
    for (double fs : {48000.0, 96000.0, 384000.0}) resp(fs, hf12, "HF pos .85 gain .75");
    // low-rate behaviour: peak output with HF frequency swept
    std::printf("\n  low sample rates, HF +max, 1 kHz 0.05 input: max |output| in 0.25 s\n");
    for (double fs : {22050.0, 32000.0, 44100.0}) for (double pos : {0.5, 0.8, 0.9, 0.95, 1.0}) {
        EqControls e{}; e[3].gain = 1.0; e[3].position = pos; FourBandDSP eq; eq.prepare(fs, e); const int n = (int)(0.25 * fs); std::vector<float> l(n);
        for (int i = 0; i < n; ++i) l[i] = 0.05f * (float)std::sin(2 * kPi * 1000 * i / fs);
        float* d[1] = {l.data()}; eq.process(d, 1, n, e, true, 0, 0); double mx = 0; int bad = 0; for (float v : l) { if (!std::isfinite(v)) ++bad; else mx = std::max(mx, (double)std::abs(v)); }
        std::printf("    fs %6.0f HF pos %.2f (%.0f Hz): max %.3g, non-finite samples %d\n", fs, pos, circuit::frequency(pos) * 47.0, mx, bad);
    }
    return 0;
}
