# Sina_crawler

## 介绍
对新浪新闻滚动页：https://news.sina.com.cn/roll/ 中的新闻进行爬取，对每条新闻进行分类与实体关系提取，并存储到mysql数据库中

爬取数据示例： id, title, time,  source, text, category, relationship

'20', '万科A(000002.SZ)：资金存入代理行指定账户以全数偿付到期美元中期票据本息', '2024年03月08日 19:37', '市场资讯', '来源：格隆汇\n格隆汇3月8日丨万科A(000002.SZ)公布，2018年12月11日，本公司之全资子公司万科地产(香港)有限公司在香港联合交易所披露了关于发行于2024年到期6.3亿美元的5.35%中期票据(ISIN:XS1917548247)的公告。此票据将于2024年3月11日到期。\n2024年3月8日，本公司已按票据尚未偿还本金金额连同累计至到期日的利息资金合计646,852,500.00美元存入于代理行指定银行账户，以全数偿付到期票据本息。\n海量资讯、精准解读，尽在新浪财经APP', 'realty', '万科A,万科地产(香港)有限公司,全资子公司\n万科地产(香港)有限公司,香港联合交易所,披露\n万科A,票据,发行\n万科A,票据,到期\n万科A,票据,全数偿付\n万科A,代理行指定银行账户,存入\n万科A,新浪财经APP,资讯解读提供方'

由于实际新闻质量和数据集，模型大小的限制，分类和实体关系提取结果仍需改进。


## 准备

### 1.1 爬虫任务准备
在服务器中启动mysql服务

安装edge浏览器 以及对应版本的driver 

更改Config.yaml中相应的配置

执行`pip install -r requirements.txt` 安装相关依赖

### 1.2 分类
新闻分类方法参考"https://github.com/649453932/Chinese-Text-Classification-Pytorch"

环境准备参照上面的仓库，注意pytorch版本需要高一些，自测1.10.0版本可行

参照eval.py.里面提供了自己写的预测类`Newsclassifier()`，因为配置写死在代码中，目前仅支持训练时配置为的--model=FastText与--embedding = random的模型，通过更改__init__方法中的设置理论上可以支持其他训练配置的模型文件 使用方法参照eval.py的main方法

### 1.3 新闻实体关系提取
使用文心一言模型，参照relationship_extraction.py,注意设置好自己的apikey和secretkey。

prompt为自己随便写的，可以根据需求灵活更改

### 1.4 定时爬虫与日志
参照execute.sh 中注释

## 文件与运行说明
执行createTable.py在mysql数据库中建表 建表语句参见此文件。

执行sinaCrawler.py进行爬取 

执行run.py进行模型训练 需要命令行参数，参照"https://github.com/649453932/Chinese-Text-Classification-Pytorch"

其他重要文件：
eval.py包含新闻分类代码
relationship_extraction.py包含新闻实体关系提取代码
