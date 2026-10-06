package io.github.aemiroo.cosmeticpets;
final class Motion {
    private Motion() {}
    static double step(double distance) { return Math.min(0.55, distance * 0.25); }
    static float heading(double x, double z) { return (float) Math.toDegrees(Math.atan2(-x, z)); }
    static float turn(float current, float target, float maximum) {
        float difference = ((target - current) % 360 + 540) % 360 - 180;
        return current + Math.max(-maximum, Math.min(maximum, difference));
    }
    static double quantize(double position) { return Math.floor(position * 4096) / 4096; }
}
