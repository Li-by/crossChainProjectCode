import csv
import os
from web3 import Web3
import json
import glob
from datetime import datetime


def readCsv(event_saved_file):
    with open(event_saved_file, 'r') as file:
        reader = csv.DictReader(file)
        try:
            txhash_list = [row for row in reader if len(row['txhash']) > 60 ]  #过滤掉无用的标题
        except:
            txhash_list = []
    return txhash_list

def readDefaultCsv(event_saved_file):
    with open(event_saved_file, 'r') as file:
        reader = csv.DictReader(file)
        try:
            txhash_list = [row for row in reader]  #过滤掉无用的标题
        except:
            txhash_list = []
    return txhash_list

def readCsvRaw(event_saved_file):
    results = []
    with open(event_saved_file, 'r') as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            results.append(row)
    return results

def write_csv_labels(save_dir, results, labels):
    # labels = ('contractAddress', 'txhash', 'blockno', 'timestamp', 'srcUser', 'srcID', 'srcToken', 'srcAmount', 'dstUser', 'dstID', 'dstToken', 'dstAmount') # 11个字段
    flag = True
    if not os.path.exists(save_dir):
        flag = False

    act = open(save_dir, mode='a',newline='')
    writer = csv.writer(act)
    if not flag:
        # labels = ("token", "down_block", "up_block")
        writer.writerow(labels)
    for i in results:
        writer.writerow(i)
    act.close()

def write_csv(save_dir, results):
    act = open(save_dir, mode='a',newline='')
    writer = csv.writer(act)
    for i in results:
        writer.writerow(i)
    act.close()

def write_csv_dict(save_dir, results, labels):
    with open(save_dir, 'a', newline= '') as f:
        writer = csv.DictWriter(f, fieldnames = labels)
        writer.writeheader()
        for i in results:
            writer.writerow(i)


def write_json(file_name, content):
    with open(file_name,"w") as f:
        json.dump(content,f)

def loadLogs(filedir):
    with open(filedir,'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict

def getStandAddr(addr):
    if len(addr) > 42:
        addr = "0x" + addr[-40:]
    return Web3.toChecksumAddress(addr)

# def readCsvPrice(event_saved_file):  # timstamp, price
#     ## return 1_3 : price 
#     results = []
#     with open(event_saved_file, 'r') as f:
#         f_csv =  csv.DictReader(f)
#         for row in f_csv:
#             # print(row)
#             results.append([row["timstamp"], row["price"]])
#     dic_price = []
#     for index in range(len(results)-1):
#         dic_price.append( (f"{int(results[index][0]) - 300}_{results[index + 1][0]}", results[index][1]) )
#         # dic_price[f"{int(results[index][0]) - 300}_{results[index + 1][0]}"] = results[index][1]
#     dic_price.append( (f"{results[index+1][0]}_{int(results[index+1][0]) + 300}", results[index+1][1]) )
#     # dic_price[f"{results[index+1][0]}_{int(results[index+1][0]) + 300}"] = results[index+1][1]
#     return dic_price


# def get_timestamp_price(token_price, timestamp):
#     len_price = len(token_price)
#     assert len_price > 0, "file must have price !"
#     start_time = int(token_price[0][0].split("_")[0])
#     end_time = int(token_price[len_price-1][0].split("_")[1])
#     if int(timestamp) < start_time or int(timestamp) > end_time:
#         return 0
#     for time_p in token_price:
#         start, end = time_p[0].split("_")
#         if int(timestamp) >= int(start) and int(timestamp) < int(end):
#             return time_p[1]

def readCsvPrice(event_saved_file):  # timstamp, price
    ## return 1_3 : price 
    with open(event_saved_file, 'r') as f:
        f_csv =  csv.DictReader(f)
        results = [ ( int(row["timstamp"]), row["price"] ) for row in f_csv ]
        results.sort()   #为了保证一致性，对时间进行重新排序
    
    start_time, end_time = results[0][0], results[-1][0]   
    start_price, end_price = results[0][1], results[-1][1]

    time_price = { ti : 0  for ti in range(start_time, end_time ) } 

    index = 1   
    for time in time_price:
        if time < results[index][0]:
            time_price[time] = results[index-1][1]
        else:
            index += 1
            time_price[time] = results[index-1][1]
    
    min5_token_start = { k : start_price for k in range(start_time - 300, start_time) }
    min5_token_end =   { k : end_price   for k in range(end_time ,   end_time + 301) }  #前后增加5分钟的价格区间
    time_price.update(min5_token_start)
    time_price.update(min5_token_end)
    return time_price


def get_block_timestamp(time_block_dir, chain):
    # return  {block : [timestamp, date]}  sort()
    timestamp_path = glob.glob(time_block_dir + f"/{chain}*.csv")
    assert len(timestamp_path) > 0, "notice !"
    # print("timestamp_path", timestamp_path)
    block_timestamp = {}
    for ti in timestamp_path:
        block_times = readCsvRaw(ti)
        for bt in block_times:
            date = bt[1]
            datetime_stamp = int(datetime.timestamp(datetime.strptime(date, '%Y-%m-%d %H:%M:%S')))  #date time to timestamp
            block_timestamp[int(bt[0])] = [datetime_stamp, date]  
    block_timestamp = dict(sorted(block_timestamp.items(), key=lambda x:x[1], reverse = False)) 
    # print(len(block_timestamp))  # {block : [timestamp, date]}
    return block_timestamp


def get_timstamp_date(date):
    return int(datetime.timestamp(datetime.strptime(date, '%Y-%m-%d %H:%M:%S')))   #datetime_stamp

if __name__ == "__main__":
    data = ""
    time_stamp = get_timstamp_date(date)