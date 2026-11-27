// Fix check: half-band resampler passband / image rejection / delay (up -> down round trip and up alone).
#include "Halfband.h"
#include <cstdio>
#include <vector>
static const double kPi = 3.14159265358979323846;
int main() {
    const auto& c = hb::coefficients();
    std::printf("coefs:"); for (double v : c) std::printf(" %.6f", v); std::printf("\n");
    const double fs = 48000;
    for (double f : {100.0, 1000.0, 10000.0, 18000.0, 20000.0, 21000.0, 22000.0}) {
        hb::Upsampler u; hb::Downsampler d; const int n = 48000; double s = 0, img = 0; double ci = 0, cq = 0;
        std::vector<double> up(2 * n);
        for (int i = 0; i < n; ++i) {
            const double x = std::sin(2 * kPi * f * i / fs); double y0, y1; u.process(x, y0, y1); up[2 * i] = y0; up[2 * i + 1] = y1;
            const double y = d.process(y0, y1);
            if (i >= n / 2) { s += y * y; ci += y * std::cos(2 * kPi * f * i / fs); cq += y * std::sin(2 * kPi * f * i / fs); }
        }
        // image at 2fs - f in the upsampled signal
        double ii = 0, iq = 0, mi = 0, mq = 0;
        for (int m = n; m < 2 * n; ++m) { const double t = m / (2 * fs); ii += up[m] * std::cos(2 * kPi * (fs - f) * t); iq += up[m] * std::sin(2 * kPi * (fs - f) * t);
            mi += up[m] * std::cos(2 * kPi * f * t); mq += up[m] * std::sin(2 * kPi * f * t); }
        const double gain = std::sqrt(2 * s / (n / 2)), phase = std::atan2(-ci, cq);
        const double delay = -phase / (2 * kPi * f) * fs;
        std::printf("f %6.0f Hz: round trip %+.4f dB, delay %.2f samples; up image %.1f dB\n", f, 20 * std::log10(gain), delay,
                    20 * std::log10(std::hypot(ii, iq) / std::hypot(mi, mq)));
        (void)img;
    }
}
