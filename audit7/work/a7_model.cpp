// AUDIT 7: measurements on the plugin models themselves (robustness, sample-rate dependence, CPU, artefacts).
#include "DynamicsCircuit.h"
#include "FourBandDSP.h"
#include <cstdio>
#include <vector>
#include <chrono>
#include <limits>
#include <string>
#include <cstring>

static const double kPi = 3.14159265358979323846;
using namespace vrdyn;

static double fsVolts(const DynamicsProcessor& p) { return 0.7746 * std::pow(10.0, p.calibrationDbu / 20.0); }
static float ampFs(const DynamicsProcessor& p, double dbu) { return (float)(0.7746 * std::sqrt(2.0) * std::pow(10.0, dbu / 20.0) / fsVolts(p)); }

// Goertzel magnitude (Hann window) of x at frequency f
static double tone(const std::vector<double>& x, double fs, double f) {
    double re = 0, im = 0, wsum = 0; const size_t n = x.size();
    for (size_t i = 0; i < n; ++i) { const double w = 0.5 - 0.5 * std::cos(2 * kPi * i / (n - 1)); re += w * x[i] * std::cos(2 * kPi * f * i / fs); im -= w * x[i] * std::sin(2 * kPi * f * i / fs); wsum += w; }
    return 2.0 * std::sqrt(re * re + im * im) / wsum;
}

