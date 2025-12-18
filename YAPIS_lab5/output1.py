# Сгенерированный код из геометрического языка
import math

# Определение геометрических классов
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Point({self.x}, {self.y})"

    def __repr__(self):
        return self.__str__()


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __str__(self):
        return f"Line({self.p1}, {self.p2})"


class Circle:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def __str__(self):
        return f"Circle({self.center}, {self.radius})"


class Polygon:
    def __init__(self, *points):
        self.points = points

    def __str__(self):
        return f"Polygon({len(self.points)} points)"


# Встроенные геометрические функции
def distance(p1, p2):
    """Расстояние между двумя точками"""
    if isinstance(p1, Point) and isinstance(p2, Point):
        return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
    return 0.0


def intersection(l1, l2):
    """Точка пересечения двух линий"""
    if isinstance(l1, Line) and isinstance(l2, Line):
        # Упрощенная реализация
        x1, y1 = l1.p1.x, l1.p1.y
        x2, y2 = l1.p2.x, l1.p2.y
        x3, y3 = l2.p1.x, l2.p1.y
        x4, y4 = l2.p2.x, l2.p2.y

        denom = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
        if denom == 0:
            return None

        x = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denom
        y = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denom

        return Point(x, y)
    return None


def belongs(point, geometry):
    """Проверяет, принадлежит ли точка геометрической фигуре"""
    if not isinstance(point, Point):
        return False

    if isinstance(geometry, Point):
        return point.x == geometry.x and point.y == geometry.y
    elif isinstance(geometry, Line):
        # Упрощенная проверка для линии
        return True
    elif isinstance(geometry, Circle):
        dx = point.x - geometry.center.x
        dy = point.y - geometry.center.y
        return dx*dx + dy*dy <= geometry.radius*geometry.radius
    elif isinstance(geometry, Polygon):
        # Упрощенная проверка для многоугольника
        return True

    return False



def calculateDistance():
    p1 = Point(1, 2)
    p2 = Point(4, 6)
    d = distance(p1, p2)
    return d


def main():
    result = calculateDistance()
    print(result)


# Запуск программы
if __name__ == "__main__":
    # Поиск функции main
    if 'main' in globals() and callable(main):
        main()
    else:
        print("Функция main не найдена")