// Behaviour tests for the VR dynamics circuit model. Prints measured curves and checks them against
// the Neve description (Book 1, 1.2.pdf p17-19) and the printed panel legends.
#include "DynamicsCircuit.h"
#include <cstdio>
#include <vector>
#include <string>

using namespace vrdyn;
static int failures = 0;
static void check(bool ok, const std::string& what) { std::printf("%s  %s\n", ok ? "PASS" : "FAIL", what.c_str()); if (!ok) ++failures; }

constexpr double fs = 48000;
constexpr double kPi = 3.14159265358979323846;

// sine of given dBu (rms) at 1 kHz into the processor; returns output rms (dBu) over the last 100 ms
static double steadyOut(DynamicsProcessor& p, const Controls& c, double dbu, double seconds = 2.0, double freq = 1000) {
    p.prepare(fs);
    const double fsVolts = 0.7746 * std::pow(10.0, p.calibrationDbu / 20.0);
    const double amp = 0.7746 * std::sqrt(2.0) * std::pow(10.0, dbu / 20.0) / fsVolts;
    const int n = (int)(seconds * fs), tail = (int)(0.1 * fs);
    std::vector<float> l(n), r(n);
    for (int i = 0; i < n; ++i) l[i] = r[i] = (float)(amp * std::sin(2 * kPi * freq * i / fs));
    float* d[2] = {l.data(), r.data()};
    for (int i = 0; i < n; i += 256) { float* b[2] = {l.data() + i, r.data() + i}; p.process(b, nullptr, 2, std::min(256, n - i), c); }
    double s = 0; for (int i = n - tail; i < n; ++i) s += (double)l[i] * l[i];
    const double rms = std::sqrt(s / tail) * fsVolts;
    (void)d;
    return 20 * std::log10(rms / 0.7746);
}

// gain trajectory for a level step; returns gain (dB) at each ms
static std::vector<double> stepGain(DynamicsProcessor& p, const Controls& c, double dbu1, double dbu2, double t1, double t2, double freq = 1000) {
    p.prepare(fs);
    const double fsVolts = 0.7746 * std::pow(10.0, p.calibrationDbu / 20.0);
    const int n1 = (int)(t1 * fs), n2 = (int)(t2 * fs);
    std::vector<double> g;
    float buf[2][48];
    for (int i = 0; i < n1 + n2; i += 48) {
        const double dbu = i < n1 ? dbu1 : dbu2, amp = 0.7746 * std::sqrt(2.0) * std::pow(10.0, dbu / 20.0) / fsVolts;
        for (int j = 0; j < 48; ++j) buf[0][j] = buf[1][j] = (float)(amp * std::sin(2 * kPi * freq * (i + j) / fs));
        float* b[2] = {buf[0], buf[1]};
        p.process(b, nullptr, 2, 48, c);
        g.push_back(p.ch[0].gainDb);
    }
    return g;
}

