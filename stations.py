import coordinates


class station:
    def __init__(self, name, companyID, coords, address):
        self.name = name
        self.companyID = companyID
        self.coordinates = coords
        self.address = address

    def __str__(self):
        return "[{}, {}, {}]".format(self.name, self.companyID, self.coordinates)

    def __repr__(self):
        return str(self)


def parseStationsFromJSON(json):
    stations = []
    for object in json['features']:
        coords = object['geometry']['coordinates']
        p = coordinates.point(coords[0], coords[1])
        name = object['properties']['CompanyMetaData']['name']
        companyID = object['properties']['CompanyMetaData']['id']
        address = object['properties']['CompanyMetaData']['address']
        st = station(name, companyID, p, address)
        stations.append(st)
    return stations
