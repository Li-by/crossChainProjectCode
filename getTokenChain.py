# import sys
# sys.path.append("./")
# -*- coding: utf-8 -*- 


from baseDatas import baseData
# import baseFunction
from baseFunction import *
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


def get_contract_csv():
    for chain in ['ETH', 'BSC', 'Polygon']:
        save_dir = os.path.join(datasName, project, chain)
        file_csv_path = glob.glob(save_dir + "/*_filled.csv")
        assert len(file_csv_path) > 0, "notice !"

        contractAddress = []
        for fi in file_csv_path:
            # print(" file_csv_path",  file_csv_path)
            sub_blocks = readCsv(fi)
            # print(len(sub_blocks))
            # for txhs in tqdm(sub_blocks):
            for txhs in sub_blocks:
                if txhs["contractAddress"] not in contractAddress:
                    contractAddress.append(txhs["contractAddress"])
        print(project, "->", chain, ":", contractAddress)
            

def main():
    token_block = {}
    file_name = f"{chain}_token_block.csv"
    if os.path.exists(file_name):
        outs = readDefaultCsv(file_name)  # "token", "down_block", "up_block"
        for line in outs:
            token_block[line["token"]] = [line["down_block"], line["up_block"]]

    for project in ["multichain", "portal", "poly"]:
        save_dir = os.path.join(datasName, project, chain)
        file_csv_path = glob.glob(save_dir + "/*.csv")
        assert len(file_csv_path) > 0, "notice !"
        chainIds = []
        for fi in file_csv_path:
            print(" file_csv_path",  file_csv_path)
            sub_blocks = readCsv(fi)
            # print(len(sub_blocks))
            for txhs in tqdm(sub_blocks):
                block = txhs["blockno"]
                for token in [txhs["srcToken"], txhs['dstToken']]:
                    if token not in token_block:
                        token_block[token] = [block, block]
                    else:
                        if block < min(token_block[token]):
                            token_block[token][0] = block
                        elif block > max(token_block[token]):
                            token_block[token][1] = block
                        else:
                            pass

                chainId = txhs['dstID']
                # if chainId == "24519021599755224229915701403662874105682026366812048727644160988680600682496":
                #     # print(txhs['txhash'])
                #     assert 1 == 0, "3.2"
                if chainId not in chainIds:
                    chainIds.append(chainId)
        
        print(f"{project} in {chain} :", chainIds)

    outs = [(key, token_block[key][0], token_block[key][1]) for key in token_block]
    # return (flag,tuple(outs))

    # print(file_name)
    write_csv(file_name, outs)

def parse_token():

    symble_token = {} # symbol : [[rtoken, token]]

    real_token_path = f"./erc20Tokens/fill_erc20Token/real_{chain}_token_block.csv"
    real_tokens = readDefaultCsv(real_token_path)
    token_realToken = { getStandAddr(record_token["token"]) : record_token for record_token in real_tokens} #if record_token["symbol"]
    # no_name_list = [record_token["token"] for record_token in real_tokens if not record_token["symbol"] ] 
    token_price_cex_dir = "./erc20Tokens/tokenPrice/cex_token_price/"
    cex_token_list = [ fi.split("_")[0] for fi in os.listdir(token_price_cex_dir) if fi.endswith("csv")]
    # print(cex_token_list)

    for record_token in real_tokens:
        # symb = None
        rsymbol = record_token["rsymbol"]
        rtoken = record_token["rtoken"]
        symbol = record_token["symbol"]
        token = record_token["token"]
        
        if rsymbol != "0":  #优先级按照顺序
            if rsymbol not in symble_token:
                symble_token[rsymbol] = [ [rtoken, token] ]
            else:
                symble_token[rsymbol].append([rtoken, token])

        elif symbol != "0":
            if symbol not in symble_token:
                symble_token[symbol] = [ [0, token] ]
            else:
                symble_token[symbol].append([0, token])

        elif token != "0":
            if token not in symble_token:
                symble_token[token] = [ [0, 0] ]
            else:
                symble_token[token].append([0, 0])

        else:
            print(f"need check {record_token}")
            break

    
    # func b
    ### ETH 在cex中寻找相似的token, 且该token是剩余的
    
    ####  eth
    # eth_token_rtoken = {
    #     'pMetis': 'Metis', 'WFTM': 'FTM', 'wROSE': 'WROSE', 'LP-BOBA': 'BOBA', 'wHAPI': 'HAPI', 'pRACA': 'RACA', 
    #     'sAVAX': 'AVAX', 'wOMI': 'OMI', 'YFII': 'YFI', 'wCELO': 'CELO', 'pCELL': 'CELL', 'sRLY': 'RLY', 'bATOM': 'BATOM', 
    #     "AAVE.e" : "AAVE", "WETH" : "ETH", "WBTC" : "BTC"}
    # eth_stable_coin = ["USDC","USDT","DAI","yvDAI","BUSD","TUSD","USD","USDD","USDK","LUSD","PUSD","cUSD","alUSD"]

    #### bsc  
    # eth_token_rtoken = {'pMetis': 'Metis', 'WFTM': 'FTM', 'wROSE': 'ROSE', 'LP-BOBA': 'BOBA', 'wHAPI': 'HAPI', 'pRACA': 'RACA', 'WSYS': 'SYS', 
    # 'wsSQUID': 'SQUID', 'sAVAX': 'AVAX', 'wOMI': 'OMI', 'YFII': 'YFI', 'wCELO': 'CELO', 'pCELL': 'CELL', 'sRLY': 'RLY', 'bATOM': 'BATOM', 
    # 'BTCB': 'BTC', 'AAVE.e': 'AAVE', 'WETH': 'ETH', 'WBTC': 'BTC', 'WAVAX': 'AVAX', 'pWING': 'WING', 'ppWING': 'WING', 'BWRX': 'WRX', 
    # 'USTC': 'UST', 'WROSE': 'ROSE', 'TOMOE': 'TOMO', 'pNEO': 'NEO', 'yvSNX': 'SNX', 'WSCRT': 'SCRT', 'WKLAY': 'KLAY', 'jEUR': 'EUR', 
    # 'sSPELL': 'SPELL', 'anyIDIA': 'IDIA', 'stkBMIV2': 'BMI', 'nICE': 'ICE', 'mWSPP': 'WSPP', 'WBNB': 'BNB', 'mDOT': 'DOT', 'WMATIC': 'MATIC',
    #  'pMATIC': 'MATIC', 'anyMATIC': 'MATIC', 'BBTC': 'BTC', 'pBTC': 'BTC', 'mBTC': 'BTC', 'pMBTC': 'BTC', 'renBTC': 'BTC', 'indexBTC': 'BTC', 
    #  'anyRYOSHI': 'RYOSHI', 'CbioShib': 'bioShib', 'IoShib': 'bioShib', 'mSOL': 'SOL', 'stSOL': 'SOL', 'wAVAX': 'AVAX', 'LP-Metis': 'Metis',
    #   'LP-METIS': 'Metis', '1ELONINDEX': 'ELONINDEX', '11ELONINDEX': 'ELONINDEX', '1UST': 'UST', 'anyALICE' : 'ALICE', 
    # '11ELON': 'ELON', '1111ELON': 'ELON', 'CAKE': 'Cake', 'GCAKE': 'Cake', 'Luna': 'LUNA', 'renLUNA': 'LUNA', 'terra-luna': 'LUNA'} #66

    # eth_stable_coin = ["USDC","USDT","DAI","BUSD","TUSD","TUSD","USD","USDD","USDK","LUSD","PUSD","cUSD","alUSD", "WBUSD","BSC-USD","USDINDEX", "aUST"]

    #### polygon
    eth_token_rtoken = {'pMetis': 'Metis', 'WFTM': 'FTM', 'wROSE': 'ROSE', 'LP-BOBA': 'BOBA', 'wHAPI': 'HAPI', 'pRACA': 'RACA', 'WSYS': 'SYS', 
    'wsSQUID': 'SQUID', 'sAVAX': 'AVAX', 'wOMI': 'OMI', 'YFII': 'YFI', 'wCELO': 'CELO', 'pCELL': 'CELL', 'sRLY': 'RLY', 'bATOM': 'BATOM', 
    'BTCB': 'BTC', 'AAVE.e': 'AAVE', 'WETH': 'ETH', 'WBTC': 'BTC', 'WAVAX': 'AVAX', 'pWING': 'WING', 'ppWING': 'WING', 'BWRX': 'WRX', 
    'USTC': 'UST', 'WROSE': 'ROSE', 'TOMOE': 'TOMO', 'pNEO': 'NEO', 'yvSNX': 'SNX', 'WSCRT': 'SCRT', 'WKLAY': 'KLAY', 'jEUR': 'EUR', 
    'sSPELL': 'SPELL', 'anyIDIA': 'IDIA', 'stkBMIV2': 'BMI', 'nICE': 'ICE', 'mWSPP': 'WSPP', 'WBNB': 'BNB', 'mDOT': 'DOT', 'WMATIC': 'MATIC',
     'pMATIC': 'MATIC', 'anyMATIC': 'MATIC', 'BBTC': 'BTC', 'pBTC': 'BTC', 'mBTC': 'BTC', 'pMBTC': 'BTC', 'renBTC': 'BTC', 'indexBTC': 'BTC', 
     'anyRYOSHI': 'RYOSHI', 'CbioShib': 'bioShib', 'IoShib': 'bioShib', 'mSOL': 'SOL', 'stSOL': 'SOL', 'wAVAX': 'AVAX', 'LP-Metis': 'Metis',
      'LP-METIS': 'Metis', '1ELONINDEX': 'ELONINDEX', '11ELONINDEX': 'ELONINDEX', '1UST': 'UST', 'anyALICE' : 'ALICE', 
    '11ELON': 'ELON', '1111ELON': 'ELON', 'CAKE': 'Cake', 'GCAKE': 'Cake', 'Luna': 'LUNA', 'renLUNA': 'LUNA', 'terra-luna': 'LUNA',
    "pSTACK":"STACK", "indexUST":"UST", "pATA":"ATA", "aCRV":"CRV", "Matic":"MATIC", "ibIndexMATIC":"MATIC", "cETH":"ETH","PETH":"ETH", "indexETH":"ETH"}

    eth_stable_coin = ["USDC","USDT","DAI","BUSD","TUSD","TUSD","USD","USDD","USDK","LUSD","PUSD","cUSD","alUSD", "WBUSD","BSC-USD","USDINDEX", "aUST",
    "indexUSDC","anyUSDT","fUSDT","USDt","wUSDT","axlUSDC","cUSDC","CCUSDC","amUSDC","ceUSDC","deUSDC","hUSDC","WUSDC","MUSD","LP-USDC","XUSDP"]

    for sta in eth_stable_coin:
        eth_token_rtoken[sta] = "USDT"

    real_symble = []
    for key in symble_token:
        if key in eth_token_rtoken:
            real_symble.append(eth_token_rtoken[key])
        else:
            real_symble.append(key)
    

    same_token_list = [key for key in real_symble if key.lower() in cex_token_list]  # 相等的币
    # 'pax': 'PAXG'

    alike_token_list = {}
    for ti in cex_token_list:
        for tk in real_symble:
            if tk not in same_token_list:
                if ti in tk.lower() and ti != tk.lower():
                    alike_token_list[ti] = tk


    print(same_token_list, len(same_token_list))
    print(alike_token_list, len(alike_token_list))
    
    """
    ## func a
    # print(token_realToken, len(token_realToken))
    # print( len(symble_token) )#symble_token, len(symble_token))
    len_token = {}

    ## eth
    # eth_token_rtoken = {  #31
    #     'pMetis': 'Metis', 'WFTM': 'FTM', 'wROSE': 'ROSE', 'LP-BOBA': 'BOBA', 'wHAPI': 'HAPI', 'pRACA': 'RACA', "WSYS" : "SYS", "wsSQUID" : "SQUID",
    #     'sAVAX': 'AVAX', 'wOMI': 'OMI', 'YFII': 'YFI', 'wCELO': 'CELO', 'pCELL': 'CELL', 'sRLY': 'RLY', 'bATOM': 'BATOM', "BTCB" : "BTC",
    #     "AAVE.e" : "AAVE", "WETH" : "ETH", "WBTC" : "BTC", 'WAVAX': 'AVAX', 'pWING': 'WING', 'ppWING': 'WING', 'BWRX': 'WRX',
    #     'USTC': 'UST', 'WROSE': 'ROSE', 'TOMOE': 'TOMO', 'pNEO': 'NEO', 'yvSNX': 'SNX', 'WSCRT': 'SCRT', 'WKLAY': 'KLAY', 'jEUR': 'EUR'}
    # eth_stable_coin = ["USDC","USDT","DAI","BUSD","TUSD","TUSD","USD","USDD","USDK","LUSD","PUSD","cUSD","alUSD"]

    for sta in eth_stable_coin:
        eth_token_rtoken[sta] = "USD"

    symbleTokens = []
    for key in symble_token:
        if key in eth_token_rtoken:
            symbleTokens.append(eth_token_rtoken[key])
        else:
            symbleTokens.append(key)

    for key in symbleTokens:
    # for key in symble_token:
        len_t = len(key)
        if len_t < 42 and len_t > 0:  #固定形式
            # if len_t not in lens:
            #     lens.append(len_t)

            if len_t not in len_token:
                len_token[len_t] = [key]
            else:
                len_token[len_t].append(key)

    len_token =  dict(sorted(len_token.items(),key = lambda item:item[0]))
    # print(len_token, len(len_token)) #775

    tokens = []
    for key in len_token:
        tokens += len_token[key]
    
    joined_token = [] #分组
    same_token = [] #记录已经保存
    for index in range(len(tokens)):
        token = tokens[index]
        if len(token) > 2:
            if token not in same_token:
                # same_token.append(token)
                same = [token]
                for index2 in range(index + 1, len(tokens)):
                    token2 =  tokens[index2]
                    if token2 not in same_token:
                        if token.lower() in token2.lower():#  and token not in and 
                            same.append(token2)
                            same_token.append(token2)
                joined_token.append(same)
        else:
            joined_token.append([token])

    # print(joined_token)
    joined_token.sort(key = lambda x : len(x))

    raw_token = []
    for i in joined_token:
        raw_token += i
    print(f"{len(raw_token)}, {len(tokens)}")
    # assert len(raw_token) == len(tokens), "nums is wrong !"

    file_name = f"./erc20Tokens/token_freq/{chain}_3_same_token.csv"
    write_csv(file_name, joined_token)
    """

