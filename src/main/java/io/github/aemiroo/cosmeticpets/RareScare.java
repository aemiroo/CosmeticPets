package io.github.aemiroo.cosmeticpets;
import java.util.function.IntUnaryOperator;
final class RareScare {
    static final int ODDS = 100_000_000;
    static final int DURATION = 20;
    private RareScare() {}
    static boolean roll(IntUnaryOperator random) { return random.applyAsInt(ODDS) == 0; }
    static double hop(int remaining) {
        return Math.sin(Math.PI * (DURATION - remaining) / DURATION) * 0.35;
    }
}
