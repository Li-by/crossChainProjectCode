import requests
import csv
file = open('demo04.csv', 'w')
writer = csv.writer(file)

def make_query(query, url):
    # print(query)
    request = requests.post(url, json={'query': query}, verify=False)  # , 'variables': variables
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
    return request


first = 1000
skip = 0
begin_time = ""
end_time = ""


def get_query_str(begin_time, end_time):#, skip=0, first=1000):
    #  first=1000 每次搜索只能最多取出1000条记录
    query = """
    query
    MyQuery
    {
        swaps(
            first: 1000
        where: {pair_: {id: "0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852"}, timestamp_gte: 
        """

    query2 = """
        ,
                timestamp_lte:"""
    query3 = """
    }
        orderBy: timestamp
        orderDirection: desc
    ) {
        id
    amountUSD
    amount1Out
    amount1In
    amount0Out
    amount0In
    timestamp
    pair
    {
        token1
    {
        name
    symbol
    }
    token0
    {
        name
    symbol
    }
    id
    }
    }
    }
    """

    all_query = query +  str(begin_time) + query2 + str(end_time) + query3
    return all_query



#想要回溯的小时
want_times = 5
ans = {}

t1 = 1670076875
for i in range(1,want_times):
    
    t2 = t1 - 60 * 60 #小时  #"1670124995"

    get_query_str_ = get_query_str(t2,t1)
    # print("join str : ", get_query_str_)

    url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"

    try:
        res = make_query(get_query_str_, url)
        # print(res)
        if res:
            data=res['data']['swaps']
            for d in data:
                # print(d)
                amount1Out = d['amount1Out']
                amount1In = d['amount1In']
                amount0Out = d['amount0Out']
                amount0In = d['amount0In']
                abs1 = abs(float(amount1In) - float(amount1Out))
                abs2 = abs(float(amount0In) - float(amount0Out))
                if abs2 != 0:
                    price = abs1 / abs2
                else:
                    price = 0
                time = d['timestamp']
                ans[time] = price
    except:
        pass

    print(f"scan from {t2} to {t1}")
    t1 = t2

# print('weth_usdt history price :')
writer.writerow(['weth_usdt history price :'])
# print(ans)
for key in ans:
    writer.writerow([key,ans[key]])










