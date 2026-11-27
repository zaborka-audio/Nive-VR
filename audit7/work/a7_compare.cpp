// AUDIT 7: plugin model (vrdyn, DynamicsCircuit.h) against the auditor's reference reading of the schematics (ref_dyn.h).
#include "DynamicsCircuit.h"
#include "ref_dyn.h"
#include <cstdio>
#include <vector>
#include <functional>
#include <string>

static const double kPi = 3.14159265358979323846;
static double ampFor(double dbu) { return 0.7746 * std::sqrt(2.0) * std::pow(10.0, dbu / 20.0); }   // volts peak of a sine

// envelope(t) in dBu (rms of the sine), returns GR trajectories sampled every ms
struct Traj { std::vector<double> ms; };
using Env = std::function<double(double)>;

static std::vector<double> runModelComp(const vrdyn::Controls& c, const Env& env, double freq, double T, double fs = 48000) {
    vrdyn::CompSidechain s; s.prepare(fs);
    const double thr = vrdyn::compThresholdDbu(c), k = vrdyn::ratioFraction(c);
    std::vector<double> out; const int n = (int)(T * fs), step = (int)(fs / 1000);
    for (int i = 0; i < n; ++i) {
        const double t = i / fs, x = ampFor(env(t)) * std::sin(2 * kPi * freq * t);
        const double v = s.tick(vrdyn::logLevelVolts(x, thr), c);
        if (i % step == 0) out.push_back(vrdyn::kVcDbPerVolt * k * v);
    }
    return out;
}
static std::vector<double> runRefComp(const ref::Ctl& c, const Env& env, double freq, double T, double fs = 192000) {
    ref::Comp s; s.prepare(fs);
    std::vector<double> out; const int n = (int)(T * fs), step = (int)(fs / 1000);
    for (int i = 0; i < n; ++i) {
        const double t = i / fs, x = ampFor(env(t)) * std::sin(2 * kPi * freq * t);
        const double v = s.tick(ref::logVolts(x, c.thrDbu), c);
        if (i % step == 0) out.push_back(s.grDb(v, c));
    }
    return out;
}
static std::vector<double> runModelGate(const vrdyn::Controls& c, const Env& env, double freq, double T, double fs = 48000, std::vector<double>* minmax = nullptr) {
    vrdyn::GateSidechain s; s.prepare(fs);
    const double thr = vrdyn::gateThresholdDbu(c);
    std::vector<double> out; const int n = (int)(T * fs), step = (int)(fs / 1000);
    for (int i = 0; i < n; ++i) {
        const double t = i / fs, x = ampFor(env(t)) * std::sin(2 * kPi * freq * t);
        const double g = s.tick(vrdyn::logLevelVolts(x, thr), c);
        if (i % step == 0) out.push_back(g);
        if (minmax) minmax->push_back(g);
    }
    return out;
}
static std::vector<double> runRefGate(const ref::Ctl& c, const Env& env, double freq, double T, double fs = 192000, std::vector<double>* all = nullptr) {
    ref::Gate s; s.prepare(fs);
    std::vector<double> out; const int n = (int)(T * fs), step = (int)(fs / 1000);
    for (int i = 0; i < n; ++i) {
        const double t = i / fs, x = ampFor(env(t)) * std::sin(2 * kPi * freq * t);
        const double g = s.tick(ref::logVolts(x, c.gThrDbu), c);
        if (i % step == 0) out.push_back(g);
        if (all) all->push_back(g);
    }
    return out;
}
// first ms index >= from where pred holds
static int firstMs(const std::vector<double>& g, int from, const std::function<bool(double)>& pred) { for (size_t i = from; i < g.size(); ++i) if (pred(g[i])) return (int)i - from; return -1; }

