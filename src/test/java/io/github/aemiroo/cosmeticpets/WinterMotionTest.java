package io.github.aemiroo.cosmeticpets;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class WinterMotionTest {
    @Test void snowmanLandsAndParticlesStayBounded() {
        assertEquals(0,WinterMotion.hop(PetKind.SNOWMAN,0));
        assertEquals(0.35,WinterMotion.hop(PetKind.SNOWMAN,11),1e-12);
        for (long tick=-64;tick<64;tick++) {
            int phase=Math.floorMod(tick,32);
            if (phase>=22) assertEquals(0,WinterMotion.hop(PetKind.SNOWMAN,tick));
            int particles=WinterMotion.snowParticles(tick);
            assertTrue(particles>=0 && particles<=5);
            if (phase>22) assertEquals(0,particles);
        }
    }
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
            assertTrue(snow>=0 && snow<=0.35);
            assertTrue(deer>=0 && deer<=0.28);
            assertEquals(snow,WinterMotion.hop(PetKind.SNOWMAN,tick+32),1e-12);
            assertEquals(deer,WinterMotion.hop(PetKind.REINDEER,tick+40),1e-12);
            if (Math.floorMod(tick,40)>=24) assertEquals(0,deer);
        }
    }
}
