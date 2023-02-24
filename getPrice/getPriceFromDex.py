
from baseDatas import baseData
from web3 import Web3
from web3.middleware import geth_poa_middleware
import csv
import json
import asyncio
import requests 
import csv
import time
import os
import glob
import argparse
from datetime import datetime
from tqdm import tqdm
from baseFunction import *

global filter_amount
global token_decimal
# token_decimal = {}
filter_amount = {'ETH' : 1, 'BNB' : 3}  #其他稳定币不能小于 1000 个


def get_price(token0, token1, amount0, amount1, symbol1): #, decimals0, decimals1, 
    # token0  询价的币种
    # token1  代表锚定的币种
    # amount0, amount1  pair中返回的余额，按照token大小返回的
    
    if token0 < token1:
        # print("token 0 ")
        token0_amount, token1_amount = amount0, amount1
    else:
        # print("token 1 ")
        token0_amount, token1_amount = amount1, amount0

    r_token0_amount = token0_amount / 10 ** token_decimal[token0]
    r_token1_amount = token1_amount / 10 ** token_decimal[token1]

    print(f"{symbol1}, {r_token1_amount}")
    if symbol1 in filter_amount:
        if r_token1_amount < filter_amount[symbol1]:
            return 0
    else:
        if r_token1_amount < 1000:
            return 0
    # 池子中 A 的数量是 1 B的数量是 10， A相对于的B价格就是 10
    return r_token1_amount / r_token0_amount

def get_pair_price(token, blockno):  #获取某个区块的eth价格

    for twin in twins: # twin == symbol1
        token1 = getStandAddr(twins[twin])  #需要重新查找
        try:
            # print(f"try the anchor the token of {token1}_{twin}, goal token {token}")
            pairs_address = uni_factory_contract.functions.getPair(token, token1).call(block_identifier = blockno)
            if pairs_address != "0x0000000000000000000000000000000000000000":
                uni_pair_contract = w3.eth.contract(pairs_address, abi = uni_pair_ABI)  # 实例化
                amount0, amount1, blockTimestampLast = uni_pair_contract.functions.getReserves().call(block_identifier = blockno) #blockTimestampLast, 最新波动的时间
                print("pairs_address", pairs_address, twin, token, amount0, amount1)
                price = get_price(token, token1, amount0, amount1, twin)
                if price:
                    # print("blockno, amount0, amount1", blockno, amount0, amount1)
                    return (price, twin, blockTimestampLast )
        except:
            pass
    # print(blockno)
    # if pairs_address != "0x0000000000000000000000000000000000000000":
    #     assert 1 == 0, "666"
    return (0, 0, 0)


def main():  # address 获取symbol name
    labels = ("token","txhash","blockno","price","rtoken","symbol", "denom", "blockTsLast")
    token_decimals_path = f"./dex_txh/{chain}_token_decimals.csv"
    token_decimals = readDefaultCsv(token_decimals_path)
    global token_decimal
    token_decimal = { getStandAddr(tokens["token"]) : int(tokens["decimals"]) for tokens in token_decimals}

    stable_coin = ["MIM"]
    no_price_path = glob.glob(f"./dex_txh/{chain}_no_*.csv")
    assert len(no_price_path) > 0, "notice !"
    print("fill price ", no_price_path)

 
    for need_price_path in no_price_path:
        txhs = readDefaultCsv(need_price_path)
        save_dir = need_price_path.replace("dex_txh", "dex_fill")

        print(f" start from index {start} \n")
        for txh in txhs[start:]:  ## 一行一行遍历

            if txh["symbol"] in stable_coin:
                txh["price"] = 1
                txh["denom"] = "USDT"
                txh["blockTsLast"] = 0
                results = [txh[k] for k in txh]
                print(results)
                write_csv_labels(save_dir, [results], labels)
            
            else:
                rtoken = getStandAddr(txh["rtoken"])
                blockno = int(txh["blockno"])
                
                price, symbol1, blockTsLast = get_pair_price(rtoken, blockno)
                if price:  #写入文件
                    txh["price"] = str(price)
                    txh["denom"] = symbol1
                    txh["blockTsLast"] = blockTsLast
                    results = [txh[k] for k in txh]
                    # print(results)
                    write_csv_labels(save_dir, [results], labels)
        #             # print
        #         break
        # break


