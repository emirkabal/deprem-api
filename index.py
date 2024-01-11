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


def fLocation(location, data):
    return list(filter(lambda i: location.upper() in i['location'], data))


def fSize(size, data, type, isGreater):
    
    size = float(size)
    type = type.lower()

    if type not in ['md', 'ml', 'mw']:
        type = 'ml'

    if isGreater:
        return list(filter(lambda i: size <= float(i['size'][type]), data))
    else:
        return list(filter(lambda i: size >= float(i['size'][type]), data))

def fTime(hour, data, type):
    if type == 'afad':
        now = datetime.strptime(datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S"), '%Y-%m-%dT%H:%M:%S')
        return [record for record in data if (now - datetime.strptime(record['date'], "%Y-%m-%dT%H:%M:%S")) <= timedelta(hours=int(hour))]
    else:
        now = datetime.strptime(datetime.now().strftime(
            "%Y.%m.%d %H:%M:%S"), '%Y.%m.%d %H:%M:%S')
        return [record for record in data if (now - datetime.strptime(record['date'], "%Y.%m.%d %H:%M:%S")) <= timedelta(hours=int(hour))]

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
    
def strtobool (val):
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("Invalid boolean value: " + val)

app = Flask(__name__)

@app.route('/')
def index():
    source_type = request.args.get(key='type', default='kandilli')
    data = getData(type=source_type)

    location = request.args.get('location')
    hour = request.args.get('hour')
    size = request.args.get('size')
    sizeType = request.args.get(key='sizeType', default='ml')
    isGreater = request.args.get(key='isGreater', default='1')

    try:
        if location is not None:
            data = fLocation(location, data)
        if size is not None and isfloat(size):
            data = fSize(size, data, type=sizeType, isGreater=strtobool(isGreater))
        if hour is not None:
            data = fTime(hour, data, type=source_type)
    except Exception as e:
        res = make_response(json.dumps({
            "error": True,
            "stack": str(e)
        }), 400)
        res.headers['Content-Type'] = 'application/json'
        res.headers['Access-Control-Allow-Origin'] = '*'
        return res


    json_data = json.dumps({
        "github": "https://github.com/emirkabal/deprem-api",
        "earthquakes": data}, sort_keys=False)
    res = make_response(json_data)
    res.headers['Content-Type'] = 'application/json'
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


if __name__ == '__main__':
    app.run(debug=True)