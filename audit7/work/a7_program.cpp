// AUDIT 7: plugin model against the auditor's reference on programme material (demo drum loop of the project).
#include "DynamicsCircuit.h"
#include "ref_dyn.h"
#include <cstdio>
#include <vector>
#include <cstdint>
#include <cstring>
#include <string>

static bool readWav(const char* path, std::vector<float>& l, double& fs) {
    FILE* f = std::fopen(path, "rb"); if (!f) return false;
    std::vector<unsigned char> d; unsigned char buf[65536]; size_t n; while ((n = std::fread(buf, 1, sizeof buf, f)) > 0) d.insert(d.end(), buf, buf + n); std::fclose(f);
    size_t p = 12; int ch = 2, bits = 16; fs = 48000;
    while (p + 8 <= d.size()) { const uint32_t sz = d[p + 4] | (d[p + 5] << 8) | (d[p + 6] << 16) | ((uint32_t)d[p + 7] << 24);
        if (!std::memcmp(&d[p], "fmt ", 4)) { ch = d[p + 10]; fs = d[p + 12] | (d[p + 13] << 8) | (d[p + 14] << 16); bits = d[p + 22]; }
        if (!std::memcmp(&d[p], "data", 4)) { const size_t frames = sz / (ch * bits / 8); l.resize(frames); for (size_t i = 0; i < frames; ++i) { const size_t o = p + 8 + i * ch * 2; l[i] = (int16_t)(d[o] | (d[o + 1] << 8)) / 32768.0f; } return bits == 16; }
        p += 8 + sz + (sz & 1); }
    return false;
}

int main(int argc, char** argv) {
    std::vector<float> x; double fs = 48000;
    if (argc < 2 || !readWav(argv[1], x, fs)) { std::printf("cannot read wav\n"); return 1; }
    // loop the file 3 times so that the state is periodic; analyse the last pass
    const size_t n1 = x.size(); std::vector<float> in; for (int k = 0; k < 3; ++k) in.insert(in.end(), x.begin(), x.end());
    const double scale = 0.7746 * std::pow(10.0, 18.0 / 20.0);
    std::printf("file %.1f s at %.0f Hz, 0 dBFS = +18 dBu\n", n1 / fs, fs);

    std::printf("\nCOMPRESSOR thr -4 dBu, ratio pot 0.8 (5:1): mean GR model / reference, mean |diff|, max |diff|, share of time with |diff| > 2 dB\n");
    struct Case { double rel; bool au; };
    for (Case cs : {Case{0.0, false}, Case{0.2, false}, Case{0.39, false}, Case{0.6, false}, Case{0.8, false}, Case{1.0, true}}) {
        vrdyn::Controls c; c.lcIn = true; c.cThreshold = 0.2; c.cRatio = 0.8; c.cRelease = cs.au ? 1.0 : cs.rel;
        ref::Ctl r; r.thrDbu = vrdyn::compThresholdDbu(c); r.ratioPot = 0.8; r.relPot = cs.rel; r.autoRel = cs.au;
        vrdyn::CompSidechain m; m.prepare(fs); ref::Comp q; q.prepare(fs);
        const double k = vrdyn::ratioFraction(c); double sm = 0, sr = 0, sd = 0, mx = 0; size_t over = 0, cnt = 0;
        for (size_t i = 0; i < in.size(); ++i) {
            const double v = in[i] * scale;
            const double gm = vrdyn::kVcDbPerVolt * k * m.tick(vrdyn::logLevelVolts(v, vrdyn::compThresholdDbu(c)), c);
            const double gr = q.grDb(q.tick(ref::logVolts(v, r.thrDbu), r), r);
            if (i >= 2 * n1) { sm += gm; sr += gr; const double d = std::abs(gm - gr); sd += d; mx = std::max(mx, d); if (d > 2.0) ++over; ++cnt; }
        }
        std::printf("  REL pot %s: mean GR %.2f / %.2f dB, mean |diff| %.2f dB, max %.1f dB, |diff|>2 dB for %.0f %% of the time\n", cs.au ? "AUTO" : std::to_string(cs.rel).substr(0, 4).c_str(), sm / cnt, sr / cnt, sd / cnt, mx, 100.0 * over / cnt);
    }
    std::printf("\nGATE thr -6 dBu, hyst 5 dB: mean GR model / reference, mean |diff|, share of time with |diff| > 6 dB\n");
    for (double range : {0.4, 0.8}) for (double rel : {0.0, 0.3, 0.6}) for (bool exp_ : {false, true}) {
        vrdyn::Controls c; c.gateIn = true; c.gThreshold = 19.0 / 40.0; c.gRange = range; c.gHysteresis = exp_ ? 0.0 : 0.2; c.gRelease = rel;
        ref::Ctl r; r.gThrDbu = vrdyn::gateThresholdDbu(c); r.rangePot = range; r.hystPot = 0.2; r.expand = exp_; r.gRelPot = rel;
        vrdyn::GateSidechain m; m.prepare(fs); ref::Gate q; q.prepare(fs); double sm = 0, sr = 0, sd = 0; size_t over = 0, cnt = 0;
        for (size_t i = 0; i < in.size(); ++i) {
            const double v = in[i] * scale; const double gm = m.tick(vrdyn::logLevelVolts(v, vrdyn::gateThresholdDbu(c)), c), gr = q.tick(ref::logVolts(v, r.gThrDbu), r);
            if (i >= 2 * n1) { sm += gm; sr += gr; const double d = std::abs(gm - gr); sd += d; if (d > 6.0) ++over; ++cnt; }
        }
        std::printf("  %s range %2.0f dB REL pot %.1f: mean GR %.2f / %.2f dB, mean |diff| %.2f dB, |diff|>6 dB for %.0f %% of the time\n", exp_ ? "EXP " : "GATE", 4.9 * 10.29 * range, rel, sm / cnt, sr / cnt, sd / cnt, 100.0 * over / cnt);
    }
    return 0;
}
