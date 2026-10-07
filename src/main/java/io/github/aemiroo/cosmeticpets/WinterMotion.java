package io.github.aemiroo.cosmeticpets;

/** Small cosmetic hops, applied after the shared collision-aware follow motion. */
final class WinterMotion {
    private WinterMotion() {}
    static double hop(PetKind kind, long tick) {
        if (kind == PetKind.SNOWMAN) {
            int phase = Math.floorMod(tick,32);
            if (phase >= 22) return 0;
            double t = phase / 22.0;
            return 0.35 * 4 * t * (1-t);
        }
        return 0;
    }
    static int walkFrame(double distance) {
        return Math.floorMod((int)Math.floor(distance / 0.9 * 12),12);
    }
}