def parse_symbol_token():
    ## eth
    # eth_token_rtoken = {  #30
    #     'pMetis': 'Metis', 'WFTM': 'FTM', 'wROSE': 'WROSE', 'LP-BOBA': 'BOBA', 'wHAPI': 'HAPI', 'pRACA': 'RACA', "WSYS" : "SYS", "wsSQUID" : "SQUID",
    #     'sAVAX': 'AVAX', 'wOMI': 'OMI', 'YFII': 'YFI', 'wCELO': 'CELO', 'pCELL': 'CELL', 'sRLY': 'RLY', 'bATOM': 'BATOM', 
    #     "AAVE.e" : "AAVE", "WETH" : "ETH", "WBTC" : "BTC",  'WAVAX': 'AVAX', 'pWING': 'WING', 'ppWING': 'WING', 'BWRX': 'WRX',
    #     'USTC': 'UST', 'WROSE': 'ROSE', 'TOMOE': 'TOMO', 'pNEO': 'NEO', 'yvSNX': 'SNX', 'WSCRT': 'SCRT', 'WKLAY': 'KLAY', 'jEUR': 'EUR'}
    # eth_stable_coin = ["USDC","USDT","DAI","yvDAI","BUSD","TUSD","USD","USDD","USDK","LUSD","PUSD","cUSD","alUSD"]

    # same_token = ['SPELL', 'IOTX', 'CTSI', 'FXS', 'FTM', 'WOO', 'MULTI', 'AVAX', 'ANKR', 'LINK', 'POND', 'KNC', 'LDO', 'SYS', 'APE', 'ALICE', 'MKR', 
    # 'SUSHI', 'NBT', 'DIA', 'BAL', 'OCEAN', 'GALA', 'ALPHA', 'CRV', 'LUNA', 'UNI', 'AUDIO', 'SRM', 'AAVE', 'BAT', 'SOL', 'RAY', 'ENJ', 'TVK', 'KEEP', 
    # '1INCH', 'AKRO', 'FRONT', 'GRT', 'PERP', 'RSR', 'SXP', 'PAXG', 'YFI', 'COMP', 'SHIB', 'UST', 'COS', 'DODO', 'ERN', 'DYDX', 'MANA', 'LINA', 'CHZ', 
    # 'AXS', 'SAND', 'ENS', 'RARE', 'MIR', 'POLS', 'RAMP', 'PEOPLE', 'POWR', 'CVC', 'RNDR', 'MC', 'SLP', 'INJ', 'AMP', 'BNT', 'RUNE', 'GMT', 'ALCX', 'DAR', 
    # 'OM', 'WAVES', 'ZIL', 'SUPER', 'LPT', 'ANC', 'BICO', 'CELR', 'XRP', 'CHR', 'GAL', 'DEGO', 'CELO', 'NEXO', 'NEAR', 'CVX', 'QUICK', 'TRIBE', 'FLUX', 'ATA']

    ## bsc
    eth_token_rtoken = {'pMetis': 'Metis', 'WFTM': 'FTM', 'wROSE': 'ROSE', 'LP-BOBA': 'BOBA', 'wHAPI': 'HAPI', 'pRACA': 'RACA', 'WSYS': 'SYS', 
    'wsSQUID': 'SQUID', 'sAVAX': 'AVAX', 'wOMI': 'OMI', 'YFII': 'YFI', 'wCELO': 'CELO', 'pCELL': 'CELL', 'sRLY': 'RLY', 'bATOM': 'BATOM', 
    'BTCB': 'BTC', 'AAVE.e': 'AAVE', 'WETH': 'ETH', 'WBTC': 'BTC', 'WAVAX': 'AVAX', 'pWING': 'WING', 'ppWING': 'WING', 'BWRX': 'WRX', 
    'USTC': 'UST', 'WROSE': 'ROSE', 'TOMOE': 'TOMO', 'pNEO': 'NEO', 'yvSNX': 'SNX', 'WSCRT': 'SCRT', 'WKLAY': 'KLAY', 'jEUR': 'EUR', 
    'sSPELL': 'SPELL', 'anyIDIA': 'IDIA', 'stkBMIV2': 'BMI', 'nICE': 'ICE', 'mWSPP': 'WSPP', 'WBNB': 'BNB', 'mDOT': 'DOT', 'WMATIC': 'MATIC',
     'pMATIC': 'MATIC', 'anyMATIC': 'MATIC', 'BBTC': 'BTC', 'pBTC': 'BTC', 'mBTC': 'BTC', 'pMBTC': 'BTC', 'renBTC': 'BTC', 'indexBTC': 'BTC', 
     'anyRYOSHI': 'RYOSHI', 'CbioShib': 'bioShib', 'IoShib': 'bioShib', 'mSOL': 'SOL', 'stSOL': 'SOL', 'wAVAX': 'AVAX', 'LP-Metis': 'Metis',
      'LP-METIS': 'Metis', '1ELONINDEX': 'ELONINDEX', '11ELONINDEX': 'ELONINDEX', '1UST': 'UST', 'anyALICE' : 'ALICE', 
    '11ELON': 'ELON', '1111ELON': 'ELON', 'CAKE': 'Cake', 'GCAKE': 'Cake', 'Luna': 'LUNA', 'renLUNA': 'LUNA', 'terra-luna': 'LUNA'} #66

    eth_stable_coin = ["USDC","USDT","DAI","BUSD","TUSD","TUSD","USD","USDD","USDK","LUSD","PUSD","cUSD","alUSD", "WBUSD","BSC-USD","USDINDEX", "aUST"]
    same_token = {'CTSI', 'NBT', 'AVAX', 'YFI', 'BICO', 'UNI', 'BTC', 'ROSE', 'T', 'GALA', 'NEXO', 'ARPA', 'DOGE', 'GMT', 'CHR', 'C98', 'SUSHI', 'BLZ', 'LDO', 
    'SPELL', 'OM', 'FXS', 'EGLD', 'BIFI', 'WIN', 'MATIC', 'ONG', 'AUDIO', 'POLS', 'ORN', 'LTC', 'NEO', 'VOXEL', 'KNC', 'ONT', 'FIS', 'MC', 'ADA', 
    'DATA', 'STG', 'ALPHA', 'FRONT', 'CFX', 'DOT', 'ONE', 'ATOM', 'FLUX', 'AAVE', 'ANKR', 'FARM', 'NEAR', 'ALPACA', 'ALICE', 'AUTO', 'MANA', 'SLP',
    'MULTI', 'SYS', 'SOL', 'SHIB', 'ETH', 'FIL', 'TWT', 'BNB', 'GAL', 'TRIBE', 'DAR', 'QI', 'BAT', 'IDEX', 'SUPER', 'ETC', 'IOTX', 'LUNA', 'MIR', 
    'POND', 'SXP', 'RAY', 'CLV', 'CELO', 'XMR', 'Cake', 'DEGO', 'INJ', 'Sushi', 'DODO', 'UST', 'FTM', 'COMP', 'ANC', 'WOO', 'ATA', 'LINK', 'BETA',
    'CELR', 'ZIL', 'WING', 'EUR', 'RAMP', 'SAND', 'SRM', 'NULS', 'APE', 'XRP', '1INCH', 'RUNE', 'BSW', 'AXS', 'SCRT', 'BAND'}
    
    ## polygon
    # eth_token_rtoken ={'pMetis': 'Metis', 'WFTM': 'FTM', 'wROSE': 'ROSE', 'LP-BOBA': 'BOBA', 'wHAPI': 'HAPI', 'pRACA': 'RACA', 'WSYS': 'SYS', 
    # 'wsSQUID': 'SQUID', 'sAVAX': 'AVAX', 'wOMI': 'OMI', 'YFII': 'YFI', 'wCELO': 'CELO', 'pCELL': 'CELL', 'sRLY': 'RLY', 'bATOM': 'BATOM', 
    # 'BTCB': 'BTC', 'AAVE.e': 'AAVE', 'WETH': 'ETH', 'WBTC': 'BTC', 'WAVAX': 'AVAX', 'pWING': 'WING', 'ppWING': 'WING', 'BWRX': 'WRX', 
    # 'USTC': 'UST', 'WROSE': 'ROSE', 'TOMOE': 'TOMO', 'pNEO': 'NEO', 'yvSNX': 'SNX', 'WSCRT': 'SCRT', 'WKLAY': 'KLAY', 'jEUR': 'EUR', 
    # 'sSPELL': 'SPELL', 'anyIDIA': 'IDIA', 'stkBMIV2': 'BMI', 'nICE': 'ICE', 'mWSPP': 'WSPP', 'WBNB': 'BNB', 'mDOT': 'DOT', 'WMATIC': 'MATIC',
    #  'pMATIC': 'MATIC', 'anyMATIC': 'MATIC', 'BBTC': 'BTC', 'pBTC': 'BTC', 'mBTC': 'BTC', 'pMBTC': 'BTC', 'renBTC': 'BTC', 'indexBTC': 'BTC', 
    #  'anyRYOSHI': 'RYOSHI', 'CbioShib': 'bioShib', 'IoShib': 'bioShib', 'mSOL': 'SOL', 'stSOL': 'SOL', 'wAVAX': 'AVAX', 'LP-Metis': 'Metis',
    #   'LP-METIS': 'Metis', '1ELONINDEX': 'ELONINDEX', '11ELONINDEX': 'ELONINDEX', '1UST': 'UST', 'anyALICE' : 'ALICE', 
    # '11ELON': 'ELON', '1111ELON': 'ELON', 'CAKE': 'Cake', 'GCAKE': 'Cake', 'Luna': 'LUNA', 'renLUNA': 'LUNA', 'terra-luna': 'LUNA',
    # "pSTACK":"STACK", "indexUST":"UST", "pATA":"ATA", "aCRV":"CRV", "Matic":"MATIC", "ibIndexMATIC":"MATIC", "cETH":"ETH","PETH":"ETH", "indexETH":"ETH"}

    # eth_stable_coin = ["USDC","USDT","DAI","BUSD","TUSD","TUSD","USD","USDD","USDK","LUSD","PUSD","cUSD","alUSD", "WBUSD","BSC-USD","USDINDEX", "aUST","indexUSDC","anyUSDT","fUSDT","USDt",
    #                 "wUSDT","axlUSDC","cUSDC","CCUSDC","amUSDC","ceUSDC","deUSDC","hUSDC","WUSDC","MUSD","LP-USDC","XUSDP"]
    # same_token = {'CTSI', 'FXS', 'BIFI', 'ONE', 'RAY', 'ATOM', 'CELO', 'FLUX', 'AVAX', 'YFI', 'RAD', 'AAVE', 'ANKR', 'UNI', 'BTC', 'ROSE', 'MATIC', 'ONG',
    #         'ENJ', 'UST', 'FUN', 'FTM', 'WOO', 'PLA', 'ADX', 'BAL', 'ATA', 'MANA', 'LINK', 'BAND', 'MULTI', 'SOL', 'SHIB', 'bat', 'ETH', 'KNC', 'EUR',
    #         'SNX', 'ONT', 'GRT', 'SAND', 'BNB', 'SRM', 'APE', '1INCH', 'SUSHI', 'TVK', 'ADA', 'DATA', 'QI', 'AMP', 'IDEX', 'BAT', 'LDO', 'FIDA', 'QUICK', 
    #         'SUPER', 'AXS', 'LUNA', 'CRV', 'OM'}

    real_token_path = f"./erc20Tokens/fill_erc20Token/real_{chain}_token_block.csv"
    real_tokens = readDefaultCsv(real_token_path)
    token_realToken = { getStandAddr(record_token["token"]) : record_token for record_token in real_tokens}

    symbol_token = {}  # symble : [token,txhash,blockno,price,rtoken,symbol]
    
    for token in token_realToken:
        rsymbol = token_realToken[token]["rsymbol"]
        rtoken = token_realToken[token]["rtoken"]
        symbol = token_realToken[token]["symbol"]
        token = token_realToken[token]["token"]

        if rsymbol != "0":  #不区分大小写
            if rsymbol not in eth_token_rtoken:
                if rsymbol not in eth_stable_coin:
                    # if rsymbol not in same_token:

                    if rsymbol not in symbol_token:
                        symbol_token[rsymbol] = [rtoken]
                    else:
                        if rtoken not in symbol_token[rsymbol]:
                            symbol_token[rsymbol].append(rtoken)

        elif symbol != "0":  #'symbol': ''
            if symbol not in eth_token_rtoken:
                if symbol not in eth_stable_coin:
                    # if symbol not in same_token:

                    if symbol not in symbol_token:
                        symbol_token[symbol] = [token]
                    else:
                        if token not in symbol_token[symbol]:
                            symbol_token[symbol].append(token)
        else:
            pass
    
    # same_symbol = []
    # hava_check = ["BTC", "ETH", "MATIC", "BNB", "LUNA"]
    # for k_token in symbol_token:
    #     if k_token not in hava_check:
    #         if len(symbol_token[k_token]) > 1:
    #             same_symbol.append( [k_token] + symbol_token[k_token]  )
                # print(k_token, symbol_token[k_token])
    
    # file_name = f"./erc20Tokens/token_freq/{chain}_same_symbol_list.csv"
    # write_csv(file_name, same_symbol)
    

    # need_attention = []
    # for wtoken in same_token: #same_token 等价于在 cex 中有
    #     if wtoken not in hava_check:  #
    #         if wtoken not in symbol_token: 
    #             if wtoken not in need_attention:
    #                 need_attention.append(wtoken)
    # print(f"do not need attention token {need_attention}", len(need_attention))

    same_symbol = []
    hava_check = ["BTC", "ETH", "MATIC", "BNB", "LUNA"]
    for k_token in symbol_token: 
        if k_token not in hava_check:
            if len(symbol_token[k_token]) > 1:
                same_symbol.append( k_token.lower() )
    
    
    out = []
    for sm in same_token:
        if sm not in hava_check:
            if sm.lower() not in same_symbol:
                # out.append(sm)
                # out.append( [sm, symbol_token[sm]])
                try:
                    for addr in symbol_token[sm]:
                        out.append( [sm, addr])
                except:
                    print(sm)
    

                    #  out.append(sm)
    # print("out", out, len(out))
    # write_json("aaa.json", symbol_token)
    write_csv("aaa.csv", out)


