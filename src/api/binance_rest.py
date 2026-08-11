import requests
url="https://data-api.binance.vision/api/v3/ticker/price"

def get_price(symbol):
    params={
      "symbol":symbol
    }
    response = requests.get(url, params=params)
    return response.json()
  
symbols = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "LINKUSDT",
    "DOTUSDT"
]

for symbol in symbols:
  data = get_price(symbol)
  print(f"{data['symbol']}: ${data['price']}")