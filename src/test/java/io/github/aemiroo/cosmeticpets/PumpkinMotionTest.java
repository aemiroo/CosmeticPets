package io.github.aemiroo.cosmeticpets;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class PumpkinMotionTest {
    @Test void hopHasGroundPauseAndStaysBounded() {
        assertEquals(0,PumpkinMotion.hop(0),1e-9);
        assertEquals(0.5,PumpkinMotion.hop(12),1e-9);
        for(int i=0;i<36;i++) {
            assertTrue(PumpkinMotion.hop(i)>=0 && PumpkinMotion.hop(i)<=0.5);
            if(i>=24) assertEquals(0,PumpkinMotion.hop(i),1e-9);
            assertEquals(PumpkinMotion.hop(i),PumpkinMotion.hop(i+36),1e-9);
        }
    }
    @Test void squashesOnLandingStretchesInAirAndKeepsVolume() {
        assertTrue(PumpkinMotion.scaleY(12)>1);
        assertTrue(PumpkinMotion.scaleY(27)<1);
        for(int i=0;i<36;i++) {
            float y=PumpkinMotion.scaleY(i), xz=PumpkinMotion.scaleXZ(y);
            assertTrue(y>=0.779 && y<=1.081);
            assertEquals(1,xz*xz*y,1e-6);
        }
    }
}