def get_some_tokens():

    ## eth
    # eth_token_rtoken = {  #30
    #     'pMetis': 'Metis', 'WFTM': 'FTM', 'wROSE': 'WROSE', 'LP-BOBA': 'BOBA', 'wHAPI': 'HAPI', 'pRACA': 'RACA', "WSYS" : "SYS", "wsSQUID" : "SQUID",
    #     'sAVAX': 'AVAX', 'wOMI': 'OMI', 'YFII': 'YFI', 'wCELO': 'CELO', 'pCELL': 'CELL', 'sRLY': 'RLY', 'bATOM': 'BATOM', 
    #     "AAVE.e" : "AAVE", "WETH" : "ETH", "WBTC" : "BTC",  'WAVAX': 'AVAX', 'pWING': 'WING', 'ppWING': 'WING', 'BWRX': 'WRX',
    #     'USTC': 'UST', 'WROSE': 'ROSE', 'TOMOE': 'TOMO', 'pNEO': 'NEO', 'yvSNX': 'SNX', 'WSCRT': 'SCRT', 'WKLAY': 'KLAY', 'jEUR': 'EUR'}
    # eth_stable_coin = ["USDC","USDT","DAI","yvDAI","BUSD","TUSD","USD","USDD","USDK","LUSD","PUSD","cUSD","alUSD"]

    ## bsc
    # eth_token_rtoken = {'pMetis': 'Metis', 'WFTM': 'FTM', 'wROSE': 'ROSE', 'LP-BOBA': 'BOBA', 'wHAPI': 'HAPI', 'pRACA': 'RACA', 'WSYS': 'SYS', 
    # 'wsSQUID': 'SQUID', 'sAVAX': 'AVAX', 'wOMI': 'OMI', 'YFII': 'YFI', 'wCELO': 'CELO', 'pCELL': 'CELL', 'sRLY': 'RLY', 'bATOM': 'BATOM', 
    # 'BTCB': 'BTC', 'AAVE.e': 'AAVE', 'WETH': 'ETH', 'WBTC': 'BTC', 'WAVAX': 'AVAX', 'pWING': 'WING', 'ppWING': 'WING', 'BWRX': 'WRX', 
    # 'USTC': 'UST', 'WROSE': 'ROSE', 'TOMOE': 'TOMO', 'pNEO': 'NEO', 'yvSNX': 'SNX', 'WSCRT': 'SCRT', 'WKLAY': 'KLAY', 'jEUR': 'EUR', 
    # 'sSPELL': 'SPELL', 'anyIDIA': 'IDIA', 'stkBMIV2': 'BMI', 'nICE': 'ICE', 'mWSPP': 'WSPP', 'WBNB': 'BNB', 'mDOT': 'DOT', 'WMATIC': 'MATIC',
    #  'pMATIC': 'MATIC', 'anyMATIC': 'MATIC', 'BBTC': 'BTC', 'pBTC': 'BTC', 'mBTC': 'BTC', 'pMBTC': 'BTC', 'renBTC': 'BTC', 'indexBTC': 'BTC', 
    #  'anyRYOSHI': 'RYOSHI', 'CbioShib': 'bioShib', 'IoShib': 'bioShib', 'mSOL': 'SOL', 'stSOL': 'SOL', 'wAVAX': 'AVAX', 'LP-Metis': 'Metis',
    #   'LP-METIS': 'Metis', '1ELONINDEX': 'ELONINDEX', '11ELONINDEX': 'ELONINDEX', '1UST': 'UST', 'anyALICE' : 'ALICE', 
    # '11ELON': 'ELON', '1111ELON': 'ELON', 'CAKE': 'Cake', 'GCAKE': 'Cake', 'Luna': 'LUNA', 'renLUNA': 'LUNA', 'terra-luna': 'LUNA'} #66
    # eth_stable_coin = ["USDC","USDT","DAI","BUSD","TUSD","TUSD","USD","USDD","USDK","LUSD","PUSD","cUSD","alUSD", "WBUSD","BSC-USD","USDINDEX", "aUST"]

    ## polygon
    eth_token_rtoken = {'pMetis': 'Metis', 'WFTM': 'FTM', 'wROSE': 'ROSE', 'LP-BOBA': 'BOBA', 'wHAPI': 'HAPI', 'pRACA': 'RACA', 'WSYS': 'SYS', 
    'wsSQUID': 'SQUID', 'sAVAX': 'AVAX', 'wOMI': 'OMI', 'YFII': 'YFI', 'wCELO': 'CELO', 'pCELL': 'CELL', 'sRLY': 'RLY', 'bATOM': 'BATOM', 
    'BTCB': 'BTC', 'AAVE.e': 'AAVE', 'WETH': 'ETH', 'WBTC': 'BTC', 'WAVAX': 'AVAX', 'pWING': 'WING', 'ppWING': 'WING', 'BWRX': 'WRX', 
    'USTC': 'UST', 'WROSE': 'ROSE', 'TOMOE': 'TOMO', 'pNEO': 'NEO', 'yvSNX': 'SNX', 'WSCRT': 'SCRT', 'WKLAY': 'KLAY', 'jEUR': 'EUR', 
    'sSPELL': 'SPELL', 'anyIDIA': 'IDIA', 'stkBMIV2': 'BMI', 'nICE': 'ICE', 'mWSPP': 'WSPP', 'WBNB': 'BNB', 'mDOT': 'DOT', 'WMATIC': 'MATIC',
     'pMATIC': 'MATIC', 'anyMATIC': 'MATIC', 'BBTC': 'BTC', 'pBTC': 'BTC', 'mBTC': 'BTC', 'pMBTC': 'BTC', 'renBTC': 'BTC', 'indexBTC': 'BTC', 
     'anyRYOSHI': 'RYOSHI', 'CbioShib': 'bioShib', 'IoShib': 'bioShib', 'mSOL': 'SOL', 'stSOL': 'SOL', 'wAVAX': 'AVAX', 'LP-Metis': 'Metis',
      'LP-METIS': 'Metis', '1ELONINDEX': 'ELONINDEX', '11ELONINDEX': 'ELONINDEX', '1UST': 'UST', 'anyALICE' : 'ALICE', 'EURT' : 'eur',
    '11ELON': 'ELON', '1111ELON': 'ELON', 'CAKE': 'Cake', 'GCAKE': 'Cake', 'Luna': 'LUNA', 'renLUNA': 'LUNA', 'terra-luna': 'LUNA',
    "pSTACK":"STACK", "indexUST":"UST", "pATA":"ATA", "aCRV":"CRV", "Matic":"MATIC", "ibIndexMATIC":"MATIC", "cETH":"ETH","PETH":"ETH", "indexETH":"ETH"}

    eth_stable_coin = ["USDC","USDT","DAI","BUSD","TUSD","TUSD","USD","USDD","USDK","LUSD","PUSD","cUSD","alUSD", "WBUSD","BSC-USD","USDINDEX", "aUST",
    "indexUSDC","anyUSDT","fUSDT","USDt","wUSDT","axlUSDC","cUSDC","CCUSDC","amUSDC","ceUSDC","deUSDC","hUSDC","WUSDC","MUSD","LP-USDC","XUSDP"]
    for sta in eth_stable_coin:
        eth_token_rtoken[sta] = "USDT"

    
    # table 1   token
    real_token_path = f"./erc20Tokens/fill_erc20Token/real_{chain}_token_block.csv"
    real_tokens = readDefaultCsv(real_token_path)
    token_realToken = { getStandAddr(record_token["token"]) : record_token for record_token in real_tokens}
    
    # table 2  #token : txhash,blockno
    token_txhash_path = f"./erc20Tokens/token_freq/{chain}_token.csv"
    token_txhash_infos = readDefaultCsv(token_txhash_path)
    token_txhash_blockno = {} # token : [ [txh, blockno] ]
    for tokens in token_txhash_infos:        #token,txhash,blockno
        token = getStandAddr(tokens["token"])
        if token not in token_txhash_blockno:
            token_txhash_blockno[token] = [[tokens["txhash"], tokens["blockno"]]]
        else:
            token_txhash_blockno[token].append([tokens["txhash"], tokens["blockno"]])
    
    # table 3   blockno date
    time_block_dir = "./crossChainProject/timeBlock"
    block_timestamp = get_block_timestamp(time_block_dir, chain)  # return  {block : [timestamp, date]}  sort()

    # writes = [ [k, block_timestamp[k][0], block_timestamp[k][1]] for k in block_timestamp]
    # write_csv("aaaaaaaa.csv", writes)

    # table 4 price from cex
    token_price_dex_dir = "./erc20Tokens/tokenPrice/cex_token_price"

    ## start logic .................. 
    symbol_token = {}  # symble : [token,txhash,blockno,price,rtoken,symbol]
    no_symbol_token = []  # token : [token,txhash,blockno,price,rtoken,0]
    for token in token_realToken:
        rsymbol = token_realToken[token]["rsymbol"]
        rtoken = token_realToken[token]["rtoken"]
        symbol = token_realToken[token]["symbol"]
        token = token_realToken[token]["token"]

        if rsymbol != "0":  #优先级按照顺序 
            if rsymbol not in symbol_token:
                symbol_token[rsymbol] = [ [rtoken, token] ]
            else:
                symbol_token[rsymbol].append([rtoken, token])

        elif symbol != "0":  #'symbol': ''
            if symbol not in symbol_token:
                symbol_token[symbol] = [ [0, token] ]
            else:
                symbol_token[symbol].append([0, token])

        elif token != "0":
            no_symbol_token.append(token)

        else:
            print(f"need check {record_token}")
            break
        
        # if token == "0x53BBE80F77ac24e5eA1B806D5e67Ed1e3f4B37FE":
        #     print(token_realToken[token])
        #     assert 1 ==0, "wrong"
    
    # 合并token, symbol
    symbol_txh_list = {}
    symbol_addr = {} # symbol : token
    for symbol in symbol_token:  # 遍历 token 
        dex_rtoken = 0
        dex_token = 0
        for token_addr in symbol_token[symbol]: # token_addr = [addr1, addr2]
            rtoken = token_addr[0]
            token = token_addr[1]

            if not dex_rtoken:
                if rtoken != "0":
                    dex_rtoken = rtoken
            if not dex_token:
                if token != "0":
                    dex_token = token

            raw_list = [ [token, t[0], t[1]]  for t in token_txhash_blockno[token]]
            # raw_list = [ token, token_txhash_blockno[token][0], token_txhash_blockno[token][1] ] #stoken, txhash, blockno

            # if symbol in eth_stable_coin: # USDT   #稳定币
            #     if symbol not in symbol_txh_list:
            #         symbol_txh_list["USDT"] =  raw_list 
            #     else:
            #         symbol_txh_list["USDT"] += raw_list 

            if symbol in eth_token_rtoken:  # symbol -> rsymbol
                symbol = eth_token_rtoken[symbol]
                if symbol not in symbol_txh_list:
                    symbol_txh_list[symbol] = raw_list
                else:
                    symbol_txh_list[symbol] += raw_list 

            else:
                if symbol not in symbol_txh_list:
                    symbol_txh_list[symbol] = raw_list
                else:
                    symbol_txh_list[symbol] += raw_list 
        if dex_rtoken:
            symbol_addr[symbol] = dex_rtoken
        else:
            symbol_addr[symbol] = dex_token

    ## 填充价格
    filled_token_price = []
    unfilled_token_price = []
    # dex_token_price = []
    # usdt = []
    # for symbol in tqdm(symbol_txh_list):
    #     if symbol == "USDT":
    #         usdt += symbol_txh_list[symbol]
    # print(usdt, len(usdt))


    for symbol in tqdm(symbol_txh_list):
        rtoken = symbol_addr[symbol]
        if symbol == "USDT":
            for txh in symbol_txh_list[symbol]:
                filled_token_price.append([txh[0], txh[1], txh[2], 1, 0, symbol])
            continue

        token_price_path = glob.glob(token_price_dex_dir + f"/{symbol.lower()}_usdt_*.csv")
        if len(token_price_path) > 0:
            token_price = readCsvPrice(token_price_path[0])  # ("time1_time2", 22 )
            for txh in symbol_txh_list[symbol]:
                blockno = int(txh[2])
                # print(blockno, block_timestamp[blockno])
                timestamp = int(block_timestamp[blockno][0])

                if timestamp in token_price:
                    price = token_price[timestamp]
                    filled_token_price.append([txh[0], txh[1], txh[2], price, rtoken, symbol])
                else:
                    unfilled_token_price.append([txh[0], txh[1], txh[2], 0, rtoken, symbol])

        else: # cex 中无价格
            for txh in symbol_txh_list[symbol]:
                unfilled_token_price.append([txh[0], txh[1], txh[2], 0, rtoken, symbol])
    
    ## write csv ....
    labels = ("token", "txhash", "blockno","price","rtoken","symbol")

    ### write price
    file_name = f"./erc20Tokens/token_freq/cex_price/{chain}_have_price.csv"
    write_csv_labels(file_name, filled_token_price, labels)
    print(f"have price : {len(filled_token_price)}")

    ### no price have symbol
    file_name = f"./erc20Tokens/token_freq/cex_price/{chain}_no_price.csv"
    write_csv_labels(file_name, unfilled_token_price, labels)
    print(f"have symbol but no price, need dex {len(unfilled_token_price)}")

    ### no price no symbol
    file_name = f"./erc20Tokens/token_freq/cex_price/{chain}_no_priceSymbol.csv"
    unfilled_token_price = []
    for token_addr in no_symbol_token:
        for txh in token_txhash_blockno[token_addr]:
            unfilled_token_price.append([token_addr, txh[0], txh[1], 0, token_addr, 0])
    write_csv_labels(file_name, unfilled_token_price, labels)
    print(f"no price no symbol {len(unfilled_token_price)}")
    

    # find_token = getStandAddr("0xF49818b5d7dE5B0DBfcCb3Ddcd14e1f0AA1A6f01")
    # outs = []
    # for sub in token_txhash_blockno[find_token]:
    #     blockno = sub[1]
    #     outs.append(block_timestamp[blockno])
    # print(outs)

