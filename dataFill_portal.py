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

global func_txhs
global funcs_hashs_list  #获取的函数输入记录

func_txhs = {}

chainId_symbol = {
    # 1 : "Solana",
    2 : "ETH ",
    4 : "BSC",
    5 : "Polygon",
}

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
    global funcs_hashs_list
    # print(txhs)
    # {'contractAddress': '0x8ea8874192c8c715e620845f833f48f39b24e222', 'txhash': '0x3d515d38124b62c107f979b8eac6ea70881e22ca88c13c7ec7780d7e41cb83d5', 'blockno': '13140651', 'timestamp': '0', 
    # 'srcUser': '0', 'srcID': 'ETH', 'srcToken': '0', 'srcAmount': '0', 
    # 'dstUser': '0', 'dstID': '0', 'dstToken': '0', 'dstAmount': '0'}
 
    flag = False  #状态
    txhash = txhs['txhash']
    receipt = func_txhs[txhash]
    methods = receipt["input"][0:10]

    if methods == "0xbee9cdfc": # wrapAndTransferETHWithPayload
        print(txhash)
        assert 1 == 0, "111111"

    elif  methods == "0xc5a5ebda": # transferTokensWithPayload
        print(txhash)
        assert 1 == 0, "22222"
    
    elif  methods == "0x9981509f": # wrapAndTransferETH
        # print(receipt)
        txhs['srcUser'] = Web3.toChecksumAddress(receipt["from"])   #chainId_symbol
        txhs['srcToken'] = "ETH"
        txhs['srcAmount'] = receipt["value"]

        chainId = int(receipt["input"][34:74], 16)
        if chainId in chainId_symbol:
            txhs['dstID'] = chainId_symbol[chainId]  
            txhs['dstUser'] = txhs['srcUser'] #标准的基于evm虚拟机地址

        else:
            txhs['dstID'] = str(chainId)
            txhs['dstUser'] = receipt["input"][74:138]

        txhs['dstToken'] = txhs['srcToken']
        txhs['dstAmount'] = txhs['srcAmount']

        # print(txhs)
        flag = True
        # assert 1 == 0, "3333333"

    elif  methods == "0x0f5287b0":  #transferTokens
        # pass
        txhs['srcUser'] = Web3.toChecksumAddress(receipt["from"])   #chainId_symbol
        txhs['srcToken'] = "0x" + receipt["input"][34:74] #
        txhs['srcAmount'] = str(int(receipt["input"][74:138], 16))

        chainId = int(receipt["input"][138:202], 16)
        # chainId = 2
        if chainId in chainId_symbol:
            txhs['dstID'] = chainId_symbol[chainId]  
            txhs['dstUser'] = txhs['srcUser'] #标准的基于evm虚拟机地址
            # print("txhs['dstID']", txhs['dstID'])

        else:
            txhs['dstID'] = str(chainId)
            txhs['dstUser'] = receipt["input"][202:266]


        txhs['dstToken'] = txhs['srcToken']
        txhs['dstAmount'] = txhs['srcAmount']
        flag = True
        # print(txhs)
        # assert 1 == 0, "44444444"

    else:
        pass
    
    outs = [txhs[key] for key in txhs]
    return (flag,tuple(outs))


def main():
    global funcs_hashs_list

    project_funcs = crossChainProject["funcs"]
    assert len(project_funcs) > 0, "there is not funcs need scan !"
    funcs_signature_hashs = get_funcs_signature_hashs(project_funcs)
    funcs_hashs_list = [funcs_signature_hashs[methods][:10] for methods in funcs_signature_hashs]
    print(funcs_hashs_list)
    
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
            flag,out  = get_fill_txhs(txhs)
            if flag and out not in fill_txhs:
                fill_txhs.append(out)
                # print(out)
                # break
    
    file_name = fi.replace(".csv", f"_filled.csv")
    print(file_name)
    write_csv(file_name, fill_txhs)

    # 0x66b1a536a70ebce821f4354a7f1ca46437da53dabca3ad8ac75adfc5ae371e7f  wrapAndTransferETH
    # 0x0ff1dd51c67a1cbde3584a6058f12e4579cde757b3e27cc1e7db3a5e85780374  transferTokens

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