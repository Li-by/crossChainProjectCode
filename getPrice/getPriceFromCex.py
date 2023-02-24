# pip install wget

import wget
import datetime
import requests
import json
import os
import time


def downloadData(url, path):
    wget.download(url, path) # 下载

# last_start:开始时间 last_end:结束时间 frequency间隔天数
def split_time_ranges(last_start, last_end, frequency):
    start_date = datetime.datetime.strptime(last_start, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(last_end, "%Y-%m-%d")

    middle_date = datetime.datetime.now()
    time_collection = []
    while True:
        time_collection.append(start_date)
        start_date = start_date + datetime.timedelta(days=frequency)
        if start_date > end_date:
            break
    return time_collection

# {"error": "'end_block' should be less than 10000 blocks away from 'start_block'"}
def get_price_from_eisberg(token0, token1, start_block, end_block, symbol):
    # https://api.eisberg.gg/pair_prices/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2/0xdac17f958d2ee523a2206206994597c13d831ec7?start_block=16287498&end_block=16288497&auth_key=1e18226544aa41c2a09ff634b2d561b5
    
    # /pair_prices/{token0}/{token1}
    # 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 ETH
    # 0xdac17f958d2ee523a2206206994597c13d831ec7 USDT

    #eisberg.gg API key 1e18226544aa41c2a09ff634b2d561b5
    apiKey = "1e18226544aa41c2a09ff634b2d561b5"
    print(token0, token1, start_block, end_block, symbol)
    url = f"https://api.eisberg.gg/pair_prices/{token0}/{token1}?start_block={start_block}&end_block={end_block}&auth_key={apiKey}"  #
    
    # startBlock 11775151   11948956(2021/2/28)

    ret = requests.get(url)
    print(ret)
    with open(f"{symbol}_{start_block}_{end_block}_eth.json","w") as f:
        json.dump(ret.json(),f)

    # print(ret)
    # print(ret.text)
    # ret.json()

    # def write_json(file_name, content):
    #     with open(file_name,"w") as f:
    #         json.dump(content,f)

def split_range(start, end, interval):
    outs = []
    while True:
        middle = start + interval
        if middle >= end:
            outs.append([start, end])
            break 
        outs.append([start, middle])
        start = middle
    return outs

def read_txt(txt_path):
    txt_list = []
    with open(txt_path, "r") as fi:
        for line in fi:
            txt_list.append(line.strip())
    # print(len(txt_list), txt_list)

    usdt_pair = []   # "BUSD" 375
    for pair in txt_list:
        # print(pair)
        if pair[-4:] == "BUSD":
            # print("********", pair)
            pair_u = pair.replace("BUSD", "USDT")
            if pair_u in txt_list:
                # print(pair_u)
                usdt_pair.append(pair_u)
    print("BUSD : ", len(usdt_pair)) #350

    for pair1 in txt_list:
        if pair1[-4:] == "USDT":
            if pair1 not in usdt_pair: # or "DOWN" not in pair1 or "UP" not in pair1:
                if "DOWN" in pair1 or "UP" in pair1:
                    # print(pair1)
                    continue
                usdt_pair.append(pair1)
    print("ADD USDT :", len(usdt_pair))   # 418 -> 378
    # for token in usdt_pair:
    #     print(token)
    return usdt_pair


if __name__ == '__main__':
    # bnb TokenPrice https://data.binance.vision/?prefix=data/spot/daily/klines/MATICUSDT/5m/

    #eth
    # url = 'https://data.binance.vision/data/spot/daily/klines/ETHUSDT/5m/ETHUSDT-5m-2021-03-01.zip' # 目标路由，下载的资源是图片
    # savePath = './ethPrice' # 保存的路径

    #bnb
    # https://data.binance.vision/data/spot/daily/klines/BNBUSDT/5m/BNBUSDT-5m-2021-03-01.zip
    # savePath = './bnbPrice' # 保存的路径

    #polygon
    # https://data.binance.vision/data/spot/daily/klines/MATICUSDT/5m/MATICUSDT-5m-2021-03-01.zip
    # savePath = './maticPrice'

    # time_list = split_time_ranges("2021-03-01", "2022-08-31", 1)  #549
    # # print(len(time_list))
    # for day in time_list:
    #     get_day = str(day).split(" ")[0]
    #     url = f"https://data.binance.vision/data/spot/daily/klines/MATICUSDT/5m/MATICUSDT-5m-{get_day}.zip"
    #     downloadData(url, savePath)

    ## get price from biance cex
    """
    time_list = split_time_ranges("2021-03-01", "2022-08-31", 1)  #549天
    txt_path = "./tokenPrice/data-spot-daily-klines.txt"
    save_dir = "./tokenPrice"
    token_list = read_txt(txt_path)
    haved_save = ["BNBUSDT", "ETHUSDT", "MATICUSDT"]
    for token in token_list:
        if token not in haved_save:
            savePath = os.path.join(save_dir, token)
            if not os.path.exists(savePath):
                os.mkdir(savePath)

                for day in time_list:
                    get_day = str(day).split(" ")[0]
                    url = f"https://data.binance.vision/data/spot/daily/klines/{token}/5m/{token}-5m-{get_day}.zip"
                    try:
                        downloadData(url, savePath)
                    except:
                        pass
            else:
                zip_list = [zip for zip in os.listdir(savePath) if zip.endswith("zip")]
                if len(zip_list) != 549:
                    print(len(zip_list), token)

            # break
        # time.sleep(100)
    """

    
    # get price from uniswap v2
    #eth
    token0 = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2" #ETH
    # token0 = "0xB8c77482e45F1F44dE1745F52C74426C631bDD52"  #BNB
    # token1 = "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0" #matic
    # token1 = "0xdac17f958d2ee523a2206206994597c13d831ec7" #USDT
    
    token1 = {"symbol" : "ust", "addr": "0xa47c8bf37f92aBed4A126BDA807A7b7498661acD", "start_blo" : 13246360, "end_blo" : 13868864} #2021-09-18 00:01:18  2021-12-24 16:01:34

    # start_block = 11766939  #(2021/2/1)
    # end_block = 11775151 #(2021/2/2)
    # start_block = 11775151 #(2021/2/2)
    # end_block = 11948956  #(2021/2/28)
    # end_block = 11785151
    interval = 10000   #最大区块间隔
    sub_start_end = split_range(token1["start_blo"], token1["end_blo"], interval)
    # print(len(sub_start_end))
    for start_end in sub_start_end:
        get_price_from_eisberg(token0, token1["addr"], start_end[0], start_end[1], token1["symbol"])
    