def check_cex_price():  
    time_block_dir = "./crossChainProject/timeBlock"
    block_timestamp = get_block_timestamp(time_block_dir, chain)  # return  {block : [timestamp, date]}  sort()

    token_list = []
    token_realToken = []
    file_name = f"./erc20Tokens/token_freq/cex_price/{chain}_have_price.csv"
    filters = ["ETH", "USDT", "BNB", "MATIC", "BTC", "symbol"]  #FTM,36214,MIM,34679,UST,16377,PLT,10380,SPELL,9736
    real_tokens = readCsvRaw(file_name) #readDefaultCsv(file_name)

    for record_token in real_tokens:
        if record_token[5] not in filters:
            # print(record_token)
            blo = int(record_token[2])
            data_time = block_timestamp[str(blo)]

            token_realToken.append(record_token + [data_time])
            
            if record_token[5] not in token_list:
                token_list.append(record_token[5])
    
    print(token_list)

    file_name = f"./erc20Tokens/token_freq/shuaid/{chain}_check_price.csv"
    labels = ("token", "txhash", "blockno","price","rtoken","symbol", "date")
    # write_csv(file_name, token_realToken)
    write_csv_labels(file_name, token_realToken, labels)



def get_token_nums():
    # {'decimals': '', 'down_block': '', 'pair_tokens': '0', 'pairs': '0', 'rdecimals': '0', 'rsymbol': '0', 'rtoken': '0', 
    # 'symbol': 'DAI', 'token': '', 'up_block': '8129074'}

    realToken_freq = {}   # token symbol : nums
    # token_txhash_infos = {}  # ['txhash', 'blockno', 'rsymbol', 'rtoken', 'token', 'symbol', 'decimals'] #重要程度  后期再检查
    token_txhash_infos = []

    real_token_path = f"./erc20Tokens/fill_erc20Token/real_{chain}_token_block.csv"
    real_tokens = readDefaultCsv(real_token_path)
    # no_name_list = [record_token["token"] for record_token in real_tokens if not record_token["symbol"] ] 
    # print(no_name_list)

    token_realToken = { getStandAddr(record_token["token"]) : record_token for record_token in real_tokens} #if record_token["symbol"]

    # for key in token_realToken:
    #     token_infos = token_realToken[key]
    #     if token_infos['decimals'] and token_infos['decimals'] != '0':
    #         if token_infos['rdecimals'] and token_infos['rdecimals'] != '0':
    #             if token_infos['decimals'] != token_infos['rdecimals']:
    #                 print(token_infos)
    
    
    projects = ['portal', 'multichain', 'poly'] 
    # swap_token = {key:0 for key in projects} # project : 
    # transfer_token = {key:0 for key in projects}
    same_token = {"WMATIC" : "MATIC", "WETH" : "ETH","ETH":"ETH", "WBNB" : "BNB", "BSC" : "BNB", "Polygon" : "MATIC" }
    token_address = {"ETH" : { "ETH" : "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" , #WETH
                               "BNB" : "0xB8c77482e45F1F44dE1745F52C74426C631bDD52", #bnb   BNB WBNB      
                                "MATIC" : "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0"},
                    "BSC" : {
                            "ETH" : "0x2170Ed0880ac9A755fd29B2688956BD959F933F8" , #WETH
                            "BNB" : "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c", #bnb   BNB WBNB      
                            "MATIC" : "0xCC42724C6683B7E57334c4E856f4c9965ED682bD"
                    },

                    "Polygon" : {
                            "ETH" : "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619" , #WETH
                            "BNB" : "0x3BA4c387f786bFEE076A58914F5Bd38d668B42c3", #
                            "MATIC" : "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
                    }
    }

    total_txhash_nums = 0
    for project in projects:
        print(f"start scan project of {project}")
        save_dir = os.path.join(datasName, project, chain)
        file_path = glob.glob(save_dir + "/*.csv")
        assert len(file_path) > 0, "notice !"
        # print(file_path)

        for fi in file_path:
            sub_blocks = readCsv(fi)  #过滤出有用的交易信息
            for record in sub_blocks:
                # token_address = None
                rsymbol = None
                if record['srcToken'] not in ['BSC','ETH','Polygon']:
                    token = getStandAddr(record['srcToken'])  # 交易记录的地址
                    # print(token)
                    # rtoken = token_realToken[token]["rtoken"]
                    if token == "0x0000000000000000000000000000000000000000":
                        rsymbol = chain  #某个链的生态币
                    # else:
                    #     rsymbol = token_realToken[token]["rsymbol"]
                    #     if rsymbol == '0':
                    #         rsymbol = token_realToken[token]["symbol"]
                else:
                    rsymbol = record['srcToken']  #符号

                # print("rsymbol", rsymbol)
                if rsymbol in same_token:
                    rsymbol = same_token[rsymbol]
                    token = token_address[chain][rsymbol]
                
                # print("token", token)
                #write csv 
                token_txhash_infos.append((token, record['txhash'], record['blockno']))


    file_name = f"./erc20Tokens/token_freq/{chain}_token.csv"
    labels = ("token", "txhash", "blockno")

    token_txhash_infos.sort(key = lambda x : x[2])  #按照block排序
    write_csv_labels(file_name, token_txhash_infos, labels)
    
    # realToken_freq = sorted(realToken_freq.items(), key=lambda x:x[1], reverse=True)  排序

                # ['txhash', 'blockno', 'rsymbol', 'rtoken', 'token', 'symbol', 'decimals']
    #             txhash_infos = {}
    #             txhash_infos['txhash'] = record['txhash']
    #             txhash_infos['blockno'] = record['blockno']
    #             if token not in token_txhash_infos:
    #                 token_txhash_infos[token] = [txhash_infos]
    #             else:
    #                 token_txhash_infos[token].append(txhash_infos)
    #             total_txhash_nums += 1
    # file_name = f"./erc20Tokens/token_freq/{chain}_token.json"
    # write_json(file_name, token_txhash_infos)
    # print(f"total txhash numbers is {total_txhash_nums}")


    """
    if 1:
        for fi in file_path:
            sub_blocks = readCsv(fi)  #过滤出有用的信息
            for record in sub_blocks:
                token_address = None
                try:
                    if record['srcToken'] not in ['BSC','ETH','Polygon']:
                        token = getStandAddr(record['srcToken'])
                        # rtoken = token_realToken[token]["rtoken"]
                        if token == "0x0000000000000000000000000000000000000000":
                            rsymbol = chain  #某个链的生态币

                        else:
                            rsymbol = token_realToken[token]["rsymbol"]
                            if rsymbol == '0':
                                rsymbol = token_realToken[token]["symbol"]

                    else:
                        rsymbol = record['srcToken']  #符号

                    if rsymbol in same_token:
                        rsymbol = same_token[rsymbol]
                    
                    if rsymbol not in realToken_freq:
                        realToken_freq[rsymbol] = 1
                    else:
                        realToken_freq[rsymbol] += 1

                    # token_txhash_infos
                    # ['txhash', 'blockno', 'rsymbol', 'rtoken', 'symbol', 'decimals']


                except:
                    pass

                # if rsymbol == "":
                #     print("file_path", file_path)
                #     print(record['txhash'])
                #     break


                # if rsymbol == "anyMATIC":
                #     print(record['txhash'])
        # break
    
    realToken_freq = sorted(realToken_freq.items(), key=lambda x:x[1], reverse=True)  # True 从大到小  False 小到大
    # # print(f"total nums is {len(token_txh_nums)}")
    # # token_freq = dict(realToken_freq)
    # # file_name = f"{chain}_freq.json"
    # # with open(file_name,"w") as f:
    # #     json.dump(token_freq,f)
    file_name = f"./erc20Tokens/token_freq/{chain}_freq.csv"
    write_csv(file_name, realToken_freq)
    """
                # if record['srcToken'] != record['dstToken']:
                #     swap_token[project] += 1
                #     print(record['txhash'])
                # else:
                #     transfer_token[project] += 1
    # print(swap_token, transfer_token)

    # swap_token(交换token)  transfer_token（跨链转移）
    # BSC {'multichain': 0, 'poly': 0, 'portal': 0} {'multichain': 1373167, 'poly': 131368, 'portal': 196231} # 1700766
    # ETH {'multichain': 0, 'poly': 0, 'portal': 0} {'multichain': 317432, 'poly': 33971, 'portal': 71793}  # 423196
    # Polygon {'multichain': 4, 'poly': 0, 'portal': 0} {'multichain': 721085, 'poly': 18540, 'portal': 70746} #810371 + 4
        # 0x757ba3aee960fe5e83d22f341327e83ef7591809c7f5471b06c43134f7eee900
        # 0x5167af2e1a03ffbdbcfdbf11231b6f45ba6649f80299a8b14c0189f804f29599
        # 0x6f5a5335cc50f3966a1d7c79b8819e078ec6b98e4eb0c597144e0578af713a44
        # 0x7220331bba432431729024505def67b9c1965a5c9110059ead23fe5714f1bdcd

