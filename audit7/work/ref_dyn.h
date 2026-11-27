#pragma once
// AUDIT 7 reference model: the auditor's own reading of EX11495 / EX11493 / EX11494 (Book 1, 1.2 p7-8, p13-14, p25-26).
// Independent of vrdyn (DynamicsCircuit.h). Used only to quantify the differences; not production code.
#include <cmath>
#include <algorithm>
#include <array>

namespace ref {

constexpr double kVt = 0.025852;                                  // kT/q at 300 K
constexpr double kLogV = 32.5 * kVt * 0.11512925464970229;        // R20/R14 = 390k/12k -> 0.09673 V per dB
constexpr double kVc = (270.0 / 4300.0) / 0.0061;                 // 10.294 dB per volt at the VCA (R54/R50, 6.1 mV/dB)
constexpr double kMake = (270.0 / 3600.0) / 0.0061;               // 12.295 dB per volt (R54/R51)

struct Ctl {
    // compressor
    double thrDbu = 0;        // threshold for a sine (rms)
    double ratioPot = 1.0;    // 0..1, linear pot, CCW..CW
    double relPot = 0.3;      // 0..1
    bool autoRel = false;
    bool fast = false;
    // gate
    double gThrDbu = 0;
    double rangePot = 0.8;    // 0..1 -> 0..-4.9 V
    double hystPot = 0.2;     // 0..1 rheostat 0..10k
    bool expand = false;
    bool gFast = false;
    double gRelPot = 0.5;
};

// RATIO: FSP7/2 = OR node, FSP7/3 = wiper = junction R35 2k4 / R37 10k (EX11495); RV5b 10k lin, CCW end at SC0V (EX11494, inferred).
inline double ratioK(double pot) {
    pot = std::clamp(pot, 0.0, 1.0);
    const double top = (1.0 - pot) * 10e3, bot = pot * 10e3;
    const double ru = top <= 0 ? 0.0 : top * 2400.0 / (top + 2400.0);           // pot top section // R35
    const double rl = bot <= 0 ? 0.0 : bot * 10e3 / (bot + 10e3);               // pot bottom section // R37 into virtual earth
    if (rl <= 0) return 0.0;
    return rl / (ru + rl);
}
inline double ratioValue(double pot) { const double s = 1.0 - kLogV * kVc * ratioK(pot); return s <= 1e-9 ? 1e9 : 1.0 / s; }

// L/C RELEASE: RV6b 10k, CCW end = FSP7/4 (buffered C11), CW end via R52 120R to SC0V, wiper via R53 680R to SC0V and to
// FSP7/5 -> R47 3k9 into the virtual earth of IC4(1-3)/TR3. (R52/R53: cut-off "R.." on EX11494 + PL11494; inferred.)
inline double relAlpha(double pot) {
    pot = std::clamp(pot, 0.0, 1.0);
    const double gs = 1.0 / 680.0 + 1.0 / 3900.0;
    const double gdn = 1.0 / ((1.0 - pot) * 10e3 + 120.0);
    if (pot <= 1e-9) return 1.0;
    const double gup = 1.0 / (pot * 10e3);
    return gup / (gup + gdn + gs);
}
inline double relTau(double pot) { return 3900.0 * 3.3e-6 / relAlpha(pot); }     // seconds (time constant of the GR in dB)

// gate RELEASE wiper volts (11493 RV6b / R16 120R / R17 620R, +2.45 V at CCW), loaded by R89 30k
inline double gateRelVolts(double pot) {
    pot = std::clamp(pot, 0.0, 1.0);
    if (pot <= 1e-9) return 2.45;
    const double gup = 1.0 / (pot * 10e3), gdn = 1.0 / ((1.0 - pot) * 10e3 + 120.0), gs = 1.0 / 620.0 + 1.0 / 30e3;
    return 2.45 * gup / (gup + gdn + gs);
}
// HYSTERESIS: IC9(1) high (+13.5 V) -> D14 -> R96 43k -> RV3b rheostat (0 at CCW .. 10k at CW) to SC0V; R95 13k to pin 3 carries no current
inline double hystVolts(double pot) { const double rh = std::clamp(pot, 0.0, 1.0) * 10e3; return 12.9 * rh / (43e3 + rh); }

inline double logVolts(double xVolts, double thrDbu) {
    const double a = std::abs(xVolts);
    double dbu = a > 1e-12 ? 20.0 * std::log10(a / 0.7746) : -200.0;
    dbu -= 3.0103;                                   // threshold trim referred to a sine (rms)
    dbu = std::max(dbu, -80.0);
    return (dbu - thrDbu) * kLogV;
}

struct Comp {
    double fs = 192000;
    double v9 = 0, v10 = 0, v11 = 0;                 // C9 1u, C8//C10 2u, C11 3u3 (AUTO: series stack; normal: only C11)
    double vFast = 0, vAvg = -6, hold = 0;
    bool charging = false;
    void prepare(double r) { fs = r; v9 = v10 = v11 = 0; vFast = 0; vAvg = -6; hold = 0; }
    double top() const { return v9 + v10 + v11; }
    double tick(double vLog, const Ctl& c) {
        const double dt = 1.0 / fs;
        const double alpha = relAlpha(c.autoRel ? 1.0 : c.relPot);
        vAvg += (std::max(vLog, -8.0) - vAvg) * (1.0 - std::exp(-dt / 4.7e-3));
        const bool low = vAvg < -20.0 * kLogV;
        charging = false;
        const double iLong = 0.46e-6;
        if (!c.autoRel) {
            double v = v11; v9 = v10 = 0;
            const double rch = 1.0 / (1.0 / 1100.0 + 1.0 / 39e3 + 1.0 / 200e3);
            if (vLog > v) { charging = true; hold = 0.030; v += (vLog - v) * (1.0 - std::exp(-dt / (rch * 3.3e-6))); }
            else if (hold > 0) hold -= dt;
            else {
                double i = iLong; if (!low && v > 0) i += alpha * v / 3900.0;
                v -= i * dt / 3.3e-6; v = std::max(v, -0.3);             // D8 clamp
            }
            v11 = v;
        } else {
            const double R = top(), S = v10 + v11, T = v11;
            const double g1 = 1.0 / 6700.0, g2 = 1.0 / 39e3, g3 = 1.0 / 200e3;
            const double pOpen = (R * g1 + S * g2 + T * g3) / (g1 + g2 + g3);
            double P = pOpen;
            if (vLog > pOpen) { P = vLog; charging = true; hold = 0.030; }
            const double i1 = (P - R) * g1, i2 = (P - S) * g2, i3 = (P - T) * g3;
            double iRel = 0;
            if (!charging) { if (hold > 0) hold -= dt; else { iRel = iLong; if (!low && R > 0) iRel += alpha * R / 3900.0; if (R <= -0.3) iRel = 0; } }
            v9 += (i1 - iRel) * dt / 1e-6;
            v10 += (i1 - iRel + i2) * dt / 2e-6;
            v11 += (i1 - iRel + i2 + i3) * dt / 3.3e-6;
        }
        {   // fast loop D2 / R26 (+R28) / C13 / R34
            const double c13 = 22e-9, rChg = c.fast ? 3000.0 : 30000.0;
            const double drive = vLog - 0.4;
            if (drive > vFast) vFast += (drive - vFast) * (1.0 - std::exp(-dt / (rChg * c13)));
            vFast *= std::exp(-dt / (560e3 * c13));
        }
        return std::max({top(), vFast, 0.0});
    }
    double grDb(double vOr, const Ctl& c) const { return kVc * ratioK(c.ratioPot) * vOr; }
};

struct Gate {
    double fs = 192000;
    double vPk = 0, vG = 0;          // detector (IC9 7/8), gate CV (C27 negative side, 0 .. vRange)
    bool open = false; double hold = 0; bool primed = false;
    void prepare(double r) { fs = r; vPk = 0; vG = 0; open = false; hold = 0; primed = false; }
    // returns GR in dB
    double tick(double vLog, const Ctl& c) {
        const double dt = 1.0 / fs;
        const double vRange = -4.9 * std::clamp(c.rangePot, 0.0, 1.0);
        if (!primed) { vPk = vRange; vG = vRange; primed = true; }
        if (vLog > vPk) vPk = vLog; else vPk += (vRange - vPk) * (1.0 - std::exp(-dt / (6.8e6 * 4.7e-9)));   // R90 returns to RANGE
        const double att = (c.gFast ? 24.3e3 : 2.43e3) * dt;                     // TR6: 25 dB per 1 ms / 100 us
        const double rel = gateRelVolts(c.gRelPot) / (30e3 * 1e-6) * dt;         // R89 30k, C27 1u
        if (!c.expand) {
            const double hv = hystVolts(c.hystPot);
            const bool was = open;
            if (open) { if (vPk < 0) open = false; } else { if (vPk > hv) open = true; }
            if (open) { vG = std::min(0.0, vG + att); hold = 0.030; }           // C46 held discharged while the trigger is low
            else { if (was) hold = 0.030; if (hold > 0) hold -= dt; else vG = std::max(vRange, vG - rel); }
        } else {
            const double target = std::clamp(vPk, vRange, 0.0);
            const double e = target - vG;                                         // >0: too much attenuation
            if (e > 0.0114) { vG = std::min(target, vG + att); hold = 0.030; }
            else if (e < -0.0176) { if (hold > 0) hold -= dt; else vG = std::max(target, vG - rel); }   // IC10(8) comparator at +8 V / 455
            else hold = 0.030;
            open = vPk > 0;
        }
        return -vG * kVc;
    }
};

} // namespace ref
