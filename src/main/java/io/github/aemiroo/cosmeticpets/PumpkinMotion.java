package io.github.aemiroo.cosmeticpets;
final class PumpkinMotion {
    static final int CYCLE = 36;
    private PumpkinMotion() {}
    static double hop(long tick) {
        int phase = Math.floorMod(tick, CYCLE);
        if (phase >= 24) return 0;
        double t = phase / 24.0;
        return 4 * 0.5 * t * (1 - t);
    }
    static float scaleY(long tick) {
        int phase = Math.floorMod(tick, CYCLE);
        if (phase < 24) return (float) (1 + 0.08 * Math.sin(Math.PI * phase / 24.0));
        if (phase < 30) return (float) (1 - 0.22 * Math.sin(Math.PI * (phase - 24) / 6.0));
        if (phase >= 32) return (float) (1 - 0.12 * Math.sin(Math.PI * (phase - 32) / 4.0));
        return 1;
    }
    static float scaleXZ(float scaleY) { return (float) (1 / Math.sqrt(scaleY)); }
}
