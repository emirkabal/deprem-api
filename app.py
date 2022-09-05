import re
import json
from urllib.request import urlopen
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, make_response, request

app = Flask(__name__)

def get_Data():
    array = []
    data = urlopen('http://www.koeri.boun.edu.tr/scripts/lst2.asp').read()
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

@app.route('/')
def index():
    data = get_Data()
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


def filterbylocation(location,data):
    return list(filter(lambda i: location.upper() in i['location'], data))


def filterbysize(size,data):
    return list(filter(lambda i: float(size) <= float(i['size']['ml']), data))


def filterbysizeandlocation(size,location,data):
    return list(filter(lambda i: float(size) <= float(i['size']['ml']) and location.upper() in i['location'], data))

if __name__ == "__main__":
    app.run(port=3000)