def get_tokens_freq(): # 统计三个项目所有的token频率
    # all_chain_freq = {}
    # for sub_chain in ['BSC','ETH','Polygon']:
    #     token_freq_path = f"./erc20Tokens/token_freq/cex_price/need_price/{sub_chain}_no_price.csv"
    #     sub_token_freq = readCsvRaw(token_freq_path)
    #     sub_token_freq = dict(sub_token_freq)
    #     for sub_token in sub_token_freq:
    #         if sub_token not in all_chain_freq:
    #             all_chain_freq[sub_token] = int(sub_token_freq[sub_token])
    #         else:
    #             all_chain_freq[sub_token] += int(sub_token_freq[sub_token])
    
    # all_chain_freq = sorted(all_chain_freq.items(), key=lambda x:x[1], reverse=True)  #False 小到大
    # file_name = f"./erc20Tokens/token_freq/all_chain_freq.csv"
    # write_csv(file_name, all_chain_freq)

    
    for sub_chain in ['BSC', 'ETH','Polygon']: #
        all_chain_freq = {}
        token_freq_path = f"./erc20Tokens/token_freq/cex_price/need_price/{sub_chain}_no_price.csv"
        sub_token_freq = readDefaultCsv(token_freq_path)
        
        for sub_token in sub_token_freq:
            symbol = sub_token["symbol"]
            try:
                if symbol not in all_chain_freq:
                    all_chain_freq[symbol] = 1
                else:
                    all_chain_freq[symbol] += 1
            except:
                print(sub_chain, symbol)
                
        all_chain_freq = sorted(all_chain_freq.items(), key=lambda x:x[1], reverse=True)  #False 小到大
        file_name = f"./erc20Tokens/token_freq/cex_price/need_price/{sub_chain}_fre_token.csv"
        write_csv(file_name, all_chain_freq)


