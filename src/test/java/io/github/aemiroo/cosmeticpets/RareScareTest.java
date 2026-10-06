package io.github.aemiroo.cosmeticpets;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class RareScareTest {
    @Test void exactlyOneWinningOutcomeWithRequestedUniformBound() {
        int[] calls={0};
        assertTrue(RareScare.roll(bound -> { calls[0]++; assertEquals(100_000_000,bound); return 0; }));
        assertEquals(1,calls[0]);
        assertFalse(RareScare.roll(bound -> 1));
        assertFalse(RareScare.roll(bound -> bound/2));
        assertFalse(RareScare.roll(bound -> bound-1));
    }
    @Test void hopReturnsToBaseAndDoesNotOvershoot() {
        assertEquals(0,RareScare.hop(RareScare.DURATION),1e-9);
        assertEquals(0,RareScare.hop(0),1e-9);
        assertEquals(0.35,RareScare.hop(10),1e-9);
        for(int remaining=0;remaining<=RareScare.DURATION;remaining++) {
            assertTrue(RareScare.hop(remaining)>=0);
            assertTrue(RareScare.hop(remaining)<=0.35);
        }
    }
}
