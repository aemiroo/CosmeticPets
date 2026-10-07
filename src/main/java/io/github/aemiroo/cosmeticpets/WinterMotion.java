package io.github.aemiroo.cosmeticpets;

/** Small cosmetic hops, applied after the shared collision-aware follow motion. */
final class WinterMotion {
    private WinterMotion() {}
    static double hop(PetKind kind, long tick) {
        if (kind == PetKind.SNOWMAN) return 0.035 * (1 - Math.cos(2 * Math.PI * Math.floorMod(tick, 80) / 80.0));
        return 0;
    }
    static int walkFrame(double distance) {
        return Math.floorMod((int)Math.floor(distance / 0.9 * 12),12);
    }
}
