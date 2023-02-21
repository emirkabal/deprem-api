import re
import json
import time
import threading
import schedule
from urllib.request import urlopen
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, make_response, request

afadData = []
kandilliData = []

def get_kandilli_data():
    array = []
    data = urlopen('http://www.koeri.boun.edu.tr/scripts/sondepremler.asp').read()
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
        Args=element.split(' ')
        location = Args[8]+element.split(Args[8])[len(element.split(Args[8])) - 1].split('İlksel')[0].split('REVIZE')[0]
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

def get_afad_data():
    array = []
    data = urlopen('https://deprem.afad.gov.tr/last-earthquakes.html').read()
    soup = BeautifulSoup(data, 'html.parser')
    data = soup.find_all('tr')
    data.pop(0)
    for i in range(len(data)):
        earthquakeType = data[i].find_all('td')[4].text
        json_data = json.dumps({
            "id": i+1,
            "date": data[i].find_all('td')[0].text,
            "timestamp": int(datetime.strptime(data[i].find_all('td')[0].text, "%Y-%m-%d %H:%M:%S").timestamp()),
            "latitude": float(data[i].find_all('td')[1].text),
            "longitude": float(data[i].find_all('td')[2].text),
            "depth": float(data[i].find_all('td')[3].text),
            "size": {
                "md": float(data[i].find_all('td')[5].text) if earthquakeType == "MD" else  0,
                "ml": float(data[i].find_all('td')[5].text) if earthquakeType == "ML" else 0,
                "mw": float(data[i].find_all('td')[5].text) if earthquakeType == "MW" else 0
            },
            "location": data[i].find_all('td')[6].text,
            "afad_id": data[i].find_all('td')[7].text,
            "attribute": earthquakeType
        }, sort_keys=False)

        array.append(json.loads(json_data))
    return array

def get_Data(
    type='kandilli',
):
    if type == 'afad':
        return afadData
    else:
        return kandilliData


def job():
    print('Job Started')
    global afadData
    global kandilliData
    afadData = get_afad_data()
    kandilliData = get_kandilli_data()

job()
schedule.every(5).minutes.do(job)

def thread_function():
    while True:
        schedule.run_pending()
        time.sleep(1)

x = threading.Thread(target=thread_function)
x.start()




def filterbylocation(location,data):
    return list(filter(lambda i: location.upper() in i['location'], data))


def filterbysize(size,data):
    return list(filter(lambda i: float(size) <= float(i['size']['ml']), data))


def filterbysizeandlocation(size,location,data):
    return list(filter(lambda i: float(size) <= float(i['size']['ml']) and location.upper() in i['location'], data))

app = Flask(__name__)

@app.route('/')
def index():
    source_type = request.args.get('type') if request.args.get('type') is not None else 'kandilli'
    data = get_Data(type=source_type)
    location = request.args.get('location')
    size = request.args.get('size')

    if location is not None and size is not None:
        data = filterbysizeandlocation(size,location,data)
    elif location is not None:
        data = filterbylocation(location, data)
    elif size is not None and size.isnumeric():
        data = filterbysize(size,data)

    json_data = json.dumps({
        "github": "https://github.com/emirkabal/deprem-api",
        "earthquakes": data}, sort_keys=False)
    res = make_response(json_data)
    res.headers['Content-Type'] = 'application/json'
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res




# if __name__ == '__main__':
#     app.run(debug=True)
