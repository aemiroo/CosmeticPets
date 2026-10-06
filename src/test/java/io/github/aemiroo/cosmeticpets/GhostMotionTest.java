package io.github.aemiroo.cosmeticpets;
import org.bukkit.Location;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class GhostMotionTest {
    @Test void playerLookPitchCannotTiltGhostOrMutatePlayerLocation() {
        Location player = new Location(null, 1, 2, 3, 123, 65);
        Location ghost = GhostMotion.upright(player);
        assertEquals(0, ghost.getPitch());
        assertEquals(123, ghost.getYaw());
        assertEquals(65, player.getPitch());
        assertEquals(player.toVector(), ghost.toVector());
    }
    @Test void bobIsContinuousAndStaysWithinAmplitude() {
        for (long tick = 0; tick < 2000; tick++) {
            assertTrue(Math.abs(GhostMotion.bob(tick)) <= 0.12);
            assertTrue(Math.abs(GhostMotion.bob(tick + 1) - GhostMotion.bob(tick)) < 0.0073);
        }
    }
    @Test void smallAnimationStepsAreNotDroppedAndCatchupSpeedIsBounded() {
        assertTrue(GhostMotion.step(0.01) > 0);
        assertEquals(0.45, GhostMotion.step(10), 1e-9);
        assertTrue(GhostMotion.step(0.01) < 0.01);
    }
}
