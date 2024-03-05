import json
import redis
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options
import time
import traceback
import pymysql
import yaml

url = 'https://news.sina.com.cn/roll/'
configPath = './Config.yaml'
page_num = 50

insert_sql = f"""INSERT INTO `news`(`title`, `time`, `source`, `text`, `category`)
                        VALUES (%s,%s,%s,%s,NULL)"""

news_li_xpath = "/html/body/div[1]/div[1]/div[2]/div[3]/div[2]/div//li"
title_xpath = "./span[2]/a"
next_page_xpath = '/html/body/div[1]/div[1]/div[2]/div[3]/div[2]/div/div/span[last()]'



def getConfig(path):
    with open(path, 'r', encoding='utf-8') as f:
        result = yaml.safe_load(f)
        return result

def getdb(config):
    db = pymysql.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['databaseName']
    )
    return db

def getRedisClient(config):
    redis_client = redis.Redis(
        host=config['redis']['host'],
        port=config['redis']['port'],
        db=config['redis']['db']
    )
    return redis_client

def get_detailed_page(url, cursor):
    # print(url)
    driver.get(url)
    try:
        title = driver.find_element(By.CLASS_NAME, 'main-title').text
        time = driver.find_element(By.CLASS_NAME, 'date').text
        try :
            source = driver.find_element(By.CLASS_NAME, 'source.ent-source').text
        except:
            source = driver.find_element(By.CLASS_NAME, 'source').text
        text = driver.find_element(By.CLASS_NAME, 'article').text
        cursor.execute(insert_sql, (title, time, source, text))


    except:
        traceback.print_exc()
        sys.stderr.write(f"wrong url , please check:{url}\n")

if __name__ == '__main__':
    options = Options()
    options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
    #后台运行 不加载图片
    options.add_argument('--no-sandbox')
    options.add_argument("--headless")
    options.add_argument('blink-settings=imagesEnabled=false')

    config = getConfig(configPath)
    service = Service(executable_path=config['driver_path'])
    driver = webdriver.Edge(service=service, options=options)

    redis_client = getRedisClient(config)

    news_detail_urls = []
    driver.get(url)
    for i in range(page_num):
        time.sleep(1)
        news_li_lists = driver.find_elements(By.XPATH, news_li_xpath)
        encounter_crawled_data = False
        for news in news_li_lists:
            try:
                news_url = news.find_element(By.XPATH, title_xpath).get_attribute('href')
            except:
                news_url = news.find_element(By.XPATH, './a[2]').get_attribute('href')
            if redis_client.sismember('urls', news_url):
                print(f"遇到已爬取过的url: {news_url} ！")
                encounter_crawled_data = True
                break
            else:
                redis_client.sadd('urls', news_url)
                news_detail_urls.append(news_url)
        if encounter_crawled_data:
            break
        wait = WebDriverWait(driver, 10)  # 10秒内每隔500毫秒扫描1次页面变化，当出现指定的元素后结束。
        wait.until(lambda driver: driver.find_element(By.XPATH, next_page_xpath))
        next_page = driver.find_element(By.XPATH, next_page_xpath)
        next_page.click()

    db = getdb(config)
    cursor = db.cursor()

    count = 0
    print(f"准备爬取{len(news_detail_urls)}条新闻")
    for url in news_detail_urls:
        get_detailed_page(url, cursor)
        count += 1
        if count % 20 == 0:
            print(f"已爬取{count}条新闻")
    print(f"爬取结束， 共爬取{count}条新闻！")
    try:
        db.commit()
    except:
        db.rollback()

    # with open(json_path, 'w', encoding='utf-8') as file:
    #     json.dump(news_list, file, indent=4, ensure_ascii=False)