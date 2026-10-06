package io.github.aemiroo.cosmeticpets;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class CollisionTest {
    @Test void sweptMovementDoesNotTunnelThroughThinWall() {
        var from = new Collision.Point(0,0,0);
        var end = new Collision.Point(0.9,0,0);
        var reached = Collision.sweep(from,end,p -> p.x() < 0.4 || p.x() > 0.6);
        assertTrue(reached.x() < 0.4);
    }
    @Test void slidesAlongWallWithoutEnteringIt() {
        var from = new Collision.Point(0,0,0);
        var end = new Collision.Point(0.9,0,0.9);
        var reached = Collision.slide(from,end,p -> p.x() < 0.4);
        assertTrue(reached.x() < 0.4);
        assertEquals(0.9,reached.z(),1e-9);
    }
    @Test void clearRouteReachesDestinationAndBlockedRouteStaysStill() {
        var from = new Collision.Point(0,0,0);
        var end = new Collision.Point(0.9,0.3,-0.4);
        assertTrue(Collision.distance(end,Collision.slide(from,end,p -> true)) < 1e-12);
        assertEquals(from,Collision.slide(from,end,p -> false));
    }
}
