import email.message
import datetime
import smtplib
import configparser

import crawler

today_str = datetime.date.today().strftime("%Y/%m/%d")  # 今天日期

# 讀取config中的email設定
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
receiver = config["email"]["receiver"]

# 設定郵件基礎內容
msg = email.message.EmailMessage()
msg["From"] = "stockapplyhelper@gmail.com"
msg["To"] = "stockapplyhelper@gmail.com"
msg["BCC"] = receiver

# 依結果是否為0筆決定信件標題，且0筆時以文字取代表格進行提示
# 信件html內文列出 篩選條件 和 符合條件的股票
htmlmsg = f"<p>{crawler.PRICE_FILTER_STR}<br>{crawler.GAIN_FILTER_STR}<br>{crawler.STATE_FILTER_STR}</p>"
if crawler.COUNT == 0:  # 若結果為0筆
    msg["Subject"] = f"【申購助手】{today_str} 今日無符合條件的股票可申購"
    htmlmsg += "<p>今日無符合條件的股票可申購</p>"
else:
    msg["Subject"] = f"【申購助手】{today_str} 股票申購標的"
    htmlmsg += """
    <p>符合條件的可申購股票:</p>
    <table border=\"1\" style=\"border-collapse: collapse\">
    <tr><th>股票名稱</th><th>承銷價</th><th>總獲利</th><th>狀態</th></tr>"""
    for line in crawler.SEARCH_RESULT:
        htmlmsg += "<tr>"
        for item in line:
            htmlmsg += f"<td>{item}</td>"
        htmlmsg += "</tr>"
    htmlmsg += "</table>"
    htmlmsg += f"<p>共 {crawler.COUNT} 筆結果</p>"

msg.add_alternative(htmlmsg, subtype="html")

# 連接gmail server
server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login(config["email"]["sender"], config["password"]["pw"])
server.send_message(msg)
server.close

print(f"{today_str}信件已寄送")