def decode_logs(token, txh_log):
    tokens = []
    # print(token)
    if len(token) < 10:
        return tokens.append(token)
    logs = txh_log["logs"]
    for log in logs:
        topics = log["topics"]
        for topic in topics:
            real_token = log["address"]
            if topic.lower() == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef" and real_token.lower() != token.lower():  # transfer
                if real_token not in tokens:
                    tokens.append(log["address"])
    return tokens

def get_real_token():
    
    token_block = []
    file_name = f"./fill_erc20Token/{chain}_token_block.csv"
    print(file_name)
    if os.path.exists(file_name):
        outs = readDefaultCsv(file_name)

    wtoken_record = {}  
    for line in outs:
        wtoken_record[line["token"].lower()] = line

    token_hashs_dir = f"../realToken/{chain}_logs.json"
    token_hashs = loadLogs(token_hashs_dir)
    token_hashs_log = {}
    for key in token_hashs:
        token_hashs_log[key.lower()] = token_hashs[key]
    
    print(len(wtoken_record), len(token_hashs_log))

    erc20_ABI = baseData['abi_contract']['erc_20'] 
    for wtoken in wtoken_record: # labels = ("token", "down_block", "up_block", "symbol", "decimals", "pairs", "pair_tokens")
        line = wtoken_record[wtoken]
        # print("line", line)
        token, symbol, decimals = 0, 0, 0
        if wtoken not in token_hashs_log:
            print(f"txh no wtoken {wtoken}")
            continue

        txh_log = json.loads(token_hashs_log[wtoken])
        tokens = decode_logs(wtoken, txh_log)
        if tokens:
            if len(tokens) == 1:
                try:
                    token = Web3.toChecksumAddress(tokens[0])
                    erc20_contract = w3.eth.contract(token, abi = erc20_ABI)
                    symbol = erc20_contract.functions.symbol().call()
                    decimals = erc20_contract.functions.decimals().call()
                except Exception as e:
                    print(f"cannot find the token {token}")

        line["rtoken"] = token
        line["rsymbol"] = symbol
        line["rdecimals"] = decimals
        token_block.append(line)
        # break

    # print(file_name)
    file_name = f"./fill_erc20Token/real_{chain}_token_block.csv"
    write_dict_csv(file_name, token_block)

def parse_args():
    parser = argparse.ArgumentParser(description='get crossChain events for eth, bsc, polygon')
    # parser.add_argument('--project', default = 'poly', help='the crosschain project')
    parser.add_argument('--chain', default = 'Polygon', help='get the chain data')  #'ETH' #'Polygon'   #['ETH', 'BSC', 'Polygon']  记得更换链
    parser.add_argument('--start', default = 0, help='scan from start index') 
    args = parser.parse_args()
    return args


if __name__ == "__main__":

    args = parse_args()
    #########       参数修改
    chain = args.chain
    start = int(args.start)

    w3 = Web3(Web3.HTTPProvider(baseData['use_network'][chain])) 
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.isConnected()

    # init univ2 factory
    uni_factory_address = Web3.toChecksumAddress(baseData['main_factory_address'][chain]['uni_v2'])
    uni_factory_ABI = baseData['abi_contract']['uni_factory']
    uni_factory_contract = w3.eth.contract(uni_factory_address, abi=uni_factory_ABI)

    # init univ2 pair
    uni_pair_ABI = baseData['abi_contract']['uni_pairs']
    twins = baseData["pair_token"][chain]

    print(f"the chain's anchor token is {twins}")
    # uni_pair_contract = w3.eth.contract(uni_pair_address, abi=uni_pair_ABI)
    #  start ...............

    main()
    # get_real_token()
    #  start ...............

    # txnHash = "0xab594848b45431b9b74bc599e47842445abcfca2ace679fe390e4e27eabcc3e0"
    # get_logs(txnHash)
