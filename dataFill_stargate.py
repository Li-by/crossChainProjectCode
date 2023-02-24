# import sys
# sys.path.append("./")
# -*- coding: utf-8 -*- 


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

# https://learnblockchain.cn/article/4309  #行不通，不清楚怎么用
# https://ethereum.stackexchange.com/questions/11144/how-to-decode-input-data-from-a-transaction #解码 input 

global func_txhs
global funcs_hashs_list  #获取的函数输入记录

func_txhs = {}

chainId_symbol = {
    1 : "ETH ",
    2 : "BSC",
    9 : "Polygon",
}


poolId = {   # symbols  decimals
            'ETH': {1: ['USDC',6], 2: ['USDT',6], 5: ['BUSD', 6], 3: ['DAI', 18], 7: ['FRAX', 18], 11: ['USDD', 18], 13: ['ETH', 18], 
                    14: ['sUSD', 18], 15: ['LUSD', 18] , 16: ['MAI', 6] }, 

            'BSC': {1: ['USDC',18], 2: ['USDT',  18], 5: ['BUSD', 18], 11: ['USDD', 18], 16:['MAI', 6]}, 

            'Polygon': {1: ['USDC',6], 2: ['USDT',6], 3: ['DAI', 18], 5: ['BUSD', 6], 16: ['MAI', 6]},
        }



# a1 = {}
# for key in poolId:
#     a2 = {}
#     for k2 in poolId[key]:
#         a2[poolId[key][k2]] = k2.upper()
#     a1[key] = a2
# print(a1)  



def get_funcs_signature_hashs(funcs):
    # if events[event]
    funcs_signature_hashs = {func : Web3.keccak(text = funcs[func]).hex() for func in funcs}
    print("the funcs total topics and funcs_signature_hash is : ", funcs_signature_hashs)
    return funcs_signature_hashs


def write_csv(save_dir, results):
    labels = ('contractAddress', 'txhash', 'blockno', 'timestamp', 'srcUser', 'srcID', 'srcToken', 'srcAmount', 'dstUser', 'dstID', 'dstToken', 'dstAmount') # 11个字段
    act = open(save_dir, mode='w',newline='')
    writer = csv.writer(act)
    writer.writerow(labels)
    for i in results:
        writer.writerow(i)
    act.close()

def readCsv(event_saved_file):
    with open(event_saved_file, 'r') as file:
        reader = csv.DictReader(file)
        try:
            txhash_list = [row for row in reader if len(row['txhash']) > 60 ]  #过滤掉无用的标题
        except:
            txhash_list = []
            pass
    return txhash_list

def write_json(file_name, content):
    with open(file_name,"w") as f:
        json.dump(content,f)

