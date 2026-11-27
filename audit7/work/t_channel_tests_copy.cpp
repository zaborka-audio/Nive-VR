// Model-level checks of the channel routing (no JUCE): EQ and dynamics models from the sibling projects.
#include <cstdio>
#include <cmath>
#include <vector>
#include "FourBandDSP.h"
#include "DynamicsCircuit.h"

static int failures = 0;
static void check(bool ok, const char* what) { std::printf("%s  %s\n", ok ? "PASS" : "FAIL", what); if (!ok) ++failures; }
static constexpr double fs = 48000, kPi = 3.14159265358979323846;

// Steady output level (dBu) of a sine through: dynamics with the EQ either in the path or in the side chain.
static double run(double freq, double dbu, bool dynSc, const EqControls& ec, const vrdyn::Controls& dc) {
    FourBandDSP eq; vrdyn::DynamicsProcessor dyn; eq.prepare(fs, ec); dyn.prepare(fs);
    const double fsV = 0.7746 * std::pow(10.0, dyn.calibrationDbu / 20.0), amp = 0.7746 * std::sqrt(2.0) * std::pow(10.0, dbu / 20.0) / fsV;
    const int n = (int)(1.5 * fs), blk = 256; std::vector<float> l(n), r(n), sl(blk), sr(blk);
    for (int i = 0; i < n; ++i) l[i] = r[i] = (float)(amp * std::sin(2 * kPi * freq * i / fs));
    for (int i = 0; i < n; i += blk) {
        const int m = std::min(blk, n - i); float* d[2] = {l.data() + i, r.data() + i};
        if (dynSc) {
            for (int j = 0; j < m; ++j) { sl[j] = d[0][j]; sr[j] = d[1][j]; }
            float* s[2] = {sl.data(), sr.data()}; eq.process(s, 2, m, ec, true, 0, 0);
            const float* sc[2] = {sl.data(), sr.data()}; dyn.process(d, nullptr, 2, m, dc, sc);
        } else { dyn.process(d, nullptr, 2, m, dc); eq.process(d, 2, m, ec, true, 0, 0); }
    }
    const int tail = (int)(0.1 * fs); double s = 0; for (int i = n - tail; i < n; ++i) s += (double)l[i] * l[i];
    return 20 * std::log10(std::sqrt(s / tail) * fsV / 0.7746);
}

int main() {
    EqControls flat{}; vrdyn::Controls off; off.lcIn = false;
    const double f1 = run(1000, 0, false, flat, off);
    std::printf("flat EQ, dynamics out: 0 dBu in -> %+.2f dBu out\n", f1);
    check(std::abs(f1) < 1.0, "flat channel is close to unity");

    EqControls hf{}; hf[3].gain = 1.0; hf[3].position = 0.5;   // HF full boost
    vrdyn::Controls comp; comp.lcIn = true; comp.cThreshold = 1.0 / 3.0; comp.cRatio = 0.8;   // 0 dBu, 5:1
    const double pathHf = run(6000, 4, false, hf, comp), scHf = run(6000, 4, true, hf, comp), scFlat = run(6000, 4, true, flat, comp);
    std::printf("6 kHz +4 dBu, HF boost: EQ in path %+.2f, EQ in side chain (DYN) %+.2f, DYN with flat EQ %+.2f dBu\n", pathHf, scHf, scFlat);
    check(scHf < scFlat - 2.0, "DYN: HF boost in the side chain compresses HF harder (de-esser)");
    check(pathHf > scHf + 6.0, "DYN: the EQ boost is no longer in the programme path");
    const double lowSc = run(200, 4, true, hf, comp), lowFlat = run(200, 4, true, flat, comp);
    std::printf("200 Hz +4 dBu: DYN with HF boost %+.2f, flat %+.2f dBu\n", lowSc, lowFlat);
    check(std::abs(lowSc - lowFlat) < 1.0, "DYN: low frequencies are unaffected by an HF side-chain boost");
    std::printf(failures ? "\nFAILED (%d)\n" : "\nALL PASS (%d failures)\n", failures);
    return failures ? 1 : 0;
}
