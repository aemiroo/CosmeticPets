package io.github.aemiroo.cosmeticpets;
import org.bukkit.Location;
final class GhostMotion {
    private GhostMotion() {}
    static Location upright(Location location) {
        Location result = location.clone();
        result.setPitch(0);
        return result;
    }
    static double bob(long tick) { return Math.sin(tick * 0.06) * 0.12; }
    static double step(double distance) { return Math.min(0.45, distance * 0.55); }
}
