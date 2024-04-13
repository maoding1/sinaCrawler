import pymysql
import yaml

sql = """CREATE TABLE news (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL Unique,
  time VARCHAR(255) NOT NULL,
  source VARCHAR(255) NOT NULL,
  text TEXT NOT NULL,
  category VARCHAR(255)
);"""

def getConfig(path):
    with open(path, 'r', encoding='utf-8') as f:
        result = yaml.safe_load(f)
        return result

if __name__ == '__main__':
    path = 'Config.yaml'
    config = getConfig(path)
    # print(config)

    # Open database connection
    db = pymysql.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['databaseName']
    )

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Drop table if it already exists using execute() method.
    cursor.execute("DROP TABLE IF EXISTS news")

    cursor.execute(sql)
    print("Created table Successfully.")