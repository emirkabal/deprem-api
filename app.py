import re
import json
from urllib.request import urlopen
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, make_response, request

app = Flask(__name__)

def get_Data():
    array = []
    data = urlopen('http://www.koeri.boun.edu.tr/scripts/lst2.asp').read().decode('utf-8')
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
        Yer = Args[8]+element.split(Args[8])[len(element.split(Args[8])) - 1].split('İlksel')[0].split('REVIZE')[0]
        json_data = json.dumps({
            "Id": index+1,
            "Tarih": Args[0],
            "Saat": Args[1],
            "Unix_Time": datetime.strptime(Args[0]+" "+Args[1], "%Y.%m.%d %H:%M:%S").timestamp(),
            "Enlem(N)": Args[2],
            "Boylam(E)": Args[3],
            "Derinlik(km)": Args[4],
            "Buyukluk": {
                "MD": Args[5].replace('-.-', '0'),
                "ML": Args[6].replace('-.-', '0'),
                "Mw": Args[7].replace('-.-', '0') 
            },
            "Yer": Yer.strip(),
            "Nitelik": element.split(Yer)[1].split()[0]
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
        "dev":"Emir Kabal (https://emirkabal.com)",
        "source":"Kandilli Rasathanesi (http://www.koeri.boun.edu.tr)",
        "github_link": "https://github.com/emirkabal/deprem-api",
        "depremler": data}, sort_keys=False)
    res = make_response(json_data)
    res.headers['Content-Type'] = 'application/json'
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


def filterbylocation(location,data):
    return list(filter(lambda i: location.upper() in i['Yer'], data)


def filterbysize(size,data):
    earthquakelist = []
    for i in data:
        try:
            if float(size) <= float(i['Buyukluk']['ML']):
                earthquakelist.append(i)
        except ValueError:
            pass
    return earthquakelist


def filterbysizeandlocation(size,location,data):
    earthquakelist = []
    for i in data:
        try:
            if float(size) <= float(i['Buyukluk']['ML']) and location.upper() in i['Yer']:
                earthquakelist.append(i)
        except ValueError:
            continue
    return earthquakelist

if __name__ == "__main__":
    app.run(port=3000)
