package io.github.aemiroo.cosmeticpets;

/** Small cosmetic hops, applied after the shared collision-aware follow motion. */
final class WinterMotion {
    private WinterMotion() {}
    static double hop(PetKind kind, long tick) {
        if (kind == PetKind.SNOWMAN) return 0.035 * (1 - Math.cos(2 * Math.PI * Math.floorMod(tick, 80) / 80.0));
        if (kind == PetKind.REINDEER) {
            int phase = Math.floorMod(tick, 40);
            if (phase >= 24) return 0;
            double t = phase / 24.0;
            return 0.28 * 4 * t * (1 - t);
        }
        return 0;
    }
}
