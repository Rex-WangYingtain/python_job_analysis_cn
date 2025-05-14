import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="123456",
    database="spider",
)


df = pd.read_sql("SELECT * FROM lagou_jobs", conn)

# 其实通过pandas可以 to 出很多
# 比如csv，xlsx，json，xml，html

df.to_csv("lagou_jobs.csv", index = False)
df.to_excel("lagou_jobs.xlsx", index = False)
df.to_json("lagou_jobs.json", orient = "records")    # orient = "records" 表示以记录形式（每行是一个 JSON 对象）输出 JSON 数据。
df.to_xml("lagou_jobs.xml")
df.to_html("lagou_jobs.html")
