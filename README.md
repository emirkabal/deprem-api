# deprem-api
### Parametreler:
- **size** : Depremin büyüklüğüne göre filtreleme yapar.
- **location** : Depremin lokasyonuna göre filtereleme yapar.

<hr>

### Örnekler:
- http://127.0.0.1:3000/?size=3.1
- http://127.0.0.1:3000/?location=istanbul
- http://127.0.0.1:3000/?size=3.1&location=istanbul

## JSON Çıktısı:
```json
"earthquakes": [
    {
      "id": 1,
      "date": "2022.09.05 16:45:54", // GMT+3
      "timestamp": 1662385554,
      "latitude": 37.1075,
      "longitude": 28.5117,
      "depth": 2.8, // km
      "size": {
        "md": 0.0,
        "ml": 3.6,
        "mw": 3.7
      },
      "location": "ARMUTCUK-ULA (MUGLA)",
      "attribute": "İlksel"
    }, {...}
]
```