int main(int argc, char** argv) {
    const std::string what = argc > 1 ? argv[1] : "all";
    auto on = [&](const char* k) { return what == "all" || what == k; };

    if (on("ripple")) {
        std::printf("== steady-state gain ripple of the model (GR max-min over the last second of a 12 s tone, thr 0 dBu, +10 dBu in, ratio lim, 48 kHz)\n");
        for (double f : {50.0, 100.0, 1000.0, 997.0, 3000.0, 10000.0}) for (double rel : {0.0, 0.39}) {
            DynamicsProcessor p; p.prepare(48000); Controls c; c.lcIn = true; c.cThreshold = 1.0 / 3.0; c.cRatio = 1.0; c.cRelease = rel;
            const int n = 12 * 48000; double lo = 1e9, hi = -1e9; const float a = ampFs(p, 10);
            float l[64], r[64]; float* d[2] = {l, r};
            for (int i = 0; i < n; i += 64) { for (int j = 0; j < 64; ++j) l[j] = r[j] = a * (float)std::sin(2 * kPi * f * (i + j) / 48000.0);
                // sample the gain per sample by processing one sample at a time
                for (int j = 0; j < 64; ++j) { float* s[2] = {l + j, r + j}; p.process(s, nullptr, 2, 1, c); if (i + j > n - 48000) { lo = std::min(lo, p.ch[0].gainDb); hi = std::max(hi, p.ch[0].gainDb); } } }
            std::printf("  %6.0f Hz REL %.2f: gain %.3f .. %.3f dB (pp %.4f)\n", f, rel, lo, hi, hi - lo);
        }
        std::printf("== expander ripple (HYST=EXP, 10 dB below thr, range 50, REL 0.0), per-sample GR over the last 0.5 s\n");
        for (double f : {60.0, 200.0, 1000.0}) {
            GateSidechain g; g.prepare(48000); Controls c; c.gateIn = true; c.gThreshold = 25.0 / 40.0; c.gRange = 1.0; c.gHysteresis = 0.0; c.gRelease = 0.0;
            const double a = 0.7746 * std::sqrt(2.0) * std::pow(10.0, -10 / 20.0); double lo = 1e9, hi = -1e9; int blips = 0; double prev = 0;
            for (int i = 0; i < 3 * 48000; ++i) { const double gr = g.tick(logLevelVolts(a * std::sin(2 * kPi * f * i / 48000.0), gateThresholdDbu(c)), c);
                if (i > 2.5 * 48000) { lo = std::min(lo, gr); hi = std::max(hi, gr); if (gr > prev + 1e-9 && prev <= lo + 1e-9) ++blips; } prev = gr; }
            std::printf("  %5.0f Hz: GR %.3f .. %.3f dB (pp %.3f), excursions in 0.5 s: %d\n", f, lo, hi, hi - lo, blips);
        }
    }

    if (on("rate")) {
        std::printf("\n== sample-rate dependence: steady GR of the limiter for a tone 10 dB over threshold (ideal continuous-time answer 10.00 dB)\n");
        for (double fs : {44100.0, 48000.0, 96000.0, 192000.0}) {
            std::printf("  fs %6.0f:", fs);
            for (double f : {1000.0, 5000.0, 10000.0, 11025.0, 12000.0, 14700.0, 16000.0, 19000.0}) {
                double worst = 1e9, best = -1e9;
                for (double ph : {0.0, 0.25, 0.5, 0.785, 1.0, 1.3}) {
                    DynamicsProcessor p; p.prepare(fs); Controls c; c.lcIn = true; c.cThreshold = 1.0 / 3.0; c.cRatio = 1.0; c.cRelease = 0.39;
                    const int n = (int)(1.0 * fs); const float a = ampFs(p, 10); std::vector<float> l(n), r(n);
                    for (int i = 0; i < n; ++i) l[i] = r[i] = a * (float)std::sin(2 * kPi * f * i / fs + ph);
                    float* d[2] = {l.data(), r.data()}; p.process(d, nullptr, 2, n, c);
                    worst = std::min(worst, -p.ch[0].gainDb); best = std::max(best, -p.ch[0].gainDb);
                }
                std::printf(" %5.0f Hz: %5.2f..%5.2f |", f, worst, best);
            }
            std::printf("\n");
        }
        std::printf("== attack/release vs sample rate (0 -> +20 dBu step, ratio lim, REL 0.39): time to 90 %% GR and time from drop to 10 %%\n");
        for (double fs : {44100.0, 48000.0, 96000.0, 192000.0}) {
            DynamicsProcessor p; p.prepare(fs); Controls c; c.lcIn = true; c.cThreshold = 1.0 / 3.0; c.cRatio = 1.0; c.cRelease = 0.39;
            const float a1 = ampFs(p, 20), a0 = ampFs(p, -10); int t90 = -1, t10 = -1; double g0 = 0;
            for (int i = 0; i < (int)(4.0 * fs); ++i) { const double t = i / fs; float v = (t < 0.5 ? a1 : a0) * (float)std::sin(2 * kPi * 1000 * t); float w = v; float* d[2] = {&v, &w}; p.process(d, nullptr, 2, 1, c);
                const double gr = -p.ch[0].gainDb; if (t < 0.5 && t90 < 0 && gr >= 18.0) t90 = i; if (t < 0.5) g0 = gr; if (t >= 0.5 && t10 < 0 && gr <= 0.1 * g0) t10 = i - (int)(0.5 * fs); }
            std::printf("  fs %6.0f: attack 90%% %.2f ms, release to 10%% %.1f ms\n", fs, 1000.0 * t90 / fs, 1000.0 * t10 / fs);
        }
    }

    if (on("nan")) {
        std::printf("\n== non-finite input\n");
        for (int kind = 0; kind < 3; ++kind) {
            DynamicsProcessor p; p.prepare(48000); Controls c; c.lcIn = true; c.cThreshold = 1.0 / 3.0; c.cRatio = 0.8; c.gateIn = true;
            const float a = ampFs(p, 0); std::vector<float> l(48000 * 3), r(48000 * 3);
            for (size_t i = 0; i < l.size(); ++i) l[i] = r[i] = a * (float)std::sin(2 * kPi * 1000 * i / 48000.0);
            const float bad = kind == 0 ? std::numeric_limits<float>::quiet_NaN() : (kind == 1 ? std::numeric_limits<float>::infinity() : 1e30f);
            l[48000] = r[48000] = bad;
            float* d[2] = {l.data(), r.data()}; p.process(d, nullptr, 2, (int)l.size(), c);
            double s = 0; int bads = 0; for (size_t i = 2 * 48000; i < l.size(); ++i) { if (!std::isfinite(l[i])) ++bads; else s += (double)l[i] * l[i]; }
            const double rms = std::sqrt(s / 48000.0);
            std::printf("  one %s sample at t=1 s: output rms in the 3rd second %.6f (input rms %.6f), non-finite outputs %d, comp vMain %g, gate vPeak %g\n", kind == 0 ? "NaN" : (kind == 1 ? "+inf" : "1e30"), rms, a / std::sqrt(2.0), bads, p.ch[0].comp.vMain, p.ch[0].gate.vPeak);
        }
        {   // EQ with a NaN sample
            FourBandDSP eq; EqControls ec{}; eq.prepare(48000, ec); std::vector<float> l(4800, 0.1f), r(4800, 0.1f); l[100] = std::numeric_limits<float>::quiet_NaN();
            float* d[2] = {l.data(), r.data()}; eq.process(d, 2, 4800, ec, true, 0, 0); int bads = 0; for (float v : l) if (!std::isfinite(v)) ++bads;
            std::printf("  EQ (FourBandDSP) with one NaN input sample: %d non-finite output samples, last output %g\n", bads, l.back());
        }
    }

    if (on("mono")) {
        DynamicsProcessor p; p.prepare(48000); Controls c; c.lcIn = true; c.cThreshold = 1.0 / 3.0; c.cRatio = 0.8; c.link = true;
        std::vector<float> l(48000); const float a = ampFs(p, 10); for (size_t i = 0; i < l.size(); ++i) l[i] = a * (float)std::sin(2 * kPi * 1000 * i / 48000.0);
        float* d[1] = {l.data()}; p.process(d, nullptr, 1, (int)l.size(), c);
        std::printf("\n== mono (nc = 1, LINK on): GR %.2f dB, meters ch0 %.2f ch1 %.2f\n", -p.ch[0].gainDb, p.meterCompGr[0], p.meterCompGr[1]);
    }

    if (on("alias")) {
        std::printf("\n== aliasing of the gain modulation: two tones 9.1 kHz + 10.3 kHz, each +4 dBu (thr 0 dBu), ratio lim, FAST, REL 0.0\n");
        for (double fs : {48000.0, 192000.0}) {
            DynamicsProcessor p; p.prepare(fs); Controls c; c.lcIn = true; c.cThreshold = 1.0 / 3.0; c.cRatio = 1.0; c.cRelease = 0.0; c.cFastAttack = true;
            const int n = (int)(3.0 * fs); const float a = ampFs(p, 4); std::vector<float> l(n), r(n);
            for (int i = 0; i < n; ++i) l[i] = r[i] = a * (float)(std::sin(2 * kPi * 9100.0 * i / fs) + std::sin(2 * kPi * 10300.0 * i / fs));
            float* d[2] = {l.data(), r.data()}; p.process(d, nullptr, 2, n, c);
            std::vector<double> x(l.begin() + (int)(2.0 * fs), l.end());
            const double ref = tone(x, fs, 9100.0);
            std::printf("  fs %6.0f: fundamental %.1f dBFS;", fs, 20 * std::log10(ref));
            std::printf(" true IMD lines (re fund): 7.9k %.1f, 6.7k %.1f, 5.5k %.1f, 4.3k %.1f, 3.1k %.1f dB;", 20 * std::log10(tone(x, fs, 7900) / ref), 20 * std::log10(tone(x, fs, 6700) / ref), 20 * std::log10(tone(x, fs, 5500) / ref), 20 * std::log10(tone(x, fs, 4300) / ref), 20 * std::log10(tone(x, fs, 3100) / ref));
            std::printf(" alias lines (48k images): 8.9k %.1f, 6.5k %.1f, 4.1k %.1f, 2.9k %.1f, 0.5k %.1f dB\n", 20 * std::log10(tone(x, fs, 8900) / ref), 20 * std::log10(tone(x, fs, 6500) / ref), 20 * std::log10(tone(x, fs, 4100) / ref), 20 * std::log10(tone(x, fs, 2900) / ref), 20 * std::log10(tone(x, fs, 500) / ref));
        }
    }

    if (on("cpu")) {
        std::printf("\n== CPU cost (single thread, stereo)\n");
        for (int mode = 0; mode < 3; ++mode) {
            DynamicsProcessor p; p.prepare(48000); Controls c; c.lcIn = true; c.gateIn = true; c.cThreshold = 0.2; c.cRatio = 0.8; c.cRelease = mode == 1 ? 1.0 : 0.39; c.gThreshold = 0.3;
            const int n = 48000 * 20, blk = mode == 2 ? 1 : 512; std::vector<float> l(n), r(n); unsigned s = 1;
            for (int i = 0; i < n; ++i) { s = s * 1664525u + 1013904223u; l[i] = r[i] = 0.25f * ((int)(s >> 8) / 8388608.0f - 1.0f) * (float)(0.5 + 0.5 * std::sin(2 * kPi * 3 * i / 48000.0)); }
            const auto t0 = std::chrono::steady_clock::now();
            for (int i = 0; i < n; i += blk) { float* d[2] = {l.data() + i, r.data() + i}; p.process(d, nullptr, 2, std::min(blk, n - i), c); }
            const double sec = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
            std::printf("  dynamics %s: %.1f ns per stereo frame, %.2f %% of real time at 48 kHz (%.2f %% at 192 kHz)\n", mode == 0 ? "normal, block 512" : (mode == 1 ? "AUTO, block 512" : "normal, block 1"), 1e9 * sec / n, 100 * sec / 20.0, 400 * sec / 20.0);
        }
        {
            FourBandDSP eq; EqControls ec{}; ec[0].gain = 0.8; ec[1].gain = 0.3; ec[2].gain = 0.7; ec[3].gain = 0.6; eq.prepare(48000, ec);
            const int n = 48000 * 10; std::vector<float> l(n), r(n); unsigned s = 1; for (int i = 0; i < n; ++i) { s = s * 1664525u + 1013904223u; l[i] = r[i] = 0.25f * ((int)(s >> 8) / 8388608.0f - 1.0f); }
            const auto t0 = std::chrono::steady_clock::now();
            for (int i = 0; i < n; i += 512) { float* d[2] = {l.data() + i, r.data() + i}; eq.process(d, 2, std::min(512, n - i), ec, true, 0, 0); }
            const double sec = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
            std::printf("  EQ FourBandDSP: %.1f ns per stereo frame, %.2f %% of real time at 48 kHz (%.2f %% at 192 kHz)\n", 1e9 * sec / n, 100 * sec / 10.0, 400 * sec / 10.0);
        }
    }

    if (on("eq")) {
        std::printf("\n== EQ (FourBandDSP as used by the channel plugin): magnitude response in dB\n");
        const double freqs[] = {20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 15000, 20000};
        auto resp = [&](double fs, const EqControls& ec, const char* name) {
            std::printf("  fs %6.0f %-22s", fs, name);
            for (double f : freqs) {
                if (f > 0.45 * fs) { std::printf("    --  "); continue; }
                FourBandDSP eq; eq.prepare(fs, ec); const int n = (int)(0.6 * fs); std::vector<float> l(n); for (int i = 0; i < n; ++i) l[i] = 0.05f * (float)std::sin(2 * kPi * f * i / fs);
                float* d[1] = {l.data()}; eq.process(d, 1, n, ec, true, 0, 0);
                // settle: EQ mix ramps in 20 ms; measure the last 0.2 s
                std::vector<double> x(l.begin() + (int)(0.4 * fs), l.end()); bool bad = false; for (double v : x) if (!std::isfinite(v)) bad = true;
                if (bad) std::printf("   NaN  "); else std::printf(" %+6.2f ", 20 * std::log10(tone(x, fs, f) / 0.05));
            }
            std::printf("\n");
        };
        std::printf("  %-34s", "freq Hz:"); for (double f : freqs) std::printf(" %6.0f ", f); std::printf("\n");
        EqControls flat{};
        EqControls lfb{}; lfb[0].gain = 1.0; EqControls lfc{}; lfc[0].gain = 0.0;
        EqControls hfb{}; hfb[3].gain = 1.0; EqControls hfmax{}; hfmax[3].gain = 1.0; hfmax[3].position = 1.0;
        EqControls hmf{}; hmf[2].gain = 1.0; hmf[2].q = 1.0; EqControls lmf{}; lmf[1].gain = 0.0; lmf[1].q = 0.0;
        EqControls hfs{}; hfs[3].gain = 1.0; hfs[3].shelf = true; EqControls lfs{}; lfs[0].gain = 1.0; lfs[0].shelf = true;
        for (double fs : {44100.0, 48000.0, 96000.0, 192000.0}) { resp(fs, flat, "flat"); }
        for (double fs : {48000.0, 96000.0}) { resp(fs, lfb, "LF +max bell"); resp(fs, lfc, "LF -max bell"); resp(fs, lfs, "LF +max shelf"); resp(fs, hfb, "HF +max bell"); resp(fs, hfs, "HF +max shelf"); resp(fs, hfmax, "HF +max, freq max"); resp(fs, hmf, "HMF +max, Q pot 1"); resp(fs, lmf, "LMF -max, Q pot 0"); }
        for (double fs : {22050.0, 32000.0}) { resp(fs, flat, "flat"); resp(fs, hfmax, "HF +max, freq max"); }
        std::printf("  band centre frequencies (model): ");
        const double caps[4] = {470e-9, 82e-9, 20e-9, 10e-9}; const char* nm[4] = {"LF", "LMF", "HMF", "HF"};
        for (int b = 0; b < 4; ++b) std::printf("%s %.0f..%.0f..%.0f Hz  ", nm[b], circuit::frequency(0) * 470e-9 / caps[b], circuit::frequency(.5) * 470e-9 / caps[b], circuit::frequency(1) * 470e-9 / caps[b]);
        std::printf("\n");
    }
    return 0;
}