int main() {
    DynamicsProcessor p;
    // ---------------- compressor static curve
    Controls c; c.lcIn = true; c.cThreshold = 1.0 / 3.0; /* 0 dBu */ c.cRelease = 0.3;
    for (double rp : {0.2, 0.5, 0.8}) {
        c.cRatio = rp;
        std::printf("\nCompressor static curve, threshold %.1f dBu, ratio pot %.2f (nominal %.2f:1)\n", compThresholdDbu(c), rp, ratioValue(c));
        double o10 = 0, o20 = 0;
        for (double in = -20; in <= 20.01; in += 5) {
            const double o = steadyOut(p, c, in);
            std::printf("  in %+6.1f dBu  out %+7.2f dBu  GR %5.2f dB\n", in, o, in - o);
            if (std::abs(in - 10) < .1) o10 = o; if (std::abs(in - 20) < .1) o20 = o;
        }
        const double slope = (o20 - o10) / 10, ratio = 1 / slope;
        check(std::abs(ratio - ratioValue(c)) / ratioValue(c) < 0.08, "ratio " + std::to_string(ratio) + " vs panel " + std::to_string(ratioValue(c)));
        const double below = steadyOut(p, c, -20);
        check(std::abs(below + 20) < 0.3, "unity gain below threshold");
    }
    // ---------------- make-up gain
    c.cRatio = 0.2; c.cGain = 0.5; c.cThreshold = 1.0;   // +20 dBu threshold, no compression
    check(std::abs(steadyOut(p, c, -10) - 5.0) < 0.2, "make-up 15 dB at mid travel");
    c.cGain = 0;
    // ---------------- attack: main loop + fast loop
    c.cThreshold = 1.0 / 3.0; c.cRatio = 1.0; c.cRelease = 0.3;
    for (bool fast : {false, true}) {
        c.cFastAttack = fast;
        auto g = stepGain(p, c, -10, 20, 0.2, 0.2);
        const int s = (int)(0.2 * fs / 48);
        const double final_ = g.back();
        auto reach = [&](double frac) { for (size_t i = s; i < g.size(); ++i) if (g[i] <= frac * final_) return (int)(i - s); return -1; };
        const int t50 = reach(0.5), t90 = reach(0.9);
        std::printf("\nAttack (%s fast loop), 30 dB step: final gain %.2f dB, 50%% after %d ms, 90%% after %d ms\n", fast ? "pulled" : "normal", final_, t50, t90);
        // fast loop (1 ms / 100 us) catches the transient; the main 7 ms loop settles the rest
        check(t50 >= 0 && t50 <= (fast ? 1 : 2), "fast loop takes the transient");
        check(t90 >= 0 && t90 <= 25, "main loop settles (7 ms time constant on programme peaks)");
    }
    c.cFastAttack = false;
    // ---------------- release vs pot
    for (double rp : {0.0, 0.39, 0.78}) {
        c.cRelease = rp;
        auto g = stepGain(p, c, 20, 0, 0.5, 6.0);
        const int s = (int)(0.5 * fs / 48);
        const double g0 = g[s - 1];
        int t63 = -1; for (size_t i = s; i < g.size(); ++i) if (g[i] >= g0 * 0.368) { t63 = (int)(i - s); break; }
        std::printf("Release pot %.2f (panel %.3f s): GR %.1f dB, 63%% recovery after %d ms\n", rp, compReleaseSeconds(c), -g0, t63);
        check(t63 > 0 && std::abs(t63 / 1000.0 - (compReleaseSeconds(c) + 0.03)) < 0.35 * compReleaseSeconds(c) + 0.02, "release time follows panel");
    }
    // auto
    c.cRelease = 1.0;
    {
        auto g1 = stepGain(p, c, 0, 20, 0.5, 0.02); auto g1r = stepGain(p, c, 20, 0, 0.02, 1.0);
        auto g2r = stepGain(p, c, 20, 0, 2.0, 2.0);
        const int s1 = (int)(0.02 * fs / 48), s2 = (int)(2.0 * fs / 48);
        auto t63 = [](const std::vector<double>& g, int s) { const double g0 = g[s - 1]; for (size_t i = s; i < g.size(); ++i) if (g[i] >= g0 * 0.368) return (int)(i - s); return -1; };
        const int a = t63(g1r, s1), b = t63(g2r, s2);
        std::printf("AUTO release: after 20 ms burst %d ms, after 2 s programme %d ms\n", a, b);
        check(b > a, "auto release is programme dependent (longer after sustained signal)");
        (void)g1;
    }
    // ---------------- low signal hold (10 dB / 7 s)
    c.cRelease = 0.0;   // 30 ms
    {
        auto g = stepGain(p, c, 20, -60, 0.5, 2.0);
        const int s = (int)(0.5 * fs / 48);
        std::printf("Signal drop to -60 dBu: GR %.1f -> after 1 s %.1f dB\n", -g[s - 1], -g[s + 1000]);
        check(-g[s + 1000] > 0.5 * -g[s - 1], "release frozen when signal falls 20 dB below threshold");
    }

    // ---------------- gate
    Controls gc; gc.gateIn = true; gc.gThreshold = 25.0 / 40.0; /* 0 dBu */ gc.gRange = 0.8; gc.gHysteresis = 0.2; gc.gRelease = 0.5;
    std::printf("\nGate: threshold %.1f dBu, range %.0f dB, hysteresis %.0f dB, release %.2f s\n", gateThresholdDbu(gc), gateRangeDb(gc), gateHysteresisDb(gc), gateReleaseSeconds(gc));
    for (double in : {-20.0, -5.0, 2.0, 10.0}) {
        const double o = steadyOut(p, gc, in, 3.0);
        std::printf("  in %+6.1f dBu  out %+7.2f dBu\n", in, o);
    }
    check(std::abs(steadyOut(p, gc, 10) - 10) < 0.3, "gate open above threshold+hysteresis");
    check(std::abs(steadyOut(p, gc, -20, 3.0) - (-20 - 40)) < 1.0, "gate closed attenuates by RANGE");
    // hysteresis: from closed, 2 dBu (between thr and thr+5) stays closed; from open it stays open
    {
        auto g = stepGain(p, gc, 10, 2, 0.5, 1.0);
        check(std::abs(g.back()) < 0.3, "hysteresis: open gate stays open at +2 dB");
        auto g2 = stepGain(p, gc, -20, 2, 3.0, 1.0);
        check(g2.back() < -30, "hysteresis: closed gate stays closed at +2 dB");
    }
    // attack 25 dB in 1 ms
    {
        auto g = stepGain(p, gc, -30, 10, 3.0, 0.05);
        const int s = (int)(3.0 * fs / 48);
        int t = -1; for (size_t i = s; i < g.size(); ++i) if (g[i] > -40 + 25) { t = (int)(i - s); break; }
        std::printf("Gate attack: 25 dB opened after %d ms\n", t);
        check(t >= 0 && t <= 3, "gate attack ~1 ms / 25 dB");
    }
    // expander
    gc.gHysteresis = 0.0;
    std::printf("\nExpander (HYST at EXP), threshold %.1f dBu\n", gateThresholdDbu(gc));
    double e1 = 0, e2 = 0;
    for (double in : {10.0, 0.0, -5.0, -10.0, -15.0, -20.0}) {
        const double o = steadyOut(p, gc, in, 3.0);
        std::printf("  in %+6.1f dBu  out %+7.2f dBu\n", in, o);
        if (in == -5.0) e1 = o; if (in == -15.0) e2 = o;
    }
    std::printf("  expansion slope %.2f (1:%.2f)\n", (e1 - e2) / 10, (e1 - e2) / 10);
    check((e1 - e2) / 10 > 1.8 && (e1 - e2) / 10 < 2.8, "expander about 1:2.3");
    // gate release: constant current into C27, time per 25 dB from the RV6b / R17 / R16 network
    {
        std::printf("\nGate release (time from open to 25 dB, RANGE 50 dB)\n");
        const double pots[5] = {0.0, 0.25, 0.5, 0.75, 1.0}, expect[5] = {0.030, 0.160, 0.300, 0.476, 2.99};
        for (int k = 0; k < 5; ++k) {
            Controls rc; rc.gateIn = true; rc.gRange = 1.0; rc.gHysteresis = 0.2; rc.gRelease = pots[k];
            GateSidechain gs; gs.prepare(fs);
            for (int i = 0; i < (int)(0.2 * fs); ++i) gs.tick(2.0, rc);          // open
            int n = 0; while (gs.tick(-6.0, rc) < 25.0 && n < (int)(10 * fs)) ++n;  // key gone
            const double t = n / fs - 0.032 * 2.0;   // minus the peak follower decay from +2 V to 0 V (1 V / 32 ms)
            std::printf("  REL pot %.2f: %.3f s (circuit %.3f s)\n", pots[k], t, expect[k]);
            check(std::abs(t - expect[k]) < 0.05 * expect[k] + 0.003, "gate release time per 25 dB follows RV6b network");
        }
    }
    // invert (ducker)
    gc.gHysteresis = 0.2; gc.invert = true; gc.gRange = 0.2;  // 10 dB duck
    check(std::abs(steadyOut(p, gc, 10) - 0) < 0.4, "INV: signal above threshold ducked by RANGE");
    check(std::abs(steadyOut(p, gc, -20, 3.0) + 20) < 0.4, "INV: below threshold passes");

    // ducker with an external key: programme -10 dBu, key bursts; duck depth = RANGE, recovery = gate RELEASE
    {
        Controls dc; dc.gateIn = true; dc.key = true; dc.invert = true; dc.gRange = 0.4; dc.gHysteresis = 0.2;
        dc.gThreshold = 0.5; dc.gRelease = 0.0;   // 0.03 s / 25 dB
        auto duck = [&](double releasePot, double& during, double& after300ms) {
            dc.gRelease = releasePot; p.prepare(fs);
            const double fsV = 0.7746 * std::pow(10.0, p.calibrationDbu / 20.0);
            const double a = 0.7746 * std::sqrt(2.0) * std::pow(10.0, -10 / 20.0) / fsV, ka = 0.7746 * std::sqrt(2.0) * 4.0 / fsV;
            const int n = (int)(2.0 * fs); std::vector<float> l(n), r(n), kl(n), kr(n);
            for (int i = 0; i < n; ++i) { l[i] = r[i] = (float)(a * std::sin(2 * kPi * 1000 * i / fs));
                kl[i] = kr[i] = (i > fs * 0.5 && i < fs * 1.0) ? (float)(ka * std::sin(2 * kPi * 300 * i / fs)) : 0.f; }
            for (int i = 0; i < n; i += 256) { float* b[2] = {l.data() + i, r.data() + i}; const float* k[2] = {kl.data() + i, kr.data() + i};
                p.process(b, k, 2, std::min(256, n - i), dc); }
            auto lvl = [&](double t0) { double s2 = 0; const int i0 = (int)(t0 * fs), m = (int)(0.02 * fs); for (int i = i0; i < i0 + m; ++i) s2 += (double)l[i] * l[i];
                return 20 * std::log10(std::sqrt(s2 / m) * fsV / 0.7746); };
            during = lvl(0.9); after300ms = lvl(1.3);
            std::printf("  ducker REL pot %.2f: before %+.1f  during key %+.1f  0.3 s after key %+.1f dBu\n", releasePot, lvl(0.3), during, after300ms);
        };
        double d1, a1, d2, a2; duck(0.0, d1, a1); duck(1.0, d2, a2);
        check(std::abs(d1 - (-10 - gateRangeDb(dc))) < 1.0, "ducker: programme ducked by RANGE while the key is present");
        check(std::abs(a1 + 10) < 0.5, "ducker: short release recovers at once");
        check(a2 < -20, "ducker: long release recovers slowly (3 s / 25 dB)");
    }

    // ---------------- curves for docs/results (CSV)
    if (FILE* f = std::fopen("curves_static.csv", "w")) {
        std::fprintf(f, "in_dbu,comp_2,comp_3,comp_5,gate,expander\n");
        Controls a; a.lcIn = true; a.cThreshold = 1.0 / 3.0;
        Controls gte; gte.gateIn = true; gte.gThreshold = 25.0 / 40.0; gte.gRange = 0.8; gte.gHysteresis = 0.2; gte.gRelease = 0.3;
        Controls ex = gte; ex.gHysteresis = 0.0;
        for (double in = -40; in <= 20.01; in += 2) {
            double o[5];
            a.cRatio = .2; o[0] = steadyOut(p, a, in, 1.0); a.cRatio = .5; o[1] = steadyOut(p, a, in, 1.0); a.cRatio = .8; o[2] = steadyOut(p, a, in, 1.0);
            o[3] = steadyOut(p, gte, in, 2.0); o[4] = steadyOut(p, ex, in, 2.0);
            std::fprintf(f, "%.1f,%.3f,%.3f,%.3f,%.3f,%.3f\n", in, o[0], o[1], o[2], o[3], o[4]);
        }
        std::fclose(f);
    }
    if (FILE* f = std::fopen("curves_time.csv", "w")) {
        // 20 dB burst of 300 ms then back: compressor (normal / fast / auto) and gate
        std::fprintf(f, "ms,comp_normal,comp_fast,comp_auto,gate\n");
        Controls a; a.lcIn = true; a.cThreshold = 1.0 / 3.0; a.cRatio = 0.8; a.cRelease = 0.39;
        Controls b = a; b.cFastAttack = true; Controls au = a; au.cRelease = 1.0;
        Controls gte; gte.gateIn = true; gte.gThreshold = 25.0 / 40.0; gte.gRange = 0.8; gte.gHysteresis = 0.2; gte.gRelease = 0.3;
        auto run = [&](const Controls& c, double lo, double hi) {
            auto g1 = stepGain(p, c, lo, lo, 0.2, 0.0);
            p.prepare(fs);
            std::vector<double> g; const double fsVolts = 0.7746 * std::pow(10.0, p.calibrationDbu / 20.0); float buf[2][48];
            for (int i = 0; i < (int)(1.5 * fs); i += 48) {
                const double t = i / fs, dbu = (t >= 0.2 && t < 0.5) ? hi : lo, amp = 0.7746 * std::sqrt(2.0) * std::pow(10.0, dbu / 20.0) / fsVolts;
                for (int j = 0; j < 48; ++j) buf[0][j] = buf[1][j] = (float)(amp * std::sin(2 * kPi * 1000 * (i + j) / fs));
                float* bb[2] = {buf[0], buf[1]}; p.process(bb, nullptr, 2, 48, c); g.push_back(p.ch[0].gainDb);
            }
            (void)g1; return g;
        };
        auto n = run(a, 0, 20), fa = run(b, 0, 20), au_ = run(au, 0, 20), ga = run(gte, -30, 10);
        for (size_t i = 0; i < n.size(); ++i) std::fprintf(f, "%zu,%.3f,%.3f,%.3f,%.3f\n", i, n[i], fa[i], au_[i], ga[i]);
        std::fclose(f);
    }

    std::printf("\n%s (%d failures)\n", failures ? "FAILED" : "ALL PASS", failures);
    return failures ? 1 : 0;
}
