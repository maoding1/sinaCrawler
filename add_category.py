from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options
import time
import traceback
import pymysql
import yaml
from eval import NewsClassifier

# 对数据库中已有的category为NULL的行进行更新

def getConfig(path):
    with open(path, 'r', encoding='utf-8') as f:
        result = yaml.safe_load(f)
        return result

def getdb(config):
    db = pymysql.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['databaseName'],
        charset='utf8mb4'
    )
    return db

configPath = '/root/sinaCrawler/Config.yaml'
if __name__ == '__main__':
    config = getConfig(configPath)
    db = getdb(config)
    cursor = db.cursor()
    classifier = NewsClassifier()
    cursor.execute("SELECT * FROM news WHERE category IS NULL")
    rows = cursor.fetchall()

    for row in rows:
        news_id = row[0] # id列下标为0
        title = row[1] # title列下标为1

        # 调用classify函数获取类别
        category = classifier.classify(title)

        # 更新category值
        cursor.execute("UPDATE news SET category = %s WHERE id = %s", (category, news_id))

    # 提交事务
    db.commit()

    