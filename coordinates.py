import math


class point:
    def __init__(self, lat, long):
        self.lat = lat
        self.long = long

    def __str__(self):
        return "[{}, {}]".format(self.lat, self.long)


def calculateDistance(p1: point, p2: point, units = "km"):
    if units == "km":
        R = 6371
    elif units =="miles":
        R = 3958.756
    else:
        R = 6371
    d = math.acos( math.sin(p1.lat) * math.sin(p2.lat) + math.cos(p1.lat) * math.cos(p2.lat) * math.cos(p1.long-p2.long))
    return math.radians(d)*R


#получает координаты и строит квадратную область вокруг данной точки для поиска заправок в данном квадрате
def getBBox(p: point):
    dist = 1  # Диапазон в котором искать заправки(в км)
    long1 = p.long - dist / abs(math.cos(math.radians(p.lat)) * 111.0)  # 1 градус широты = 111 км
    long2 = p.long + dist / abs(math.cos(math.radians(p.lat)) * 111.0)
    lat1 = p.lat - (dist / 111.0)
    lat2 = p.lat + (dist / 111.0)
    return "{},{}~{},{}".format(long1, lat1, long2, lat2)


