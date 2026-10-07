package io.github.aemiroo.cosmeticpets;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class WinterMotionTest {
    @Test void gaitAdvancesWithTravelAndWrapsAtOneStride() {
        assertEquals(0,WinterMotion.walkFrame(0));
        assertEquals(3,WinterMotion.walkFrame(0.225));
        assertEquals(6,WinterMotion.walkFrame(0.45));
        assertEquals(0,WinterMotion.walkFrame(0.9));
        assertEquals(0,WinterMotion.hop(PetKind.REINDEER,12));
    }
    @Test void motionIsBoundedPeriodicAndReindeerRests() {
        for (long tick=-160;tick<160;tick++) {
            double snow=WinterMotion.hop(PetKind.SNOWMAN,tick), deer=WinterMotion.hop(PetKind.REINDEER,tick);
            assertTrue(snow>=0 && snow<=0.07);
            assertTrue(deer>=0 && deer<=0.28);
            assertEquals(snow,WinterMotion.hop(PetKind.SNOWMAN,tick+80),1e-12);
            assertEquals(deer,WinterMotion.hop(PetKind.REINDEER,tick+40),1e-12);
            if (Math.floorMod(tick,40)>=24) assertEquals(0,deer);
        }
    }
}
