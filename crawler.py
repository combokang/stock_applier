import requests
from bs4 import BeautifulSoup
import configparser
import datetime
import sys
import random
import time

# 若今天為星期日則不執行爬蟲
if datetime.date.today().weekday() == 6:
    sys.exit("星期日不執行")

print("開始抓取網頁資料，請稍後...")

# 增加亂數延遲，模擬使用者
time.sleep(random.randint(0, 10))

# 抓取網頁資料，附加headers
url = "https://histock.tw/stock/public.aspx"  # 資料來源：嗨投資 網站
data = requests.get(url, headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"})
soup = BeautifulSoup(data.text, "html.parser")
org_list = soup.find("table").find_all("tr")  # 原始股票列表的html(首列為標題列)


# 處理html、篩選欄位，建立股票資料
stock_list = []  # 處理過的股票列表(二階巢狀)
for stock in org_list[1:]:  # for迴圈處理每筆股票的html、篩選欄位
    td = stock.find_all("td")
    name = td[1].find("a").string.replace("\xa0", " ")  # [0]股票代號+名稱(字串)
    selling_price = td[6].string.strip()  # [1]承銷價(字串)
    try:
        gain = td[8].find("span").string.replace(",", "")  # [2]申購總獲利(字串)
    except:
        gain = "0"
    try:
        state = td[13].find("span").string  # [3]申購狀態(字串)
    except:
        state = "未開始"  # 無狀態則賦予狀態為未開始
    single_stock = [name, selling_price, gain, state]   # 單筆股票資訊
    stock_list.append(single_stock)  # 將單筆股票加入處理結果

# 從config讀取篩選條件
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

# 將搜尋結果寫入stock_list.txt檔案
with open("stock_list.txt", mode="w", encoding="utf-8") as file:
    # 寫入篩選條件與文字敘述
    try:
        max_price = float(config["parameters"]["max_price"])  # 讀取最高承銷價設定
        if max_price == 0:
            str = "最高承銷價: 不進行篩選"
            print(str)
            file.write(str + "\n")
        else:
            str = f"最高承銷價: {max_price}"
            print(str)
            file.write(str + "\n")
        min_gain = int(config["parameters"]["min_gain"])  # 讀取最低總獲利設定
        str = f"最低總獲利: {min_gain}"
        print(str)
        file.write(str + "\n")
        obj_state = config["parameters"]["obj_state"]  # 讀取狀態設定
        if obj_state == "0":
            str = "狀態: 不進行篩選"
            print(str)
            file.write(str + "\n")
        else:
            str = f"狀態: {obj_state}"
            print(str)
            file.write(str + "\n")
    except:
        print("參數設定有誤，請開啟config.ini設定檔進行檢查")
    print("以上參數可使用記事本開啟config.ini設定檔進行設定\n")

    title = "符合條件的可申購股票:\n股票名稱\t承銷價\t總獲利\t狀態"
    print(title)
    file.write(title + "\n")

    # 寫入股票
    COUNT = 0  # 篩選結果筆數
    for line in stock_list:  # 每筆股票
        if min_gain <= int(line[2]):  # 進行最低總獲利篩選
            # 進行最高承銷價篩選，且價格不符
            if max_price != 0 and max_price < float(line[1]):
                continue
            else:
                if obj_state != "0" and line[3] not in obj_state.split(
                    ","
                ):  # 進行狀態篩選，且狀態不符
                    continue
                else:
                    line_str = "\t".join(line)
                    print(line_str)
                    file.write(line_str + "\n")
                    COUNT += 1
    # 將最終筆數寫入檔案並印出
    str = f"共 {COUNT} 筆結果"
    print(str)
    file.write(str)
