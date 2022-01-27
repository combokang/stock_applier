import requests
from bs4 import BeautifulSoup
import configparser
import datetime
import sys
import random
import time

# 若今天為星期日則不執行爬蟲
if datetime.date.today().weekday() == 6:
    sys.exit("星期日程式不執行")

print("開始抓取網頁資料，請稍後...\n")

# 增加亂數延遲，模擬使用者
time.sleep(random.randint(0, 10))

# 抓取網頁資料，附加headers
url = "https://histock.tw/stock/public.aspx"  # 資料來源：嗨投資 網站
data = requests.get(url, headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"})
soup = BeautifulSoup(data.text, "html.parser")
html_list = soup.find("table").find_all("tr")  # 原始股票列表的html(首列為標題列)


# 處理html、篩選欄位，建立股票資料
stock_list = []  # 處理過的股票列表(二階巢狀)
for stock in html_list[1:]:  # for迴圈處理每筆股票的html、篩選欄位
    td = stock.find_all("td")
    name = td[1].find("a").string.replace("\xa0", " ")  # [0]股票代號+名稱(字串)
    selling_price = float(td[6].string.strip())  # [1]承銷價
    try:
        gain = int(td[8].find("span").string.replace(",", ""))  # [2]申購總獲利
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
        # 讀取最高承銷價設定
        max_price = float(config["parameters"]["max_price"])
        if max_price == 0:
            PRICE_FILTER_STR = "最高承銷價: 不進行篩選"
        else:
            PRICE_FILTER_STR = f"最高承銷價: {max_price}"
        print(PRICE_FILTER_STR)
        file.write(PRICE_FILTER_STR + "\n")

        # 讀取最低總獲利設定
        min_gain = int(config["parameters"]["min_gain"])
        GAIN_FILTER_STR = f"最低總獲利: {min_gain}"
        print(GAIN_FILTER_STR)
        file.write(GAIN_FILTER_STR + "\n")

        # 讀取狀態設定
        obj_state = config["parameters"]["obj_state"]
        if obj_state == "0":
            STATE_FILTER_STR = "狀態: 不進行篩選"
        else:
            STATE_FILTER_STR = f"狀態: {obj_state}"
        print(STATE_FILTER_STR)
        file.write(STATE_FILTER_STR + "\n")
    except:
        print("參數設定有誤，請開啟config.ini設定檔進行檢查")
    print("以上參數可使用記事本開啟config.ini設定檔進行設定\n")

    title = "符合條件的可申購股票:\n股票名稱\t承銷價\t總獲利\t狀態"
    print(title)
    file.write(title + "\n")

    # 寫入股票
    COUNT = 0  # 結果筆數
    SEARCH_RESULT = []  # 篩選結果
    for stock in stock_list:  # 每筆股票
        if stock[2] >= min_gain:  # 總獲利>=進行最低總獲利
            # 有進行最高承銷價篩選，且承銷價>=最高承銷價，則跳過不選
            if max_price != 0 and stock[1] >= max_price:
                continue
            else:
                # 有進行狀態篩選，且狀態不符，則跳過不選
                if obj_state != "0" and stock[3] not in obj_state.split(","):
                    continue
                else:   # 全部條件皆符合則加入搜尋結果、印出且寫入txt檔案備存
                    SEARCH_RESULT.append(stock)  # 加入篩選結果
                    stock_str = f"{stock[0]}\t{stock[1]}\t{stock[2]}\t{stock[3]}"
                    print(stock_str)
                    file.write(stock_str + "\n")
                    COUNT += 1

    # 將最終筆數寫入檔案並印出
    str = f"共 {COUNT} 筆結果\n"
    print(str)
    file.write(str)