def get_token_timestamp():
    token_chain_nums = {}
    for sub_chain in ['BSC', 'ETH','Polygon']: #
        file_name = f"./erc20Tokens/token_freq/cex_price/need_price/{sub_chain}_fre_token.csv"
        tokens_fre = readCsvRaw(file_name)
        symbol_nums = {}
        for symbol in tokens_fre:
            symbol_nums[symbol[0]] = symbol[1]
        token_chain_nums[sub_chain] = symbol_nums
        # break 
    # print(token_chain_nums)
    chain_block_timestamp = {}
    chain_tokens_txh = {}
    for sub_chain in ['BSC', 'ETH','Polygon']:
        time_block_dir = "./crossChainProject/timeBlock"
        block_timestamp = get_block_timestamp(time_block_dir, sub_chain)
        token_freq_path = f"./erc20Tokens/token_freq/cex_price/need_price/{sub_chain}_no_price.csv"
        tokens_txh = readDefaultCsv(token_freq_path)
        chain_block_timestamp[sub_chain] = block_timestamp
        chain_tokens_txh[sub_chain] = tokens_txh

    # symbol = "UST"
    for symbol in token_chain_nums['ETH']:
        if int(token_chain_nums['ETH'][symbol]) < 500:
            break

        for sub_chain in ['BSC', 'ETH','Polygon']: #
            token_blocks = []
            tokens_txh = chain_tokens_txh[sub_chain]
            block_timestamp = chain_block_timestamp[sub_chain]
            for sub_token in tokens_txh:
                if symbol == sub_token["symbol"]:
                    token_blocks.append( int(sub_token["blockno"]) )
            if len(token_blocks) > 0:
                start_blno, end_blno = min(token_blocks), max(token_blocks)
                print(f"the token {symbol} in {sub_chain} is in {start_blno}_{block_timestamp[start_blno]} --> {end_blno}_{block_timestamp[end_blno]}")
                print(f"{sub_chain}_{token_chain_nums[sub_chain][symbol]}")



