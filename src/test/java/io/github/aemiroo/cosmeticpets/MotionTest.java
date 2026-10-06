package io.github.aemiroo.cosmeticpets;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class MotionTest {
    @Test void slowsNearDestinationWithoutOvershooting() {
        double distance = 4;
        for (int i = 0; i < 100; i++) {
            double step = Motion.step(distance);
            assertTrue(step <= 0.9 && step <= distance);
            distance -= step;
        }
        assertTrue(distance < 0.001);
    }
    @Test void turnsAcrossAngleBoundaryByShortestRoute() {
        assertEquals(181, Motion.turn(179, -179, 24), 0.001);
        assertEquals(-181, Motion.turn(-179, 179, 24), 0.001);
        assertEquals(24, Motion.turn(0, 90, 24), 0.001);
        assertEquals(-90, Motion.heading(1, 0), 0.001);
    }
    @Test void encodedDeltasReachSamePositionWithoutDrift() {
        double client = Motion.quantize(-0.15);
        double previous = client;
        for (int i = 1; i <= 1000; i++) {
            double next = Motion.quantize(-0.15 + i * 0.037);
            double delta = next - previous;
            client += ((short) (delta * 4096)) / 4096.0;
            assertEquals(next, client, 1e-9);
            previous = next;
        }
    }
}
