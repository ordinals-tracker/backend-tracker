import requests
from datetime import datetime, timedelta

ME_TOKEN = "your_magic_eden_api_key_here"

def fetch_btc_price():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"

    params = {
        'vs_currency': 'usd',
        'days': 'max',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {datetime.fromtimestamp(timestamp / 1000.0).strftime('%d/%m/%Y'): price for timestamp, price in data['prices']}
    return []

def fetch_real_time_btc_price():

    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        btc_price = data['bitcoin']['usd']
        return btc_price
    return 0
    
def create_chart():
    current_date = datetime.utcnow()
    one_year_now = current_date - timedelta(days=365)
    date_array = []
    mint = []
    buy = []
    sell = []

    while one_year_now <= current_date:
        date_array.append(one_year_now.strftime('%Y-%m-%d'))
        one_year_now += timedelta(days=1)
        mint.append(0)
        buy.append(0)
        sell.append(0)

    return date_array,mint,buy,sell

def get_me_activity(wallets):

    result = []
    buy = 0
    usd_buy = 0
    trades = {}
    sell = 0
    usd_sell = 0
    mint = 0
    usd_mint = 0

    btc_prices = fetch_btc_price()

    date_chart,mint_chart,buy_chart,sell_chart = create_chart()

    for wallet in wallets:
        cont = 0
        resp = [None]
        try:
            while resp != []:
                headers = {
                    "Authorization": ME_TOKEN,
                }

                params = {
                    'limit': '40',
                    'offset': 40 * cont,
                    'ownerAddress': wallet,
                    'kind': ["buying_broadcasted","transfer","mint_broadcasted","create"]
                }

                response = requests.get("https://api-mainnet.magiceden.dev/v2/ord/btc/activities", params=params, headers=headers)

                resp = response.json()["activities"]
                result += resp
                cont+=1
        except:
            pass
        
    result_dict = {}
    for info in result[::-1]:
        if info["collectionSymbol"] != None and "brc20_" not in info["collectionSymbol"]:
            parsed_date = datetime.strptime(info["createdAt"], '%a, %d %b %Y %H:%M:%S %Z')
            formatted_date = parsed_date.strftime('%Y-%m-%d')
            btc_data = parsed_date.strftime('%d/%m/%Y')

            price_btc = btc_prices[btc_data] if btc_data in btc_prices else btc_prices[-1]

            position = date_chart.index(formatted_date)
            timestamp = datetime.strptime(info["createdAt"], "%a, %d %b %Y %H:%M:%S %Z").timestamp()

            if info["collectionSymbol"] not in result_dict:
                headers = {
                    "Authorization": "Bearer 9e44e66c-cc39-4262-973b-df7342790dcd",
                }

                response = requests.get("https://api-mainnet.magiceden.dev/v2/ord/btc/collections/"+info["collectionSymbol"], headers=headers)
                c = response.json()

                response = requests.get("https://api-mainnet.magiceden.dev/v2/ord/btc/stat?collectionSymbol="+info["collectionSymbol"], headers=headers)
                stats = response.json()

                result_dict[info["collectionSymbol"]] = {"event": []}
                result_dict[info["collectionSymbol"]].update(c)
                result_dict[info["collectionSymbol"]].update(stats)
                result_dict[info["collectionSymbol"]]["floorPrice"] = float(result_dict[info["collectionSymbol"]]["floorPrice"])/10**8 if result_dict[info["collectionSymbol"]]["floorPrice"] != None else 0
                result_dict[info["collectionSymbol"]]["totalVolume"] = float(result_dict[info["collectionSymbol"]]["totalVolume"])/10**8 if result_dict[info["collectionSymbol"]]["totalVolume"] != None else 0

            del info["collection"]
            key = info["collectionSymbol"]
            del info["collectionSymbol"]
            if info["kind"] == "buying_broadcasted" and info["oldOwner"] in wallets:
                info["kind"] = "Sell"
                sell += info["listedPrice"]
                usd_sell += price_btc*(info["listedPrice"]/10**8)
                sell_chart[position] -= info["listedPrice"]/10**8
                if info["tokenId"] not in trades:
                    trades[info["tokenId"]] = {"name": info["token"]["meta"]["name"] if "meta" in info["token"] and info["token"]["meta"]["name"] != "" else str(info["token"]["inscriptionNumber"]),"collection_id":key, "collection": result_dict[key]["name"], "sell": [],"buy": [], "mint": [],"id": info["tokenId"], "inscription_contentType": info["token"]["contentType"], "collection_image": result_dict[key]["imageURI"]} 

                trades[info["tokenId"]]["sell"].append({"price": info["listedPrice"]/10**8, "usd_price": price_btc*(info["listedPrice"]/10**8),"tx": info["txId"], "when": timestamp})

            elif info["kind"] == "buying_broadcasted" and info["oldOwner"] not in wallets and info["newOwner"] in wallets:
                info["kind"] = "Buy"
                buy += info["listedPrice"]
                usd_buy += price_btc*(info["listedPrice"]/10**8)
                buy_chart[position] += info["listedPrice"]/10**8
                if info["tokenId"] not in trades:
                    trades[info["tokenId"]] = {"name": info["token"]["meta"]["name"] if "meta" in info["token"] and "name" in info["token"]["meta"] and info["token"]["meta"]["name"] != "" else "Inscription #"+str(info["token"]["inscriptionNumber"]),"collection_id":key, "collection": result_dict[key]["name"], "sell": [],"buy": [], "mint": [],"id": info["tokenId"], "inscription_contentType": info["token"]["contentType"], "collection_image": result_dict[key]["imageURI"]} 

                trades[info["tokenId"]]["buy"].append({"price": info["listedPrice"]/10**8, "usd_price": price_btc*(info["listedPrice"]/10**8), "tx": info["txId"], "when": timestamp})

            elif info["kind"] == "mint_broadcasted" and info["oldOwner"] not in wallets and info["newOwner"] in wallets:
                info["kind"] = "Mint"
                mint += info["listedPrice"]
                usd_mint += price_btc*(info["listedPrice"]/10**8)
                mint_chart[position] += info["listedPrice"]/10**8
                if info["tokenId"] not in trades:
                    trades[info["tokenId"]] = {"name": info["token"]["meta"]["name"] if "meta" in info["token"] and info["token"]["meta"]["name"] != "" else str(info["token"]["inscriptionNumber"]),"collection_id":key, "collection": result_dict[key]["name"], "sell": [],"buy": [], "mint": [],"id": info["tokenId"], "inscription_contentType": info["token"]["contentType"], "collection_image": result_dict[key]["imageURI"]} 

                trades[info["tokenId"]]["mint"].append({"price": info["listedPrice"]/10**8 , "usd_price": price_btc*(info["listedPrice"]/10**8), "tx": info["txId"], "when": timestamp})

            elif info["kind"] == "transfer" and info["oldOwner"] in wallets:
                info["kind"] = "Send"

            elif info["kind"] == "transfer" and info["oldOwner"] not in wallets and info["newOwner"] in wallets:
                info["kind"] = "Receive"
            
            if "listedPrice" in info:
                info["usd_price"] = price_btc*(info["listedPrice"]/10**8)

            result_dict[key]["event"].append(info)
    
    trades = [trade_data for trade_data in trades.values()]
    result_dict = [result_data for result_data in result_dict.values()]
    
    sell = sell/10**8
    mint = mint/10**8
    buy = buy/10**8

    pnl = 0
    usd_pnl = 0
    upnl = 0
    usd_upnl = 0

    for info in trades:
        if (info["buy"] != [] or info["mint"] != []) and info["sell"] != []:
            b = info["buy"][0]["price"] if len(info["buy"]) > 0 else 0
            m = info["mint"][0]["price"] if len(info["mint"]) > 0 else 0
            s = info["sell"][0]["price"]
            pnl += (s - m - b)

            usd_b = info["buy"][0]["usd_price"] if len(info["buy"]) > 0 else 0
            usd_m = info["mint"][0]["usd_price"] if len(info["mint"]) > 0 else 0
            usd_s = info["sell"][0]["usd_price"]
            usd_pnl += (usd_s - usd_m - usd_b)

        elif  info["buy"] == [] and info["mint"] == [] and info["sell"] != []:
            pnl += info["sell"][0]["price"]
            usd_pnl += info["sell"][0]["usd_price"]

        elif (info["buy"] != [] or info["mint"] != []) and info["sell"] == []:
            b = info["buy"][0]["price"] if len(info["buy"]) > 0 else 0
            m = info["mint"][0]["price"] if len(info["mint"]) > 0 else 0
            upnl += (b+m) 

            usd_b = info["buy"][0]["usd_price"] if len(info["buy"]) > 0 else 0
            usd_m = info["mint"][0]["usd_price"] if len(info["mint"]) > 0 else 0
            usd_upnl += (usd_b+usd_m) 
    
    for i,info in enumerate(result_dict):
        result_dict[i]["event"] =  sorted(result_dict[i]["event"], key=lambda x: datetime.strptime(x['createdAt'], '%a, %d %b %Y %H:%M:%S %Z'))

    return {
                "count": len(result), 
                "collections": result_dict, 
                "buy": buy, 
                "sell": sell,  
                "mint": mint,
                "usd_buy": usd_buy, 
                "usd_sell": usd_sell,  
                "usd_mint": usd_mint,
                "pnl": pnl,
                "upnl": upnl,
                "usd_pnl": usd_pnl,
                "usd_upnl": usd_upnl,
                "pnl_percent": pnl/(buy + mint) if (buy + mint) > 0 else 0,
                "trades": trades, 
                "chart": [
                    {"Mint": mint_chart},
                    {"Buy": buy_chart},
                    {"Sell": sell_chart},
                    {"Dates": date_chart} 
                ]
            }

def get_holdings(wallets):
    result = []
    btc_price = fetch_real_time_btc_price()
    for wallet in wallets:
        cont = 0
        resp = [None]
        while resp != []:
            headers = {
                "Authorization": ME_TOKEN,
            }

            params = {
                'limit': '40',
                'offset': 40 * cont,
                'ownerAddress': wallet,
            }

            response = requests.get("https://api-mainnet.magiceden.dev/v2/ord/btc/tokens", params=params, headers=headers)
            resp = response.json()["tokens"]
            result += resp
            cont+=1

    result_dict = {}

    for info in result:
        if "collectionSymbol" not in info:
            info["collectionSymbol"] = "Unverified"
        
        if  info["collectionSymbol"] == "Unverified":
            pass
        elif info["collectionSymbol"] != None and "brc20_" not in info["collectionSymbol"]:

            if info["collectionSymbol"] not in result_dict:
                headers = {
                    "Authorization": "Bearer 9e44e66c-cc39-4262-973b-df7342790dcd",
                }

                response = requests.get("https://api-mainnet.magiceden.dev/v2/ord/btc/collections/"+info["collectionSymbol"], headers=headers)
                c = response.json()

                response = requests.get("https://api-mainnet.magiceden.dev/v2/ord/btc/stat?collectionSymbol="+info["collectionSymbol"], headers=headers)
                stats = response.json()

                result_dict[info["collectionSymbol"]] = {"inscriptions": []}
                result_dict[info["collectionSymbol"]].update(c)
                result_dict[info["collectionSymbol"]].update(stats)
                result_dict[info["collectionSymbol"]]["floorPrice"] = float(result_dict[info["collectionSymbol"]]["floorPrice"])/10**8 if result_dict[info["collectionSymbol"]]["floorPrice"] != None else 0
                result_dict[info["collectionSymbol"]]["totalVolume"] = float(result_dict[info["collectionSymbol"]]["totalVolume"])/10**8 if result_dict[info["collectionSymbol"]]["totalVolume"] != None else 0

            del info["collection"]
            key = info["collectionSymbol"]
            del info["collectionSymbol"]

            result_dict[key]["inscriptions"].append(info)
        elif "brc20_" not in info["collectionSymbol"]:

            del info["collection"]
            key = info["collectionSymbol"]
            del info["collectionSymbol"]
            result_dict[key]["inscriptions"].append(info)

    result_calculated = []
    total_balance = 0
    for result_data in result_dict.values():
        result_data["holdingBalance"] = result_data["floorPrice"] * len(result_data["inscriptions"])
        result_data["usd_holdingBalance"] = result_data["floorPrice"] * len(result_data["inscriptions"]) * btc_price
        total_balance += result_data["floorPrice"] * len(result_data["inscriptions"])
        result_calculated.append(result_data)

    result_calculated = sorted(result_calculated, key=lambda x: x['holdingBalance'], reverse=True)
    return result_calculated,total_balance,total_balance*btc_price