def filter_blockno():
    end_block = {"Polygon" : 32534395, "ETH" : 15449611, 'BSC' : 20936752 }

    labels = ("token", "txhash", "blockno","price","rtoken","symbol")
    for sub_chain in ['BSC', 'ETH','Polygon']:
        file_paths = [f"./erc20Tokens/token_freq/cex_price/need_price/bak/{sub_chain}_no_price.csv", 
                     f"./erc20Tokens/token_freq/cex_price/need_price/bak/{sub_chain}_no_priceSymbol.csv"]

        for fi_path in file_paths:
            outs = []
            blockno_list = readDefaultCsv(fi_path)
            print(f"before the length is {len(blockno_list)}")
            for txhash in blockno_list:
                if int(txhash["blockno"]) <= end_block[sub_chain]:
                    outs.append(txhash)
        
            save_dir = fi_path.replace("/bak","")
            # print(save_dir)
            write_csv_dict(save_dir, outs, labels)
            print(f"after filter {len(outs)}")
            # break
        # break
            # 
            
def clean_for_dex():
    from token_config import tokenData
    #清理数据之后是使用dex进行价格获取
    # have price -> no price
    # have price -> not price
    labels = ("token", "txhash", "blockno","price","rtoken","symbol")
    not_price = tokenData["dex_no_price"][chain]
    dex_price = tokenData["dex_have_price"][chain]

    cex_have_price = f"./erc20Tokens/token_freq/cex_price/{chain}_have_price.csv"  #token,txhash,blockno,price,rtoken,symbol
    dex_have_price = f"./erc20Tokens/token_freq/cex_price/{chain}_no_price.csv"

    # STEP1 拿出无法获取
    not_price_dict = {}
    cex_have_price_list = readDefaultCsv(cex_have_price)
    dex_have_price_list = readDefaultCsv(dex_have_price)
    print(f"before_length: cex_{len(cex_have_price_list)}, dex_{len(dex_have_price_list)}")

    cex_have_price_remain = []
    dex_have_price_remain = []

    ## 剔除not
    for price_list in [cex_have_price_list, dex_have_price_list]:
        num = 0
        for sub_cex in price_list:
            if sub_cex["token"] in not_price: #剔除出去
                if sub_cex["token"] not in not_price_dict:
                    not_price_dict[sub_cex["token"]] = [ [sub_cex["token"], sub_cex["txhash"], sub_cex["blockno"], 0, sub_cex["rtoken"], sub_cex["symbol"] ] ]
                else:
                    not_price_dict[sub_cex["token"]].append( [sub_cex["token"], sub_cex["txhash"], sub_cex["blockno"], 0, sub_cex["rtoken"], sub_cex["symbol"]] )
                num += 1

        print(f"nums_{num}")

    assert len(not_price_dict) == len(not_price), "not price number is wrong !"
    not_price_name = f"./erc20Tokens/token_freq/cex_price/NOT_PRICE/{chain}_no_price.csv"
    not_price_list = []

    for k in not_price_dict:
        for r in not_price_dict[k]: # []
            not_price_list.append(r)
    write_csv_labels(not_price_name, not_price_list, labels)
    # print(f"not price {not_price_list}, {len(not_price_list)}")

    #from cex to dex
    for sub_cex in cex_have_price_list:
        if sub_cex["token"] in not_price:
            print(f"not price {sub_cex['token']}")
            continue

        elif sub_cex["token"] in dex_price:  # 
            # sub_cex["rtoken"] = sub_cex["token"]  
            # sub_cex["price"] = 0
            print(f"cex in dex {sub_cex['token']}")
            dex_have_price_remain.append( [sub_cex["token"], sub_cex["txhash"], sub_cex["blockno"], 0, sub_cex["token"], sub_cex["symbol"]] )
        
        else:
            cex_have_price_remain.append([sub_cex["token"], sub_cex["txhash"], sub_cex["blockno"], sub_cex["price"], sub_cex["rtoken"], sub_cex["symbol"]])
    
    for sub_dex in dex_have_price_list:
        if sub_dex["token"] not in not_price_dict: #没有剔除掉
            if sub_dex["token"] in dex_price:  #bsc 
                sub_dex["rtoken"] = sub_dex["token"]
            dex_have_price_remain.append([sub_dex["token"], sub_dex["txhash"], sub_dex["blockno"], 0, sub_dex["rtoken"], sub_dex["symbol"]])
    
    print(f"after_length: cex_{len(cex_have_price_remain)}, dex_{len(dex_have_price_remain)}")
    assert len(cex_have_price_remain) + len(dex_have_price_remain) + len(not_price_list) == len(cex_have_price_list) + len(dex_have_price_list)

    cex_file_name = f"./erc20Tokens/token_freq/cex_price/cex_2_dex/{chain}_have_price.csv"
    dex_file_name = f"./erc20Tokens/token_freq/cex_price/cex_2_dex/{chain}_no_price.csv"
    write_csv_labels(cex_file_name, cex_have_price_remain, labels)
    write_csv_labels(dex_file_name, dex_have_price_remain,  labels)
    



def get_block_time_filled():
    time_block_dir = "./crossChainProject/timeBlock"
    timestamp_path = glob.glob(time_block_dir + f"/{chain}*.csv")
    assert len(timestamp_path) > 0, "notice !"
    print("timestamp_path", timestamp_path)
    block_project = {}
    for ti in timestamp_path:
        block_times = readCsvRaw(ti)
        for bt in block_times:
            if bt[0] not in block_project:
                block_project[bt[0]] = bt[1]
    print(f"the haved blocks times {len(block_project)}")  #

    all_blocktime = [[k, block_project[k]] for k in block_project]
    file_name2 = f"./crossChainProject/timeBlock/Polygon_all_blocktime.csv"
    write_csv(file_name2, all_blocktime)

    # token_txhash_blockno = []
    # token_txhash_path = f"./erc20Tokens/token_freq/{chain}_token.csv"
    # token_txhash_infos = readDefaultCsv(token_txhash_path)
    # for tokens in token_txhash_infos:        #token,txhash,blockno
    #     # if tokens["blockno"] not in token_txhash_blockno:
    #     token_txhash_blockno.append(tokens["blockno"])
    # token_txhash_blockno = set(token_txhash_blockno)
    # print(f"the total blocks {len(token_txhash_blockno)}")  # 

    # need_add_block = []
    # for block in token_txhash_blockno:
    #     if block not in block_project:
    #         need_add_block.append([block])
    # print(f"need addd the txh {len(need_add_block)}", need_add_block)
    # need_length = len(need_add_block)
    # need_length1 = int(need_length * 0.5)
    # # need_length2 = need_length - need_length1
    
    # file_name1 = f"./crossChainProject/timeBlock/Polygon_adds_1.csv"
    # write_csv(file_name1, need_add_block[:need_length1] )

    # file_name2 = f"./crossChainProject/timeBlock/Polygon_adds_2.csv"
    # write_csv(file_name2, need_add_block[need_length1:])


def get_logs_to_json(): #multichain poly stargate portal

    projects = ['multichain', 'poly', 'portal'] #'multichain',  'stargate'

    token_txh_logs = {}
    for project in projects:
        print(f"start scan project of {project}")
        save_dir = os.path.join(datasName, project, chain)
        file_path = glob.glob(save_dir + "/*.csv")
        assert len(file_path) > 0, "notice !"
        print(file_path)
        for fi in file_path:
            sub_blocks = readCsv(fi)
            for record in sub_blocks:
                txnHash = record['txhash']
                for token in [ record['srcToken'], record['dstToken'] ]:
                    if token not in token_txh_logs:
                        token_txh_logs[token] = txnHash
                        break
    print(f"total nums is {len(token_txh_logs)}")
    file_name = f"{chain}.json"
    with open(file_name,"w") as f:
        json.dump(token_txh_logs,f)



def parse_args():
    parser = argparse.ArgumentParser(description='get crossChain events for eth, bsc, polygon')
    # parser.add_argument('--project', default = 'poly', help='the crosschain project')
    parser.add_argument('--chain', default = 'Polygon', help='get the chain data')  #'ETH' #'Polygon'   #['ETH', 'BSC', 'Polygon']  记得更换链
    parser.add_argument('--project', default = 'poly', help='the crosschain project')

    args = parser.parse_args()
    return args

