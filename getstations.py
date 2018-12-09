import psycopg2
import requests
import coordinates
import stations
import random
import strgen

apiKey = 'yandexAPIkeyHere'
constr = "postgres://{user}:{password}@{host}:5432/{dbname}?sslmode=disable".format(user="user",
                                                                                      password="user",
                                                                                      host="127.0.0.1",
                                                                                      dbname="stations-example")


# Получаем все заправке в городе
def getAllStations(city):
    url = "https://search-maps.yandex.ru/v1/?text=заправка, {city}&type=biz&lang=ru_RU&results=200&apikey={apikey}".format(
        apikey=apiKey,
        city=city)
    response = requests.get(url)
    return response.json()


# Получаем заправки недалеко от точки
def getStationsInBBox(p: coordinates.point):
    box = coordinates.getBBox(p)
    url = "https://search-maps.yandex.ru/v1/?text=заправка&type=biz&lang=ru_RU&results=200&bbox={bbox}&apikey={apikey}".format(
        apikey=apiKey, bbox=box)
    response = requests.get(url)
    return response.json()


# Мохраняем станции в базе
def addStationsToDatabase(db, sts):
    cursor = db.cursor()
    basequerystr = 'insert into stations (name, company_id, address, cost80, cost92, cost95, cost98) values '
    arglist = []
    for o in sts:
        cost80 = float(str(random.randint(45, 55)) + "." + str(random.randint(0, 100)))
        cost92 = float(str(random.randint(45, 55)) + "." + str(random.randint(0, 100)))
        cost95 = float(str(random.randint(45, 55)) + "." + str(random.randint(0, 100)))
        cost98 = float(str(random.randint(45, 55)) + "." + str(random.randint(0, 100)))
        name = o.name.encode("utf-8").decode("utf-8")
        address = o.address.encode("utf-8").decode("utf-8")
        stringa = cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s)", (name, int(o.companyID), address, cost80, cost92, cost95, cost98))
        arglist.append(stringa.decode("utf-8"))
    args = ",".join(arglist)
    cursor.execute(basequerystr+args)
    db.commit()
    cursor.close()


# Ищет все заправки в городе
def saveStationsInCity(db, city):
    jsonStations = getAllStations(city)
    stationList = stations.parseStationsFromJSON(jsonStations)
    addStationsToDatabase(db, stationList)


# Создает временную таблицу в которой будут хранится дистанции от точки до заправки
def createTmpTable(db, sts, point:coordinates.point):
    tablename = strgen.StringGenerator("[a-z]{15}").render()
    cursor = db.cursor()
    cursor.execute("create table {tname} (id bigint, distance integer);".format(tname=tablename))
    basequerystr = 'insert into {tname} (id, distance) values '.format(tname=tablename)
    arglist = []
    for o in sts:
        distance = coordinates.calculateDistance(point, o.coordinates)
        stringa = cursor.mogrify("(%s,%s)", (int(o.companyID), distance))
        arglist.append(stringa.decode("utf-8"))
    args = ",".join(arglist)
    cursor.execute(basequerystr+args)
    db.commit()
    cursor.close()
    return tablename


# Ищет лучшую заправку для пользователя на заданный объем бака
def getBestStation(db, plist, userID, L):
    BestStation = None
    for p in plist:
        jsonsts = getStationsInBBox(p)
        sts = stations.parseStationsFromJSON(jsonsts)
        if len(sts) == 0:
            continue
        tname = createTmpTable(db, sts, p)
        cursor = db.cursor()
        querystr = """
        select s.company_id, s.name, s.address, 
            case u.fuel 
                when '80' then %(L)s*s.cost80 + u.AvgConsumption/100*d.distance*s.cost80
                when '92' then %(L)s*s.cost92 + u.AvgConsumption/100*d.distance*s.cost92
                when '95' then %(L)s*s.cost95 + u.AvgConsumption/100*d.distance*s.cost95
                when '98' then %(L)s*s.cost98 + u.AvgConsumption/100*d.distance*s.cost98
            end
        as cost from stations s 
        join {distanceTname} d on d.id = s.company_id
        join users u on u.id = %(userid)s
        order by cost
        """.format(distanceTname=tname)
        cursor.execute(querystr, {'L': L, 'userid':userID})
        result = cursor.fetchone()
        if result is not None:
            if BestStation is not None and result[3] < BestStation[3]:
                BestStation = result
            elif BestStation is None:
                BestStation = result
        cursor.execute("drop table {tablename}".format(tablename=tname))
        db.commit()
        cursor.close()
    return BestStation


# Connect к базе
db = psycopg2.connect(constr)
# Поиск заправок в Москве
saveStationsInCity(db, 'Москва')

# "Создание" Маршрута
plist = []
plist.append(coordinates.point(55.844642, 37.378689))
plist.append(coordinates.point(55.849842, 37.368173))
plist.append(coordinates.point(55.844868, 37.378129))
plist.append(coordinates.point(55.839846, 37.386369))
plist.append(coordinates.point(55.831876, 37.384567))
plist.append(coordinates.point(55.822213, 37.385597))

# Тестовые данные пользователя
userID = 1
L = 50

# Поиск лучшей заправки
best = getBestStation(db, plist, userID, L)
print("companyID: {}, Name:{}, Address:{}, cost: {}".format(best[0],
                                                            best[1],
                                                            best[2],
                                                            best[3].encode('utf-8').decode('utf-8')))
db.close()
