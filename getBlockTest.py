# import sys
# sys.path.append("./")

from baseDatas import baseData
from web3 import Web3
from web3.middleware import geth_poa_middleware
import csv
import json
import asyncio
import requests
import time
import os
import glob
import argparse



def _anySwapIn(result):
    # LogAnySwapIn(bytes32 indexed txhash, address indexed token, address indexed to, uint amount, uint fromChainID, uint toChainID) #txhash暂时用不上
    contractAddress = result['address']
    txhash = result['transactionHash'].hex()
    blockno = result["blockNumber"]  #str(int(result["blockNumber"],16))
    timestamp = 0  #str(int(result["timeStamp"], 16))
    srcUser = '0x' + result['topics'][3].hex()[-40:]

    srcID = str(int(result['data'][66:130], 16))
    # srcToken = '0x' + result['topics'][1][-40:]
    srcToken = '0x' + result['topics'][2].hex()[-40:]
    srcAmount = str(int(result['data'][2:66], 16))
    dstUser = '0x' + result['topics'][3].hex()[-40:]
    dstID = str(int(result['data'][-64:], 16))
    dstToken = srcToken
    dstAmount = srcAmount

    return (contractAddress, txhash, blockno, timestamp, srcUser, srcID, srcToken, srcAmount, dstUser, dstID, dstToken, dstAmount)
    
def _anySwapOut1(result):
    # LogAnySwapOut(address indexed token, address indexed from, address indexed to, uint amount, uint fromChainID, uint toChainID)
    contractAddress = result['address']
    txhash = result['transactionHash'].hex()
    blockno = result["blockNumber"] #str(int(result["blockNumber"],16))
    timestamp = 0 # str(int(result["timeStamp"], 16))
    srcUser = '0x' + result['topics'][2].hex()[-40:]
    srcID = str(int(result['data'][66:130], 16))
    srcToken = '0x' + result['topics'][1].hex()[-40:]
    srcAmount = str(int(result['data'][2:66], 16))
    dstUser = '0x' + result['topics'][3].hex()[-40:]
    dstID = str(int(result['data'][-64:], 16))
    dstToken = srcToken
    dstAmount = srcAmount

    return (contractAddress, txhash, blockno, timestamp, srcUser, srcID, srcToken, srcAmount, dstUser, dstID, dstToken, dstAmount)

def _anySwapOut2(result):
    assert 1 == 0, "anySwapOut2 ! "
    # contractAddress = result['address']
    # txhash = result['transactionHash'].hex()
    # blockno = result["blockNumber"]  #str(int(result["blockNumber"],16))
    # timestamp = 0  #str(int(result["timeStamp"], 16))
    # srcUser = '0x' + result['topics'][2].hex()[-40:]

    # srcID = str(int(result['data'][66:130], 16))
    # srcToken = '0x' + result['topics'][1].hex()[-40:]
    # srcAmount = str(int(result['data'][2:66], 16))
    # dstUser = srcUser
    # dstID = str(int(result['data'][-64:], 16))
    # dstToken = srcToken
    # dstAmount = srcAmount

    # return (contractAddress, txhash, blockno, timestamp, srcUser, srcID, srcToken, srcAmount, dstUser, dstID, dstToken, dstAmount)

def _tokensForTokens(result):
    contractAddress = result['address']
    txhash = result['transactionHash'].hex()
    blockno = result["blockNumber"]  #str(int(result["blockNumber"],16))
    timestamp = 0  #str(int(result["timeStamp"], 16))
    srcUser = '0x' + result['topics'][2].hex()[-40:]

    srcID = str(int(result['data'][66:130], 16))
    srcToken = '0x' + result['topics'][1].hex()[-40:]
    srcAmount = str(int(result['data'][2:66], 16))
    dstUser = srcUser
    dstID = str(int(result['data'][-64:], 16))
    dstToken = srcToken
    dstAmount = srcAmount

    return (contractAddress, txhash, blockno, timestamp, srcUser, srcID, srcToken, srcAmount, dstUser, dstID, dstToken, dstAmount)

def _tokensForNative(result):
    print("tokensForNative", txhash = result['transactionHash'])