int main() {
    std::printf("constants: ref kLogV %.5f V/dB, kVc %.4f dB/V, product %.5f; model 0.1 V/dB x %.4f = %.4f\n\n", ref::kLogV, ref::kVc, ref::kLogV * ref::kVc, vrdyn::kVcDbPerVolt, 0.1 * vrdyn::kVcDbPerVolt);

    // ------------------------------------------------------------------ E3: ratio law
    std::printf("E3 RATIO pot law (static slope): pot | model ratio | circuit ratio (pot as divider, R35 2k4 // top, R37 10k load)\n");
    for (double p : {0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 1.0}) {
        vrdyn::Controls c; c.cRatio = p;
        std::printf("  %.2f | %8.2f | %8.2f\n", p, std::min(999.0, vrdyn::ratioValue(c)), std::min(999.0, ref::ratioValue(p)));
    }
    // static check through the dynamic paths, +10 dB over threshold
    std::printf("  steady GR for +10 dB over (1 kHz): pot | model dB | circuit dB\n");
    for (double p : {0.2, 0.5, 0.8, 1.0}) {
        vrdyn::Controls c; c.lcIn = true; c.cThreshold = 1.0 / 3.0; c.cRatio = p; ref::Ctl r; r.thrDbu = 0; r.ratioPot = p;
        auto gm = runModelComp(c, [](double) { return 10.0; }, 1000, 0.5), gr = runRefComp(r, [](double) { return 10.0; }, 1000, 0.5);
        std::printf("  %.2f | %6.2f | %6.2f\n", p, gm.back(), gr.back());
    }

    // ------------------------------------------------------------------ E1: release law
    std::printf("\nE1 L/C RELEASE: tau(model) = 0.03*100^(p/0.78) s; tau(circuit) = R47*C11/alpha(p). Step thr+20 -> thr-10 dBu, ratio lim.\n");
    std::printf("  pot | model tau s | circuit tau s | circuit 2.3 tau | measured: time (ms) from drop until GR falls to 50%% and to 10%%  model / circuit\n");
    for (double p : {0.0, 0.1, 0.25, 0.39, 0.5, 0.6, 0.75, 0.9, 0.96}) {
        vrdyn::Controls c; c.lcIn = true; c.cThreshold = 1.0 / 3.0; c.cRatio = 1.0; c.cRelease = p;
        ref::Ctl r; r.thrDbu = 0; r.ratioPot = 1.0; r.relPot = p;
        const Env env = [](double t) { return t < 0.5 ? 20.0 : -10.0; };
        const double T = 0.5 + 40.0;
        auto gm = runModelComp(c, env, 1000, T), gr = runRefComp(r, env, 1000, T);
        const double m0 = gm[499], r0 = gr[499];
        std::printf("  %.2f | %8.3f | %8.4f | %7.3f | 50%%: %6d / %6d   10%%: %6d / %6d   (GR0 %.1f / %.1f dB)\n", p, vrdyn::compReleaseSeconds(c), ref::relTau(p), 2.303 * ref::relTau(p),
                    firstMs(gm, 500, [&](double g) { return g <= 0.5 * m0; }), firstMs(gr, 500, [&](double g) { return g <= 0.5 * r0; }),
                    firstMs(gm, 500, [&](double g) { return g <= 0.1 * m0; }), firstMs(gr, 500, [&](double g) { return g <= 0.1 * r0; }), m0, r0);
    }

    // ------------------------------------------------------------------ E2: AUTO
    std::printf("\nE2 AUTO release (ratio lim, thr 0): burst at +20 dBu of given length, then -10 dBu. Time (ms) until GR = 50%% / 25%% / 10%% of its value at the end of the burst\n");
    for (double len : {0.005, 0.02, 0.1, 0.5, 2.0, 10.0}) {
        vrdyn::Controls c; c.lcIn = true; c.cThreshold = 1.0 / 3.0; c.cRatio = 1.0; c.cRelease = 1.0;
        ref::Ctl r; r.thrDbu = 0; r.ratioPot = 1.0; r.autoRel = true;
        const Env env = [len](double t) { return (t >= 0.1 && t < 0.1 + len) ? 20.0 : -10.0; };
        const double T = 0.1 + len + 30.0; const int s = (int)((0.1 + len) * 1000);
        auto gm = runModelComp(c, env, 1000, T), gr = runRefComp(r, env, 1000, T);
        const double m0 = gm[s - 1], r0 = gr[s - 1];
        auto t3 = [&](const std::vector<double>& g, double g0, char* buf) { std::snprintf(buf, 64, "%5d /%5d /%6d", firstMs(g, s, [&](double x) { return x <= 0.5 * g0; }), firstMs(g, s, [&](double x) { return x <= 0.25 * g0; }), firstMs(g, s, [&](double x) { return x <= 0.1 * g0; })); };
        char a[64], b[64]; t3(gm, m0, a); t3(gr, r0, b);
        std::printf("  burst %6.3f s: model GR0 %5.1f dB -> %s   | circuit GR0 %5.1f dB -> %s\n", len, m0, a, r0, b);
    }
    {   // attack in AUTO vs normal: time to 90 % of final GR for a 0 -> +20 step
        for (bool au : {false, true}) {
            vrdyn::Controls c; c.lcIn = true; c.cThreshold = 1.0 / 3.0; c.cRatio = 1.0; c.cRelease = au ? 1.0 : 0.3;
            ref::Ctl r; r.thrDbu = 0; r.ratioPot = 1.0; r.autoRel = au; r.relPot = 0.3;
            const Env env = [](double t) { return t < 0.2 ? -30.0 : 20.0; };
            auto gm = runModelComp(c, env, 1000, 3.2), gr = runRefComp(r, env, 1000, 3.2);
            std::printf("  attack %-6s: model 50%%/90%%/99%% of final at %d / %d / %d ms (final %.1f)   circuit %d / %d / %d ms (final %.1f)\n", au ? "AUTO" : "normal",
                        firstMs(gm, 200, [&](double g) { return g >= 0.5 * gm.back(); }), firstMs(gm, 200, [&](double g) { return g >= 0.9 * gm.back(); }), firstMs(gm, 200, [&](double g) { return g >= 0.99 * gm.back(); }), gm.back(),
                        firstMs(gr, 200, [&](double g) { return g >= 0.5 * gr.back(); }), firstMs(gr, 200, [&](double g) { return g >= 0.9 * gr.back(); }), firstMs(gr, 200, [&](double g) { return g >= 0.99 * gr.back(); }), gr.back());
        }
    }

    // ------------------------------------------------------------------ E4: gate hold / detector decay
    std::printf("\nE4 GATE closing after the signal stops (1 kHz at thr+L dB, then silence). Time (ms) until GR reaches 1 dB / 20 dB. hyst 5 dB\n");
    for (double range : {0.2, 0.8, 1.0}) for (double L : {5.0, 10.0, 20.0}) for (double rel : {0.0, 0.5}) {
        vrdyn::Controls c; c.gateIn = true; c.gThreshold = 25.0 / 40.0; c.gRange = range; c.gHysteresis = 0.2; c.gRelease = rel;
        ref::Ctl r; r.gThrDbu = 0; r.rangePot = range; r.hystPot = 0.2; r.gRelPot = rel;
        const Env env = [L](double t) { return t < 0.3 ? L : -100.0; };
        auto gm = runModelGate(c, env, 1000, 4.0), gr = runRefGate(r, env, 1000, 4.0);
        const double target = std::min(20.0, 0.9 * 4.9 * 10.29 * range);
        std::printf("  range %4.0f dB, L +%2.0f dB, REL pot %.1f: 1 dB: model %4d / circuit %4d ms   %2.0f dB: model %5d / circuit %5d ms\n", 4.9 * 10.29 * range, L, rel,
                    firstMs(gm, 300, [](double g) { return g >= 1.0; }), firstMs(gr, 300, [](double g) { return g >= 1.0; }), target,
                    firstMs(gm, 300, [&](double g) { return g >= target; }), firstMs(gr, 300, [&](double g) { return g >= target; }));
    }

    // ------------------------------------------------------------------ E5: LF tone, does the gate stay open
    std::printf("\nE5 GATE with a steady low tone (opened by a 0.2 s burst at thr+25 dB, then the tone at thr+X). Max GR (dB) during the last second; hyst 5 dB, REL 0.5\n");
    for (double range : {0.2, 0.8}) for (double f : {40.0, 60.0, 100.0, 200.0, 1000.0}) {
        std::printf("  range %2.0f dB, %5.0f Hz:", 4.9 * 10.29 * range, f);
        for (double X : {1.0, 3.0, 6.0, 10.0, 15.0}) {
            vrdyn::Controls c; c.gateIn = true; c.gThreshold = 25.0 / 40.0; c.gRange = range; c.gHysteresis = 0.2; c.gRelease = 0.5;
            ref::Ctl r; r.gThrDbu = 0; r.rangePot = range; r.hystPot = 0.2; r.gRelPot = 0.5;
            const Env env = [X](double t) { return t < 0.2 ? 25.0 : X; };
            std::vector<double> am, ar; runModelGate(c, env, f, 3.0, 48000, &am); runRefGate(r, env, f, 3.0, 192000, &ar);
            double mm = 0, mr = 0; for (size_t i = (size_t)(2.0 * 48000); i < am.size(); ++i) mm = std::max(mm, am[i]); for (size_t i = (size_t)(2.0 * 192000); i < ar.size(); ++i) mr = std::max(mr, ar[i]);
            std::printf("  +%2.0f: %4.1f/%4.1f", X, mm, mr);
        }
        std::printf("   (model/circuit)\n");
    }

    // ------------------------------------------------------------------ E6: expander static curve and ripple
    std::printf("\nE6 EXPANDER static (1 kHz) and ripple at low frequency; range 50 dB, REL 0.0\n");
    for (double below : {3.0, 6.0, 10.0, 15.0, 20.0, 30.0}) {
        vrdyn::Controls c; c.gateIn = true; c.gThreshold = 25.0 / 40.0; c.gRange = 1.0; c.gHysteresis = 0.0; c.gRelease = 0.0;
        ref::Ctl r; r.gThrDbu = 0; r.rangePot = 1.0; r.expand = true; r.gRelPot = 0.0;
        const Env env = [below](double) { return -below; };
        std::vector<double> am, ar; runModelGate(c, env, 1000, 2.0, 48000, &am); runRefGate(r, env, 1000, 2.0, 192000, &ar);
        auto stats = [](const std::vector<double>& a, size_t from, double& mean, double& pp) { double lo = 1e9, hi = -1e9, s = 0; for (size_t i = from; i < a.size(); ++i) { lo = std::min(lo, a[i]); hi = std::max(hi, a[i]); s += a[i]; } mean = s / (a.size() - from); pp = hi - lo; };
        double m1, p1, m2, p2; stats(am, (size_t)(1.5 * 48000), m1, p1); stats(ar, (size_t)(1.5 * 192000), m2, p2);
        std::vector<double> bm, br; runModelGate(c, env, 60, 2.0, 48000, &bm); runRefGate(r, env, 60, 2.0, 192000, &br);
        double m3, p3, m4, p4; stats(bm, (size_t)(1.5 * 48000), m3, p3); stats(br, (size_t)(1.5 * 192000), m4, p4);
        std::printf("  %2.0f dB below thr: 1 kHz GR model %5.2f (pp %.2f) circuit %5.2f (pp %.2f) | 60 Hz GR model %5.2f (pp %.2f) circuit %5.2f (pp %.2f)\n", below, m1, p1, m2, p2, m3, p3, m4, p4);
    }
    // ------------------------------------------------------------------ hysteresis law
    std::printf("\nHYST pot: pot | model dB | circuit dB (12.9 V * Rh/(43k+Rh) at %.4f V/dB)\n", ref::kLogV);
    for (double p : {0.1, 0.2, 0.4, 0.6, 0.8, 1.0}) { vrdyn::Controls c; c.gHysteresis = p; std::printf("  %.1f | %5.1f | %5.1f\n", p, vrdyn::gateHysteresisDb(c), ref::hystVolts(p) / ref::kLogV); }
    return 0;
}
