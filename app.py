import re
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, make_response


app = Flask(__name__)

def get_Data():
    array = []
    data = requests.get('http://www.koeri.boun.edu.tr/scripts/lst2.asp')
    soup = BeautifulSoup(data.content, 'html.parser')
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
            "Nitelik": element.split(Yer)[1].split(' ')[0]
        }, sort_keys=False)

        array.append(json.loads(json_data))
    return array

@app.route('/')
def index():
    data = get_Data()
    json_data = json.dumps({
        "dev":"Emir Kabal (https://emirkabal.com)",
        "source":"Kandilli Rasathanesi (http://www.koeri.boun.edu.tr)",
        "github_link": "https://github.com/emirkabal/deprem-api",
        "depremler": data}, sort_keys=False)
    res = make_response(json_data)
    res.headers['Content-Type'] = 'application/json'
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res

# heroku app
# if __name__ == "__main__":
#     app.run(port=3000)