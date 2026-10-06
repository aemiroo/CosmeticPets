package io.github.aemiroo.cosmeticpets;
import java.util.function.Predicate;
final class Collision {
    record Point(double x, double y, double z) {
        Point add(double dx, double dy, double dz) { return new Point(x + dx, y + dy, z + dz); }
    }
    static Point sweep(Point start, Point end, Predicate<Point> clear) {
        double dx = end.x - start.x, dy = end.y - start.y, dz = end.z - start.z;
        int steps = Math.max(1, (int) Math.ceil(Math.sqrt(dx*dx + dy*dy + dz*dz) / 0.1));
        Point current = start;
        for (int i = 0; i < steps; i++) {
            Point next = current.add(dx/steps, dy/steps, dz/steps);
            if (!clear.test(next)) break;
            current = next;
        }
        return current;
    }
    static Point slide(Point start, Point end, Predicate<Point> clear) {
        Point direct = sweep(start, end, clear);
        if (distance(direct, end) < 0.000001) return direct;
        Point xFirst = sweep(start, new Point(end.x, start.y, start.z), clear);
        xFirst = sweep(xFirst, new Point(xFirst.x, end.y, end.z), clear);
        Point zFirst = sweep(start, new Point(start.x, start.y, end.z), clear);
        zFirst = sweep(zFirst, new Point(end.x, end.y, zFirst.z), clear);
        Point best = distance(xFirst, end) < distance(zFirst, end) ? xFirst : zFirst;
        return distance(direct, end) < distance(best, end) ? direct : best;
    }
    static double distance(Point a, Point b) {
        return Math.pow(a.x-b.x,2) + Math.pow(a.y-b.y,2) + Math.pow(a.z-b.z,2);
    }
}
