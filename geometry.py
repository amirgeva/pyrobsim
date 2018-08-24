from PyQt5 import QtGui
from vtypes import vec2


def norm(p):
    return vec2(p.x(), p.y()).norm()


class Segment:
    def __init__(self, *args):
        if isinstance(args[0], QtGui.QPolygonF):
            poly = args[0]
            i = args[1]
            self.p1 = vec2(poly.at(i))
            self.p2 = vec2(poly.at((i + 1) % poly.size()))
        if isinstance(args[0], vec2):
            self.p1 = args[0]
            self.p2 = args[1]
        D = self.p2 - self.p1;
        self.N = vec2(-D.y, D.x).normalized()
        self.d = self.p1 * self.N


def check_segment_intersection(s1, s2):
    return (s1.p1 * s2.N - s2.d) * (s1.p2 * s2.N - s2.d) < 0 and (s2.p1 * s1.N - s1.d) * (s2.p2 * s1.N - s1.d) < 0


def check_poly_intersection(p1, p2):
    s1 = [Segment(p1, i) for i in range(p1.size())]
    s2 = [Segment(p2, i) for i in range(p2.size())]
    for si in s1:
        for sj in s2:
            if check_segment_intersection(si, sj):
                return True
    return False


def check_intersection(o1, o2):
    dist = norm(o1.pos - o2.pos)
    sum_rad = o1.radius + o2.radius
    if dist > sum_rad:
        return False
    return check_poly_intersection(o1.poly, o2.poly)


def intersection_distance(ray_seg, seg):
    p = ray_seg.p1
    r = ray_seg.p2 - ray_seg.p1
    q = seg.p1
    s = seg.p2 - seg.p1
    t = (q - p).cross(s / r.cross(s))
    return t


def ray_intersection(start, dir, length, obj):
    s = Segment(start, start + dir * length)
    poly = obj.poly
    sp = [Segment(poly, i) for i in range(poly.size())]
    min_t = -0.01
    for side in sp:
        if check_segment_intersection(s, side):
            t = intersection_distance(s, side)
            if t < min_t or min_t < 0:
                min_t = t
    return min_t * length
