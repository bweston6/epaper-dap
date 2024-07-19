from functools import total_ordering


@total_ordering
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, other):
        assert isinstance(other, (int, float, complex))
        self._x = other

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, other):
        assert isinstance(other, (int, float, complex))
        self._y = other

    @property
    def tuple(self):
        return (self.x, self.y)

    @tuple.setter
    def tuple(self, other):
        self.x, self.y = other

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.tuple == other.tuple

    def __lt__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.x < other.x and self.y < other.y

    def __str__(self):
        return f"{type(self)} ({self.x}, {self.y})"


class Rectangle:
    def __init__(self, point1, point2):
        assert isinstance(point1, Point)
        assert isinstance(point2, Point)
        self.point1 = point1
        self.point2 = point2

    @property
    def point1(self):
        return self._point1

    @point1.setter
    def point1(self, new_point):
        assert isinstance(new_point, Point)
        self._point1 = new_point

    @property
    def point2(self):
        return self._point2

    @point2.setter
    def point2(self, new_point):
        assert isinstance(new_point, Point)
        self._point2 = new_point