def loadLogs(filedir):
    with open(filedir,'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict



def get_fill_txhs(txhs):
    # 'contractAddress': '0xe672486151ee8d7508df79d98153b1d65dc4b1bd', 'txhash': '0xc74b34cf9c6a71ed95ff25d60258032ba6d5ee569f6c83c29b7b996402f4161f', 'blockno': '14405186', 'timestamp': '0', 
    # 'srcUser': '0', 'srcID': 'ETH', 'srcToken': '1', 'srcAmount': '0', 
    # 'dstUser': '0', 'dstID': '6', 'dstToken': '1', 'dstAmount': '9994000'}
    # [0, 10, 74, 138, 202, 266, 330]
    flag = False  #状态
    txhash = txhs['txhash']
    receipt = func_txhs[txhash]
    txhs['contractAddress'] = Web3.toChecksumAddress(receipt['to'])
    methods = receipt["input"][0:10]

    if methods == "0x9fbf10fc" or methods == "0x84d0dba3": 
        # methods == "0x9fbf10fc"  # only polygon: # swap()  bsc, polygon, eth
        # methods == "0x84d0dba3": # only polygon  redeemRemote(uint16 _dstChainId,uint256 _srcPoolId,uint256 _dstPoolId,address _refundAddress,uint256 _amountLP,uint256 _minAmountLD,bytes _to,tuple _lzTxParams)

        # pass
        # MethodID: 0x9fbf10fc 10
        # [0]:  0000000000000000000000000000000000000000000000000000000000000002 74  dstChainId
        # [1]:  0000000000000000000000000000000000000000000000000000000000000001 138  srcPoolId 
        # [2]:  0000000000000000000000000000000000000000000000000000000000000005 202 dstPoolId
        # [3]:  000000000000000000000000d27a40cdc1781509e34a28e3a4115384785d910a 266  refundAddress
        # [4]:  0000000000000000000000000000000000000000000000000000000005f5e100 330 amountLD

        txhs['srcUser'] = Web3.toChecksumAddress(receipt["from"])
        
        srcTokenId = int(receipt["input"][74: 138], 16) 
        id_tokenSymbol = poolId[txhs['srcID']]
        # print("srcTokenId", srcTokenId)
        if srcTokenId in id_tokenSymbol:
            txhs['srcToken'] = id_tokenSymbol[srcTokenId][0] #token
            decimals = id_tokenSymbol[srcTokenId][1] #decimals
            txhs['srcAmount'] = format(int(receipt["input"][266:330], 16)/ 10 ** decimals, ".6f") #保留6位有效数字

        else:
            assert 1 == 0, "1.1"
        
        ## dest
        txhs['dstUser'] = txhs['srcUser']
        chainId  = int(receipt["input"][10:74], 16)
        if chainId in chainId_symbol:
            txhs['dstID'] = chainId_symbol[chainId]  
        else:
            txhs['dstID'] = str(chainId)

        try:
            chain = txhs['srcID']
            dstTokenId = int(receipt["input"][138:202], 16)
            # print(chain)
            if dstTokenId in poolId[chain]:
                txhs['dstToken'] = poolId[chain][dstTokenId][0] #token
                decimals = poolId[chain][dstTokenId][1] #decimals
                dstAmount = int(receipt["input"][330: 394], 16)
                # print(dstAmount)
                dstAmount = format(dstAmount / 10 ** decimals, ".6f")  #保留6位有效数字
                txhs['dstAmount'] = dstAmount
            else:
                assert 1 == 0, "1.2"

        except Exception as e:
            print("error", e)
           
        flag = True
        
    elif  methods == "0x1114cd2a": #  only eth
        # pass
        # swapETH(uint16 _dstChainId, address _refundAddress, bytes _toAddress, uint256 _amountLD, uint256 _minAmountLD)
        # MethodID: 0x1114cd2a
        # [0]:  000000000000000000000000000000000000000000000000000000000000000b 74
        # [1]:  0000000000000000000000006821ec1fcd40ad5268d3b5607e49441d4e7eb4e7 138 
        # [2]:  00000000000000000000000000000000000000000000000000000000000000a0 202
        # [3]:  00000000000000000000000000000000000000000000000002c68af0bb140000 266
        # [4]:  00000000000000000000000000000000000000000000000002c2fd72164d8000 330 
        # [5]:  0000000000000000000000000000000000000000000000000000000000000014 394
        # [6]:  6821ec1fcd40ad5268d3b5607e49441d4e7eb4e7000000000000000000000000
        txhs['srcUser'] = Web3.toChecksumAddress(receipt["from"])
        txhs['dstUser'] = txhs['srcUser']
        txhs['srcToken'] = txhs['srcID'] 
        txhs['dstToken'] = txhs['srcToken']
        # txhs['dstID'] = 
        chainId  = int(receipt["input"][10:74], 16)
        if chainId in chainId_symbol:
            txhs['dstID'] = chainId_symbol[chainId]  
        else:
            txhs['dstID'] = str(chainId)
        
        if txhs['srcID'] == "ETH":
            id_tokenSymbol_infos = poolId["ETH"][13]  # 13: ['ETH', 18]
            decimals = id_tokenSymbol_infos[1] #decimals
            txhs['srcAmount'] = format(int(receipt["input"][202:266], 16)/ 10 ** decimals, ".6f") #保留6位有效数字
            txhs['dstAmount'] = format(int(receipt["input"][266:330], 16)/ 10 ** decimals, ".6f") #保留6位有效数字
           
        else:
            assert 1 == 0, "2.1"
        
        # print("txhs", txhs)
        # assert 1 == 0, "2.2"
        flag = True

    elif  methods == "0x4c904106": # bsc 和 polygon  #该函数可以跨币转账 ->  woo -> eth, 该函数先在本地进行了一次swap，然后使用固定的token进行跨链。
        # woo -> usd -> 跨链 -> usd -> eth  类似这样的记录
        # crossSwap(uint256 refId_, address fromToken, address toToken, uint256 fromAmount, uint256 srcMinQuoteAmount, uint256 dstMinToAmount, uint16 srcChainId, uint16 dstChainId, address to)
        # [0]:  00000000000000000000000000000000000000000000000002d4a7239abef1f2
        # [1]:  0000000000000000000000004691937a7508860f876c9c0a2a617e7d9e945d4b  #srcToken
        # [2]:  000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee  # desToken， eee代表eth
        # [3]:  0000000000000000000000000000000000000000000000000de0b6b3a7640000  # 发送数量  1000000000000000000    
        # [4]:  00000000000000000000000000000000000000000000000002565141e52d01c3
        # [5]:  00000000000000000000000000000000000000000000000006080b7e09d51ffc # 最小得到的数量  0.43461
        # [6]:  0000000000000000000000000000000000000000000000000000000000000002 # srcChainId
        # [7]:  000000000000000000000000000000000000000000000000000000000000000c # dstChainId  
        # [8]:  000000000000000000000000ea02dcc6fe3ec1f2a433ff8718677556a3bb3618 # 接收地址

        # '0x00a60eb8a82a20866fe369b67f4ab7ff540c806379310c38afc78c235d256e02', 'blockno': '18446387', 'timestamp': '0', 
        # 'srcUser': '0', 'srcID': 'BSC', 'srcToken': '1', 'srcAmount': '0', 
        # 'dstUser': '0', 'dstID': '12', 'dstToken': '1', 'dstAmount': '168254'}
        # pass
        txhs['srcUser'] = Web3.toChecksumAddress(receipt["from"])
        txhs['dstUser'] = txhs['srcUser']
        
        dstChain = int(txhs['dstID'])
        if dstChain in chainId_symbol:
            txhs['dstID'] = chainId_symbol[dstChain]  
  
        dstTokenId = int(txhs['dstToken'])
        id_tokenSymbol_infos = poolId[txhs['srcID']][dstTokenId]
        txhs['dstToken'] = id_tokenSymbol_infos[0]
        txhs['srcToken'] = txhs['dstToken']
        decimals = id_tokenSymbol_infos[1] #decimals
        txhs['dstAmount'] = format(int(txhs['dstAmount'])/ 10 ** decimals, ".6f") #保留6位有效数字
        txhs['srcAmount'] = txhs['dstAmount']




        # if txhs['dstID'] in poolId:  # ETH  
             
        #     if dstTokenId in poolId[txhs['dstID']]:
        #         id_tokenSymbol_infos = poolId[txhs['dstID']][dstTokenId]  # 13: ['ETH', 18]
        #         txhs['dstToken'] = id_tokenSymbol_infos[0]
        #         txhs['srcToken'] = txhs['dstToken']
        #         decimals = id_tokenSymbol_infos[1] #decimals
        #         txhs['dstAmount'] = format(int(txhs['dstAmount'])/ 10 ** decimals, ".6f") #保留6位有效数字
        #         txhs['srcAmount'] = txhs['dstAmount']
        #         # assert 1 == 0, "3.2"
        #     else:
        #         pass
                # assert 1 == 0, "3.2"

        # print("txhs", txhs)
        flag = True


    else:
        pass
    
    outs = [txhs[key] for key in txhs]
    return (flag,tuple(outs))


def main():
    global funcs_hashs_list

    # project_funcs = crossChainProject["funcs"]
    # assert len(project_funcs) > 0, "there is not funcs need scan !"
    # funcs_signature_hashs = get_funcs_signature_hashs(project_funcs)
    # funcs_hashs_list = [funcs_signature_hashs[methods][:10] for methods in funcs_signature_hashs]
    # print(funcs_hashs_list)
    
    save_dir = os.path.join(datasName, project, chain)
    file_csv_path = glob.glob(save_dir + "/*.csv")
    assert len(file_csv_path) > 0, "notice !"
    
    file_json_path = glob.glob(save_dir + "/*.json")
    assert len(file_json_path) > 0, "no json !"
    for js in file_json_path:
        temp_json = loadLogs(js)
        for item in temp_json:
            func_txhs[item] = json.loads(temp_json[item])
    print(f"the total func txhs is {len(func_txhs)} ")

    
    fill_txhs = []
    for fi in file_csv_path:
        sub_blocks = readCsv(fi)
        # print(len(sub_blocks))
        for txhs in tqdm(sub_blocks):
            # if txhs['txhash'] == "0x3709ddfefaea3ae5d1f0319b976e07bb4adfbcf3b638b4c71d6d3e744154bc7d":
            flag,out = get_fill_txhs(txhs)
                # print(flag,out)
        #     break
        # break
            if flag and out not in fill_txhs:
                fill_txhs.append(out)
            #     print(out)
            #     break
           

    ### write it !
    file_name = fi.replace(".csv", f"_filled.csv")
    # print(file_name)
    write_csv(file_name, fill_txhs)

    # step1 get token
    """
    tokens = {}
    for fi in file_csv_path:
        sub_blocks = readCsv(fi)
        # print(len(sub_blocks))
        for txhs in tqdm(sub_blocks):
            dstToken = txhs['dstToken']
            if dstToken not in tokens:
                tokens[dstToken] = 1
            else:
                tokens[dstToken] += 1

            srcToken = txhs['dstToken']
            if srcToken not in tokens:
                tokens[srcToken] = 1
            else:
                tokens[srcToken] += 1
    print(tokens) 
    """
    # {'2': 18166, '1': 26254, '11': 2, 'USDT': 17958, 'USDC': 24470, 'USDD': 2}  bsc
    # {'1': 8982, '2': 3422, '5': 1178, '13': 2344, '11': 2, 'USDC': 8284, 'USDT': 3064, 'BUSD': 1058, 'ETH': 2338, 'USDD': 2} eth 
    # {'2': 8066, '1': 27234, '5': 3450, 'USDT': 7786, 'USDC': 25916, 'BUSD': 3266}
    # ['USDT',  'USDC', 'USDD',  'BUSD', 'ETH']
    

    # step 2 get detId
    # dst_id = {}
    # for fi in file_csv_path:
    #     sub_blocks = readCsv(fi)
    #     # print(len(sub_blocks))
    #     for txhs in tqdm(sub_blocks):
    #         dstId = get_fill_txhs(txhs)
    #         if dstId not in dst_id:
    #             dst_id[dstId] = 1
    #         else:
    #             dst_id[dstId] += 1
    # print(dst_id)

    # step1 get methods hash 
    # methods_hash = {}
    # methods_dict = {}
    # for fi in file_csv_path:
    #     sub_blocks = readCsv(fi)
    #     # print(len(sub_blocks))
    #     for txhs in sub_blocks:
    #         out,has = get_fill_txhs(txhs)
    #         if out not in methods_hash:
    #             # methods_hash[out] = has
    #             methods_hash[out] = 1
    #             methods_dict[out] = has
    #         else:
    #             methods_hash[out] += 1

    # # methods_hash = sorted(methods_hash.items(), key=lambda x:x[1], reverse=False)
    # print(methods_hash, methods_dict)
    # # for key in ["0x2d62fc1a", "0x656f3d64"]:  # ["0x9fbf10fc", "0x656f3d64", "0x84d0dba3", "0x4c904106"]:
    #     print(methods_dict[key])

def parse_args():
    parser = argparse.ArgumentParser(description='get crossChain events for eth, bsc, polygon')
    # parser.add_argument('--project', default = 'poly', help='the crosschain project')
    parser.add_argument('--chain', default = 'Polygon', help='get the chain data')  #'ETH' #'Polygon'   #['ETH', 'BSC', 'Polygon']  记得更换链
    parser.add_argument('--project', default = 'poly', help='the crosschain project')

    args = parser.parse_args()
    return args


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

    #  start ...............
    main()


    # python dataFill.py --chain Polygon --project portal --startBlock 22697553 #eth   填充数据 blocknumber -> utc时间
    # python dataFill.py --chain ETH --project portal
    # python dataFill.py --chain BSC --project portal  

    # python dataFill_stargate.py --chain ETH --project stargate





