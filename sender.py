import email.message
import datetime
import smtplib
import configparser

import crawler

today_str = datetime.date.today().strftime("%Y/%m/%d")

# 讀取config中的篩選條件
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
receiver = config["email"]["receiver"]

# 設定郵件基礎內容
msg = email.message.EmailMessage()
msg["From"] = "stockapplyhelper@gmail.com"
msg["To"] = "stockapplyhelper@gmail.com"
msg["BCC"] = receiver
msg["Subject"] = f"【股票申購助手】{today_str} 股票申購標的"

# 信件html內文列出符合條件的股票，若結果為0筆則以文字取代表格進行提示
with open("stock_list.txt", mode="r", encoding="utf-8") as file:
    readlines = file.readlines()
    htmlmsg = f"""
    <p>{readlines[0]}<br>{readlines[1]}<br>{readlines[2]}<br>符合條件的可申購股票:</p>"""
    if crawler.COUNT == 0:  # 篩選結果筆數
        htmlmsg += "<p>今日無符合條件的股票可申購</p>"
    else:
        htmlmsg += """<table border=\"1\" style=\"border-collapse: collapse\">
        <tr><th>股票名稱</th><th>承銷價</th><th>總獲利</th><th>狀態</th></tr>"""
        for line in readlines[5:-1]:
            htmlmsg += "<tr>"
            inline = line.split("\t")
            for item in inline:
                htmlmsg += f"<td>{item}</td>"
            htmlmsg += "</tr>"
        htmlmsg += "</table>"
        htmlmsg += f"<p>{readlines[-1]}</p>"
msg.add_alternative(htmlmsg, subtype="html")

# 連接gmail server
server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login("stockapplyhelper@gmail.com", "python2022")
server.send_message(msg)
server.close

print(f"{today_str}信件已寄送")
