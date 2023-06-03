import re
import json
import time
import threading
import schedule
from urllib.request import urlopen, Request
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from flask import Flask, make_response, request

afadData = []
kandilliData = []


def getKandilliData():
    try:
        array = []
        data = urlopen(
            'http://www.koeri.boun.edu.tr/scripts/sondepremler.asp').read()
        soup = BeautifulSoup(data, 'html.parser')
        data = soup.find_all('pre')
        data = str(data).strip().split('--------------')[2]

        data = data.split('\n')
        data.pop(0)
        data.pop()
        data.pop()
        for index in range(len(data)):
            element = str(data[index].rstrip())
            element = re.sub(r'\s\s\s', ' ', element)
            element = re.sub(r'\s\s\s\s', ' ', element)
            element = re.sub(r'\s\s', ' ', element)
            element = re.sub(r'\s\s', ' ', element)
            Args = element.split(' ')
            location = Args[8]+element.split(Args[8])[len(element.split(
                Args[8])) - 1].split('İlksel')[0].split('REVIZE')[0]
            json_data = json.dumps({
                "id": index+1,
                "date": Args[0]+" "+Args[1],
                "timestamp": int(datetime.strptime(Args[0]+" "+Args[1], "%Y.%m.%d %H:%M:%S").timestamp()),
                "latitude": float(Args[2]),
                "longitude": float(Args[3]),
                "depth": float(Args[4]),
                "size": {
                    "md": float(Args[5].replace('-.-', '0')),
                    "ml": float(Args[6].replace('-.-', '0')),
                    "mw": float(Args[7].replace('-.-', '0'))
                },
                "location": location.strip(),
                "attribute": element.split(location)[1].split()[0]
            }, sort_keys=False)

            array.append(json.loads(json_data))
        return array
    except:
        return []


def getAfadData():
    try:
        array = []
        req = Request(
            'https://deprem.afad.gov.tr/EventData/GetEventsByFilter', method='POST')
        req.add_header('Content-Type', 'application/json; charset=utf-8')

        current_date = datetime.now()
        start_date = current_date - timedelta(days=1)
        end_date = current_date
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        start_date_str = start_date.strftime(date_format)
        end_date_str = end_date.strftime(date_format)

        data = json.dumps({
            "EventSearchFilterList": [
                {"FilterType": 9, "Value": end_date_str},
                {"FilterType": 8, "Value": start_date_str}
            ],
            "Skip": 0,
            "Take": 20,
            "SortDescriptor": {"field": "eventDate", "dir": "desc"}
        })
        data = data.encode()
        content = urlopen(req, data=data).read()
        content = json.loads(content)
        for i in range(len(content["eventList"])):
            el = content["eventList"][i]
            magnitudeType = el["magnitudeType"]
            json_data = json.dumps({
                "id": i+1,
                "date": el["eventDate"],
                "timestamp": int(datetime.strptime(el["eventDate"], "%Y-%m-%dT%H:%M:%S").timestamp()),
                "latitude": float(el["latitude"]),
                "longitude": float(el["longitude"]),
                "depth": float(el["depth"]),
                "size": {
                    "md": float(el["magnitude"]) if magnitudeType == "MD" else 0,
                    "ml": float(el["magnitude"]) if magnitudeType == "ML" else 0,
                    "mw": float(el["magnitude"]) if magnitudeType == "MW" else 0
                },
                "location": el["location"],
                "afadDetails": {
                    "id": el["id"],
                    "refId": el["refId"]
                },
                "attribute": magnitudeType
            }, sort_keys=False)

            array.append(json.loads(json_data))
        return array
    except:
        return []


def getData(
    type='kandilli',
):
    if type == 'afad':
        return afadData
    else:
        return kandilliData


def job():
    global afadData
    global kandilliData
    afadData = getAfadData()
    kandilliData = getKandilliData()[:100]


job()
schedule.every(5).minutes.do(job)


def threadFunction():
    while True:
        schedule.run_pending()
        time.sleep(1)


x = threading.Thread(target=threadFunction)
x.start()


def filterByLocation(location, data):
    return list(filter(lambda i: location.upper() in i['location'], data))


def filterBySize(size, data):
    return list(filter(lambda i: float(size) <= float(i['size']['ml']), data))


def filterBySizeAndLocation(size, location, data):
    return list(filter(lambda i: float(size) <= float(i['size']['ml']) and location.upper() in i['location'], data))


def filterByTime(hour, data):
    now = datetime.strptime(datetime.now().strftime(
        "%Y.%m.%d %H:%M:%S"), '%Y.%m.%d %H:%M:%S')
    return [record for record in data if (now - datetime.strptime(record['date'], "%Y.%m.%d %H:%M:%S")) <= timedelta(hours=int(hour))]


def filterBySizeandtime(size, hour, data):
    filtered_by_time = filterByTime(hour, data)
    filtered_by_size = filterBySize(size, filtered_by_time)
    return filtered_by_size


def filterBySizeandtimeandlocation(size, hour, location, data):
    filtered_by_time = filterByTime(hour, data)
    filtered_by_size = filterBySize(size, filtered_by_time)
    filtered_by_location = filterByLocation(location, filtered_by_size)
    return filtered_by_location


app = Flask(__name__)


@app.route('/')
def index():
    source_type = request.args.get('type') if request.args.get(
        'type') is not None else 'kandilli'
    data = getData(type=source_type)
    location = request.args.get('location')
    size = request.args.get('size')
    hour = request.args.get('hour')

    if location is not None and size is not None:
        data = filterBySizeAndLocation(size, location, data)
    elif location is not None:
        data = filterByLocation(location, data)
    elif size is not None and size.isnumeric():
        data = filterBySize(size, data)
    elif hour is not None and size == None and location == None:
        data = filterByTime(hour, data)

    json_data = json.dumps({
        "github": "https://github.com/emirkabal/deprem-api",
        "earthquakes": data}, sort_keys=False)
    res = make_response(json_data)
    res.headers['Content-Type'] = 'application/json'
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


if __name__ == '__main__':
    app.run(debug=True)
