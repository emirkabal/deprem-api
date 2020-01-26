# deprem-api
Tüm API'ye https://deprem-api.herokuapp.com adresinden ulaşabilirsiniz.

Url Parametre:
- 	**size** : Depremin büyüklüğüne göre filtreleme yapar.
- 	**location** : Depremin lokasyonuna göre filtereleme yapar.

Örnek İstek:
- 	http://127.0.0.1:3000/?size=3.1
- 	http://127.0.0.1:3000/?location=istanbul
- 	http://127.0.0.1:3000/?size=3.1&location=istanbul

JSON Çıktısı:

    "depremler": [
    {
    	"Id": 1,
    	"Tarih": "2019.08.22",
    	"Saat": "13:01:01",
    	"Unix_Time": 1566468061,
    	"Enlem(N)": "40.1722",
    	"Boylam(E)": "30.7525",
    	"Derinlik(km)": "5.2",
    	"Buyukluk": {
    		"MD": "0",
    		"ML": "1.5",
    		"Mw": "0"},
    	"Yer": "ASAGIKINIK-GOYNUK (BOLU)",
    	"Nitelik": "İlksel"
    }, ... ]
    


