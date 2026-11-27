// Fix check: EQ CPU per stereo frame (static knobs, EQ in / out), and one knob sweeping.
#include "FourBandDSP.h"
#include <chrono>
#include <cstdio>
#include <vector>
int main() {
    for (double fs : {44100.0, 48000.0, 96000.0, 192000.0}) {
        for (int scen = 0; scen < 3; ++scen) {
            FourBandDSP d; EqControls c{}; c[3].gain = 0.8; c[0].gain = 0.3; d.prepare(fs, c);
            const int n = (int)fs * 4, blk = 256; std::vector<float> l(blk), r(blk); float* p[2] = {l.data(), r.data()};
            double secs = 0;
            for (int i = 0; i < n; i += blk) {
                for (int j = 0; j < blk; ++j) l[j] = r[j] = (float)(0.1 * std::sin(0.01 * (i + j)));
                if (scen == 2) c[1].gain = 0.5 + 0.5 * std::sin(i / fs * 3.0);   // continuous automation of one band
                auto t0 = std::chrono::steady_clock::now();
                d.process(p, 2, blk, c, scen != 1, 0, 0);
                secs += std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
            }
            const char* name[3] = {"EQ in, static", "EQ out", "EQ in, LMF gain automated"};
            std::printf("fs %6.0f  %-28s %.3f us/frame = %5.2f %% of one core\n", fs, name[scen], secs / n * 1e6, 100.0 * secs / 4.0);
        }
    }
}
