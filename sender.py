import email.message
import datetime
import smtplib

import crawer

# 建立變數
receiver = "hiromoto1995@gmail.com"
today = datetime.date.today().strftime("%Y/%m/%d")

# 設定郵件內容
msg = email.message.EmailMessage()
msg["From"] = "stockapplyhelper@gmail.com"
msg["To"] = "stockapplyhelper@gmail.com"
msg["BCC"] = receiver
msg["Subject"] = f"{today} 股票申購標的test"
# with open("stock_list.txt", mode="r", encoding="utf-8") as file:
#     msg.set_content(file.read())
with open("stock_list.txt", mode="r", encoding="utf-8") as file:
    readlines = file.readlines()
    htmlmsg = f"""
    <p>{readlines[0]}<br>{readlines[1]}<br>{readlines[2]}<br>符合條件的可申購股票:</p>
    <table border=\"1\" style=\"border-collapse: collapse\">
    <tr><th>股票名稱</th><th>承銷價</th><th>總獲利</th><th>狀態</th></tr>"""
    for line in readlines[5:]:
        htmlmsg += "<tr>"
        inline = line.split("\t")
        for item in inline:
            htmlmsg += f"<td>{item}</td>"
        htmlmsg += "</tr>"
    htmlmsg += "</table>"
msg.add_alternative(htmlmsg, subtype="html")

# 連接gmail server
server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login("stockapplyhelper@gmail.com", "python2022")
server.send_message(msg)
server.close

print(f"{today}信件已寄送")