def join_dict():
    a = eth_token_rtoken = {  #31
        'pMetis': 'Metis', 'WFTM': 'FTM', 'wROSE': 'ROSE', 'LP-BOBA': 'BOBA', 'wHAPI': 'HAPI', 'pRACA': 'RACA', "WSYS" : "SYS", "wsSQUID" : "SQUID",
        'sAVAX': 'AVAX', 'wOMI': 'OMI', 'YFII': 'YFI', 'wCELO': 'CELO', 'pCELL': 'CELL', 'sRLY': 'RLY', 'bATOM': 'BATOM', "BTCB" : "BTC",
        "AAVE.e" : "AAVE", "WETH" : "ETH", "WBTC" : "BTC", 'WAVAX': 'AVAX', 'pWING': 'WING', 'ppWING': 'WING', 'BWRX': 'WRX',
        'USTC': 'UST', 'WROSE': 'ROSE', 'TOMOE': 'TOMO', 'pNEO': 'NEO', 'yvSNX': 'SNX', 'WSCRT': 'SCRT', 'WKLAY': 'KLAY', 'jEUR': 'EUR'}
    
    b = ["SPELL,sSPELL","IDIA,anyIDIA","BMI,stkBMIV2","ICE,nICE","WSPP,mWSPP","BNB,WBNB","DOT,mDOT","MATIC,WMATIC,pMATIC,anyMATIC",
    "BTC,BBTC,pBTC,mBTC,pMBTC,renBTC,indexBTC","RYOSHI,anyRYOSHI","bioShib,CbioShib,IoShib","SOL,mSOL,stSOL","AVAX,wAVAX",
    "Metis,LP-Metis,LP-METIS","ELONINDEX,1ELONINDEX,11ELONINDEX","UST,1UST","ELON,11ELON,1111ELON","Cake,CAKE,GCAKE","LUNA,Luna,renLUNA,terra-luna"]
    print(len(a))
    for sub in b:
        keys = sub.split(",")
        v = keys[0]
        for index in range(1, len(keys)):
            key = keys[index]
            if key not in a:
                a[key] = v
    print(a, len(a))
    # {'pMetis': 'Metis', 'WFTM': 'FTM', 'wROSE': 'ROSE', 'LP-BOBA': 'BOBA', 'wHAPI': 'HAPI', 'pRACA': 'RACA', 'WSYS': 'SYS', 
    # 'wsSQUID': 'SQUID', 'sAVAX': 'AVAX', 'wOMI': 'OMI', 'YFII': 'YFI', 'wCELO': 'CELO', 'pCELL': 'CELL', 'sRLY': 'RLY', 'bATOM': 'BATOM', 
    # 'BTCB': 'BTC', 'AAVE.e': 'AAVE', 'WETH': 'ETH', 'WBTC': 'BTC', 'WAVAX': 'AVAX', 'pWING': 'WING', 'ppWING': 'WING', 'BWRX': 'WRX', 
    # 'USTC': 'UST', 'WROSE': 'ROSE', 'TOMOE': 'TOMO', 'pNEO': 'NEO', 'yvSNX': 'SNX', 'WSCRT': 'SCRT', 'WKLAY': 'KLAY', 'jEUR': 'EUR', 
    # 'sSPELL': 'SPELL', 'anyIDIA': 'IDIA', 'stkBMIV2': 'BMI', 'nICE': 'ICE', 'mWSPP': 'WSPP', 'WBNB': 'BNB', 'mDOT': 'DOT', 'WMATIC': 'MATIC',
    #  'pMATIC': 'MATIC', 'anyMATIC': 'MATIC', 'BBTC': 'BTC', 'pBTC': 'BTC', 'mBTC': 'BTC', 'pMBTC': 'BTC', 'renBTC': 'BTC', 'indexBTC': 'BTC', 
    #  'anyRYOSHI': 'RYOSHI', 'CbioShib': 'bioShib', 'IoShib': 'bioShib', 'mSOL': 'SOL', 'stSOL': 'SOL', 'wAVAX': 'AVAX', 'LP-Metis': 'Metis',
    #   'LP-METIS': 'Metis', '1ELONINDEX': 'ELONINDEX', '11ELONINDEX': 'ELONINDEX', '1UST': 'UST', 
    # '11ELON': 'ELON', '1111ELON': 'ELON', 'CAKE': 'Cake', 'GCAKE': 'Cake', 'Luna': 'LUNA', 'renLUNA': 'LUNA', 'terra-luna': 'LUNA'}

def get_token_decimals():
    real_token_path = f"./erc20Tokens/fill_erc20Token/real_{chain}_token_block.csv"
    real_tokens = readDefaultCsv(real_token_path)
    token_realToken = { getStandAddr(record_token["token"]) : record_token for record_token in real_tokens}

    token_list = []
    symbol_token = []  # symble : [token,decimals,symbol]
    
    for token in token_realToken:
        rsymbol = token_realToken[token]["rsymbol"]
        rtoken = token_realToken[token]["rtoken"]
        rdecimals = token_realToken[token]["rdecimals"]
        symbol = token_realToken[token]["symbol"]
        token = token_realToken[token]["token"]
        decimals = token_realToken[token]["decimals"]

        # if decimals == "0":
        #     print(token_realToken[token])
        if rtoken != "0":
            if rtoken not in token_list:
                token_list.append(rtoken)
                symbol_token.append([rtoken, rdecimals, rsymbol])
        
        if token != "0":
            if token not in token_list:
                token_list.append(token)
                if rsymbol != "0":
                    symbol = rsymbol
                symbol_token.append([token, decimals, symbol])

    labels = ["token","decimals","symbol"]
    file_name = f"./erc20Tokens/token_freq/{chain}_token_decimals.csv"
    write_csv_labels(file_name, symbol_token, labels)


if __name__ == "__main__":

    args = parse_args()
    #########       参数修改
    datasName = 'crossChainProject'
    chain = args.chain
    project = args.project

    w3 = Web3(Web3.HTTPProvider(baseData['use_network'][chain])) 
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.isConnected()

    crossChainProject = baseData[datasName][project][chain]

    # get_contract_csv()
    # get_logs_to_json()
    # get_token_nums()
    # get_tokens_freq()
    # parse_token()
    # get_some_tokens()
    # get_block_time_filled()
    # check_cex_price()
    # join_dict()
    # parse_symbol_token()
    # clean_for_dex()
    # get_token_timestamp()
    # filter_blockno()
    get_token_decimals()









    #  start ...............
    # main()

    # python dataFill.py --chain Polygon --project portal --startBlock 22697553 #eth   填充数据 blocknumber -> utc时间
    # python dataFill.py --chain ETH --project portal
    # python dataFill.py --chain BSC --project portal  

    # python getTokenChain.py --chain BSC


    # python getTokenChain.py --chain ETH --project multichain

    # multichain in ETH : ['1', '56', '42161', '250', '137', '66', '43114', '4689', '1285', '336', '40', '100', '1666600000',
    #  '288', '25', '128', '42220', '1088', '1313161554', '0', '1284', '122', '42262', '21', '10', '321', '2001', '1030', 
    #  '199', '1024', '592', '70', '2222', '108', '88', '256256', '57', '24', '8217', '9001', '30', '10000', '24734', '42170',
    #   '1234', '2000', '86', '1294', '71402', '1000005788240']

    # portal in ETH : ['1', 'BSC', '3', 'Polygon', '6', '7', '0', '10', '9', 'ETH ', '11', '14', '12', '18', '13', '8', '15']
    # poly in ETH : ['7', '6', '3', '12', '4', '17', '8', '19', '21', '25', '22', '14', '20', '23', '31', '35', '24', '36']

    # multichain in BSC : ['56', '1', '250', '137', '66', '43114', '42161', '4689', '1285', '128', '42220', '288', '25', '40', 
    # '1666600000', '915075275427796312961621483344205150649341908991', '100', '807084874370421761305021364215756945555379632289',
    #  '1313161554', '1088', '122', '1284', '57', '256', '42262', '10', '321', '1030', '2001', '1024', '199', '86', '256256',
    #   '70', '88', '2222', '61', '24', '128849018880000000000000137', '108', '96', '58', '1818', '24734', '30', '42170', '1234',
    #    '2000', '2025', '10000', '144', '1000005788240']

    # portal in BSC : ['ETH ', '1', '3', 'Polygon', '6', '7', 'BSC', '10', '137', '9', '11', '14', '18', '12', '13', '15']
    # poly in BSC : ['2', '7', '17', '12', '3', '19', '4', '21', '24', '23', '14', '26', '28', '30', '27', '32', '22', '20', '35', '36', '37', '38']

    # multichain in Polygon : ['137', '250', '56', '1', '66', '43114', '97', '97000000000000000000', '42161', '42220', '288', 
    # '25', '1666600000', '40', '1285', '100', '128', '1313161554', '1088', '122', '1284', '0', '4689', '336', '321', '592',
    #  '10', '57', '199', '2001', '1024', '1030', '144', '2000', '4181']

    # portal in Polygon : ['BSC', '3', '1', 'ETH ', 'Polygon', '6', '7', '10', '43114', '9', '11', '137', '14', '18', '13']
    # poly in Polygon : ['7', '6', '2', '3', '12', '19', '20', '21', '23', '22', '14', '27', '32', '35', '36', '37', '24', '30']

    