def _tokensForTokens(result):
    contractAddress = result['address']
    txhash = result['transactionHash'].hex()
    blockno = result["blockNumber"]  #str(int(result["blockNumber"],16))
    timestamp = 0  #str(int(result["timeStamp"], 16))
    srcUser = '0x' + result['topics'][1].hex()[-40:]
    dstUser = '0x' + result['topics'][2].hex()[-40:]
    srcID = str(int(result['data'][194:258], 16))
    dstID = str(int(result['data'][258:322], 16))
    srcToken = '0x' + result['data'][386:450]
    dstToken = '0x' + result['data'][450:514]
    srcAmount = str(int(result['data'][66:130], 16))
    dstAmount = srcAmount

    return (contractAddress, txhash, blockno, timestamp, srcUser, srcID, srcToken, srcAmount, dstUser, dstID, dstToken, dstAmount)

def _polyWrapperLock(result):
    contractAddress = result['address']
    txhash = result['transactionHash'].hex()
    blockno = result["blockNumber"]  #str(int(result["blockNumber"],16))
    timestamp = 0  #str(int(result["timeStamp"], 16))

    srcUser = '0x' + result['topics'][2].hex()[-40:]
    srcID = chain  #源链
    srcToken = '0x' + result['topics'][1].hex()[-40:]
    srcAmount = str(int(result['data'][130:194], 16))
    dstUser = '0x' + result['data'][-64:-24].strip('0')  #存疑
    dstID = str(int(result['data'][2:66], 16))   #str(int(result['data'][-64:], 16))
    dstToken = srcToken
    dstAmount = srcAmount

    return (contractAddress, txhash, blockno, timestamp, srcUser, srcID, srcToken, srcAmount, dstUser, dstID, dstToken, dstAmount)

def _swap(result): # contractAddress, txhash, blockno, srcAmount, 
    contractAddress = '0x' + result['data'][154:194]
    txhash = result['transactionHash'].hex()
    blockno = result["blockNumber"]  #str(int(result["blockNumber"],16))
    timestamp = 0  #str(int(result["timeStamp"], 16))

    srcUser = 0
    srcID = chain  #源链
    srcToken = str(int(result['data'][90:130], 16)) #后期需要更正
    srcAmount = 0
    dstUser = 0
    dstID = str(int(result['data'][2:66], 16)) 
    dstToken = srcToken
    dstAmount = str(int(result['data'][194:258], 16))

    return (contractAddress, txhash, blockno, timestamp, srcUser, srcID, srcToken, srcAmount, dstUser, dstID, dstToken, dstAmount)

def _portal(result): # contractAddress, txhash, blockno, srcAmount, 
    contractAddress = '0x' + result['topics'][1].hex()[-40:]
    txhash = result['transactionHash'].hex()
    blockno = result["blockNumber"]  #str(int(result["blockNumber"],16))
    timestamp = 0  #str(int(result["timeStamp"], 16))

    srcUser = 0
    srcID = chain  #源链
    srcToken = 0
    srcAmount = 0
    dstUser = 0
    dstID = 0 
    dstToken = 0
    dstAmount = 0

    return (contractAddress, txhash, blockno, timestamp, srcUser, srcID, srcToken, srcAmount, dstUser, dstID, dstToken, dstAmount)


