import pymysql
import yaml
from eval import NewsClassifier
from relationship_extraction import get_response
# 对数据库中已有的category或relationship为NULL的行进行更新

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
    # classifier = NewsClassifier()
    cursor.execute("SELECT * FROM news WHERE relationship IS NULL OR relationship = ''")
    rows = cursor.fetchall()
    print(len(rows))
    cnt = 0
    for row in rows:
        news_id = row[0] # id列下标为0
        # title = row[1] # title列下标为1
        text = row[4]  # text列下标为4
        # 调用classify函数获取类别
        # category = classifier.classify(title)
        relationship = get_response(text)
        try:
            # cursor.execute("UPDATE news SET category = %s WHERE id = %s", (category, news_id))
            cursor.execute("UPDATE news SET relationship = %s WHERE id = %s", (relationship, news_id))
            db.commit()
            cnt += 1
            if(cnt % 10 == 0):
                print("已处理%d条信息" % cnt)
        except:
            db.rollback()
    

    