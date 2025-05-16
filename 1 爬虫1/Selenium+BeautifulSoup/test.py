import pymysql
from selenium import webdriver
import time
import pymysql
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import random

def init_mysql():
    dbparams = {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "123456",
        "database": "spider",
        "charset": "utf8",
    }
    # 初始化数据库连接
    conn = pymysql.connect(**dbparams)
    cur = conn.cursor()
    return cur, conn


""" 获取数据库连接 """
cur, conn = init_mysql()

sql = """INSERT INTO lagou_jobs 
    (job_address,salary,requirements,company,company_info,job_info,highlights) 
    VALUES (%s,%s,%s,%s,%s,%s,%s)"""


""" 先登录 """
# 初始化浏览器，使用无头模式
options = webdriver.EdgeOptions()
options.add_argument("--disable-gpu")  # 禁用GPU加速
options.add_argument("--disable-blink-features=AutomationControlled")  # 隐藏自动化特征

driver = webdriver.Edge(options=options)
# 全屏
driver.maximize_window()
# 请求拉勾网首页
driver.get("https://www.lagou.com/")

# 暂停，进行手动登录。
input("手动登录完成按回车")


""" 爬取每一页 """
page = 1  # 开始页/当前页
all_page = 30  # 结束页

max_retries = 10  # 设置最大重试次数避免死循环
retry_count = 0

while page <= all_page:
    print(f"第{page}页")

    while retry_count < max_retries:
        driver.get(
            f"https://www.lagou.com/wn/jobs?cl=false&fromSearch=true&kd=python&pn={page}"
        )
        
        try:
            # 显式等待元素加载，最多10秒
            job_list = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "jobList"))
            )
            break  # 成功获取元素后退出循环
        except TimeoutException:
            print(f"第{retry_count+1}次尝试超时，刷新页面重试...")
            driver.refresh()
            retry_count += 1
            time.sleep(10)  # 避免连续刷新过快

    # 检查是否成功获取元素
    if retry_count < max_retries:
        # 获取源码
        html = driver.page_source
        # 使用BeautifulSoup解析
        soup = BeautifulSoup(html, "html.parser")

        for item in soup.select("div.item__10RTO"):
            try:
                # 岗位名和工作地址
                job_address = item.select_one(".p-top__1F7CL a").text.strip()
            except Exception as e:
                print('异常 ', e)
                job_address = ''

            try:
                # 薪资
                salary = item.select_one(".money__3Lkgq").text.strip()
            except Exception as e:
                print('异常 ', e)
                salary = ''

            try:
                # 要求
                requirements = item.select_one(".p-bom__JlNur").text.strip()
            except Exception as e:
                print('异常 ', e)
                requirements = ''

            try:
                # 公司名称
                company = item.select_one(".company-name__2-SjF a").text.strip()
            except Exception as e:
                print('异常 ', e)
                company = ''

            try:
                # 公司信息
                company_info = item.select_one(".industry__1HBkr").text.strip()
            except Exception as e:
                print('异常 ', e)
                company_info = ''

            try:
                # 岗位信息
                tag_list = [span.text for span in item.select(".ir___QwEG span")]
                job_info = "/".join(tag_list)
            except Exception as e:
                print('异常 ', e)
                job_info = ''

            try:
                # 亮点
                highlights = item.select_one(".il__3lk85").text.strip()
            except Exception as e:
                print('异常 ', e)
                highlights = ''

            cur.execute(
                sql,
                (
                    job_address,
                    salary,
                    requirements,
                    company,
                    company_info,
                    job_info,
                    highlights,
                ),
            )

    else:
        print("已达到最大重试次数，元素仍未加载")

    conn.commit()

    time.sleep(50 + random.uniform(0, 20))
    page += 1



""" 关闭 """
# 关闭数据库连接
cur.close()
conn.close()
# 关闭浏览器
driver.quit()