def loadLogs(filedir):
    with open(filedir,'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict

def writeCsv(event, outs, end_Block):
    print(f"start write the event {event} !")
    event_save_path = glob.glob(os.path.join(save_dir, event + "*.csv"))
    assert len(event_save_path) < 2, "the event's recode of {} is wrong !".format(event)   #条件false触发异常
    labels = ('contractAddress', 'txhash', 'blockno', 'timestamp', 'srcUser', 'srcID', 'srcToken', 'srcAmount', 'dstUser', 'dstID', 'dstToken', 'dstAmount') # 11个字段
    event_save_file = os.path.join(save_dir, event + "_" + str(end_Block) + ".csv")
    if len(event_save_path) == 0:  #需要新创建
        act = open(event_save_file, mode='w',newline='')
        writer = csv.writer(act)
        writer.writerow(labels)

        for out in outs:
            writer.writerow(out)
        act.close()

    else: # ==1
        event_saved_file = event_save_path[0]
        with open(event_saved_file, 'r') as file:
            reader = csv.DictReader(file)
            try:
                txhash_list = [row['txhash'] for row in reader]
            except:
                txhash_list = []
                pass

        act = open(event_saved_file, mode='a',newline='')
        writer = csv.writer(act)
        writer.writerow(labels)

        for out in outs:
            if out[0] not in txhash_list:  #'txhash' 在之前列表中没有出现过
                writer.writerow(out)
        act.close()
        os.rename(event_saved_file, event_save_file)  # such as anySwapOut1_20125.csv -> anySwapOut1_30125.csv
    print(f"##### ##### ##### write logs of event {event}_{end_Block} csv success ! ")

    # >>> def square(x) :         # 计算平方数
    # ...     return x ** 2
    # ...
    # >>> map(square, [1,2,3,4,5])    # 计算列表各个元素的平方
    # <map object at 0x100d3d550>     # 返回迭代器
    # >>> list(map(square, [1,2,3,4,5]))   # 使用 list() 转换为列表
    # [1, 4, 9, 16, 25]

def getEventsFromAddressAndTopics(topic, fromBlock, endBlock):
    flag = 1
    logs = None
    
    try:
        # event_filter_params = {'topics': [topic], 'address': contractAddress, 'fromBlock': fromBlock, 'toBlock': endBlock}  #, 15384470
        event_filter_params = {'topics': [topic], 'fromBlock': fromBlock, 'toBlock': endBlock}  #不指定合约名字
        logs = w3.eth.get_logs(event_filter_params)  #一次只能过滤一个事件，返回的目标list长度不能大于10000，自动按照升序排列的。
        # print(logs[0])

    except Exception as e:
        flag = 0
        print(e)
        # try:
        #     if e.args[0]["code"] == -32005:  # ValueError: {'code': -32005, 'message': 'query returned more than 10000 results'}
        #         flag = 0
        # except:
        #     raise e  #抛出错误Rai
    return flag, logs  # 1:success , 0:more than 10000 results, reduce the query

def get_events_signature_hashs(events):
    # if events[event]
    events_signature_hashs = {event : Web3.keccak(text = events[event]).hex() for event in events}
    print("the events total topics and events_signature_hash is : ", events_signature_hashs)
    return events_signature_hashs

def get_start_and_end_block(event, fromBlock, endBlock):  #单个事件，单个记录
    event_save_path = glob.glob(os.path.join(save_dir, event + "_*.csv"))
    assert len(event_save_path) < 2, "the event's recode of {} is wrong !".format(event)   #条件false触发异常
    if len(event_save_path) == 0:  #新建
        fromBlock = max(int(crossChainProject['startBlock']), fromBlock)
        
    else: #更新存诸
        recode_start = int(event_save_path[0].split('_')[-1].strip(".csv")) # such as : "anySwapOut1 in anySwapOut1_20125.csv" 
        fromBlock = max(recode_start, fromBlock)
    
    if not endBlock: #无指定，最新块
        # now_block = w3.eth.block_number
        endBlock = event_end_block[chain]

    assert fromBlock < endBlock, f"the event's block of {event} is wrong ! or may be the latest state ! "   #条件false触发异常

    print(f"Scanning event {event} in {chain} from blocks {fromBlock} -> {endBlock}")
    return (fromBlock, endBlock)

def parse_write_event(event, results, end_Block):
    print(f"start parse the event {event} !")
    outs = []
    if event == 'anySwapIn':
        for result in results:
            out = _anySwapIn(result)
            if out not in outs:
                outs.append(out)

    elif event == 'anySwapOut1':
        for result in results:
            out = _anySwapOut1(result)
            if out not in outs:
                outs.append(out)

    elif event == 'anySwapOut2':
        for result in results:
            out = _anySwapOut2(result)
            if out not in outs:
                outs.append(out)

    elif event == 'tokensForTokens':
        for result in results:
            out = _tokensForTokens(result)
            if out not in outs:
                outs.append(out)

    elif event == 'tokensForNative':  #该事件似乎存在记录，需要后期筛选。
        print(results)
        # _tokensForNative(result)
        raise ValueError({"function _tokensForNative"})

    elif event == 'Poly':  # poly项目只有该事件
        for result in results:
            out = _polyWrapperLock(result)
            if out not in outs:
                outs.append(out)

    elif event == "Swap":  # 'stargate' 项目只有该事件
        for result in results:
            out = _swap(result)
            if out not in outs:
                outs.append(out)

    elif event == "Portal":  # 'stargate' 项目只有该事件
        for result in results:
            out = _portal(result)
            if out not in outs:
                outs.append(out)


    else:
        print("no function")
    
    writeCsv(event, outs, end_Block)

def get_event_logs(event, events_signature_hashs, fromToEndBlock):

    start_Block = fromToEndBlock[0]
    end_Block = fromToEndBlock[1]

    event_logs = []
    while True:
        sub_end_Block = start_Block + initQueryRange
        if sub_end_Block > end_Block:
            sub_end_Block = end_Block
        
        # print(f"scanning the event of {event} from blocks {start_Block} -> {sub_end_Block}")
        # flag, logs = getEventsFromAddressAndTopics(events_signature_hashs[event], start_Block, sub_end_Block)
        while True:
            print(f"scanning the event of {event} from blocks {start_Block} -> {sub_end_Block}")
            flag, logs = getEventsFromAddressAndTopics(events_signature_hashs[event], start_Block, sub_end_Block)
            if flag:
                break
            else:
                sub_end_Block = start_Block + int((sub_end_Block - start_Block) * decayRatio)
        print(f"have scaned the event of {event} in {chain} from blocks {start_Block} -> {sub_end_Block}")
        # print(logs)
        event_logs += logs
        
        if sub_end_Block == end_Block:
            if len(event_logs):
                #结果分析存入，退出
                parse_write_event(event, event_logs, sub_end_Block)
                
            break

        if len(event_logs) > interval:
            #结果分析存入，
            parse_write_event(event, event_logs, sub_end_Block)
            event_logs = []  #置空

        start_Block = sub_end_Block

def main():
    # "test demo"
    # topic = "0xfea6abdf4fd32f20966dff7619354cd82cd43dc78a3bee479f04c74dbfc585b3"
    # event_filter_params = {'topics': [topic], 'fromBlock':125915510 , 'toBlock': 125915511}  #不指定合约名字
    # logs = w3.eth.get_logs(event_filter_params)  #一次只能过滤一个事件，返回的目标list长度不能大于10000，自动按照升序排列的。
    # print(logs)

    # [AttributeDict({'address': '0x101816545F6bd2b1076434B54383a1E633390A2E', 
    
    # 'blockNumber': 15351090, 
    # data = '0x000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000d000000000000000000000000150f94b44927f078737562f0fcf3c95c01cc23760000000000000000000000000000000000000000000000000011c0beb9f15000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000022ecb25c0000000000000000000000000000000000000000000000000000000297913cd4000000000000000000000000000000000000000000000000000000000000000000'
    # result = {"data" : data}
    # AttributeDict({'address': '0x4f3Aff3A747fCADe12598081e80c6605A8be192F', 'topics': [HexBytes('0xfea6abdf4fd32f20966dff7619354cd82cd43dc78a3bee479f04c74dbfc585b3'), HexBytes('0x000000000000000000000000ff8e30e4c1e676fd152ee5eeba09ba142e842bf1'), HexBytes('0x000000000000000000000000ff8e30e4c1e676fd152ee5eeba09ba142e842bf1')], 'data': '0x00000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002e90edd000000000000000000000000000000000000000000000000000000000000000008900000000000000000000000000000000000000000000000000000000000000380000000000000000000000000000000000000000000000000000000000000002000000000000000000000000d69b31c3225728cc57ddaf9be532a4ee1620be51000000000000000000000000c2132d05d31c914a87c6611c10748aeb04b58e8f', 'blockNumber': 25915510, 'transactionHash': HexBytes('0x7220331bba432431729024505def67b9c1965a5c9110059ead23fe5714f1bdcd'), 'transactionIndex': 7, 'blockHash': HexBytes('0x23b5e24d0273a00d559c83708d23139a10e306d3c532366a5f656f6164bd899b'), 'logIndex': 76, 'removed': False})]
  
    
    project_events = crossChainProject["events"]
    assert len(project_events) > 0, "there is not events need scan !"
    events_signature_hashs = get_events_signature_hashs(project_events)

    # event : [anySwapIn, anySwapOut1, anySwapOut2,  tokensForTokens, tokensForNative]
    for event in events_signature_hashs:
        # fromToEndBlock = get_start_and_end_block(event, fromBlock, endBlock)
        # event = "anySwapOut1"
        if event != event_goal:   #'anySwapOut2': #
            continue
         
        try:
            fromToEndBlock = get_start_and_end_block(event, fromBlock, endBlock)
            # print(222)
            get_event_logs(event, events_signature_hashs, fromToEndBlock)

        except Exception as e:
            print(e)
    

def parse_args():
    parser = argparse.ArgumentParser(description='get crossChain events for eth, bsc, polygon')
    parser.add_argument('--project', default = 'poly', help='the crosschain project')
    parser.add_argument('--chain', default = 'Polygon', help='get the chain data')  #'ETH' #'Polygon'   #['ETH', 'BSC', 'Polygon']  记得更换链
    parser.add_argument('--fromBlock', default = 0, help='scan start')  # 如果为0，优先遍历目录中的文件，若没有，则从项目的startBlock位置开始
    parser.add_argument('--endBlock', default = 0, help='scan end')  #  若不指定，默认为0。则根据配置查找
    parser.add_argument('--getRange', default = 1000, help='get the block range')
    parser.add_argument('--event', default = 'Poly', help='get the block range')
    args = parser.parse_args()

    return args



if __name__ == "__main__":
    args = parse_args()
    #########       参数修改
    datasName = 'crossChainProject'
    project = args.project
    chain = args.chain
    fromBlock = int(args.fromBlock)
    endBlock = int(args.endBlock)
    initQueryRange = int(args.getRange)   #50000 #每次查询 50000 个区块   2000, 1000
    event_goal = args.event

    # print(project)

    decayRatio = 0.8 #当查询区间过大时，筛选出来的记录超过10000条，衰减。
    interval = 200 #当超过1000条记录，则保存一次
    # print(args.chain)

    w3 = Web3(Web3.HTTPProvider(baseData['use_network'][chain])) 
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.isConnected()

    event_end_block = {
        "BSC" : 20936753, # 2022-08-31 23:59:57   
        "ETH" : 15449617, #2022-08-31 23:59:35
        'Polygon' : 32534498, # 2022-08-31 23:59:59
    }  #每个项目的结束区块

    # print("11111", w3.eth.block_number)
    #  pre start ............... 
    
    save_dir = os.path.join(datasName, project, chain) #创建初始化目录，起始块赋值0
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    crossChainProject = baseData[datasName][project][chain]

    #  start ...............  
    main()

    # event : [anySwapIn, anySwapOut1, anySwapOut2,  tokensForTokens, tokensForNative]
    # python getBlockTest.py --project multichain --chain ETH --fromBlock 0 --endBlock 20936753 --getRange 1000000

    # mutichain
    # python getBlockTest.py --project multichain --chain Polygon --getRange 1000
    # python getBlockTest.py --project multichain --chain Polygon --getRange 1000 --event anySwapOut1 
    # python getBlockTest.py --project multichain --chain Polygon --getRange 1000 --event anySwapOut2
    # python getBlockTest.py --project multichain --chain Polygon --getRange 1000 --event tokensForTokens --fromBlock 125915510  --endBlock 125915511
    # python getBlockTest.py --project multichain --chain Polygon --getRange 1000 --event tokensForNative   

    # poly
    # 0x2b0591052cc6602e870d3994f0a1b173fdac98c215cb3b0baf84eaca5a0aa81e
    # python getBlockTest.py --project 'poly' --chain Polygon --getRange 1000 --event 'Poly'
    # python getBlockTest.py --project 'poly' --chain ETH --getRange 1000 --event 'Poly'
    # python getBlockTest.py --project poly --chain ETH  --fromBlock 15591321 --endBlock 15591322


    ######   stargate 和 portal 项目 不能通过合约事件直接得到所有需要字段, 可以先筛选出事件对应的txhsah，根据txhash获取调用的函数，进行分析

    #stargate
    # python getBlockTest.py --project stargate --chain ETH  --fromBlock 15351090  --endBlock 15351091  --event Swap

    #portal
    # python getBlockTest.py --project portal --chain ETH  --event Portal  --fromBlock 15351969   --endBlock 15351970  

    