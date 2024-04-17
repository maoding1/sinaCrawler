import requests
import json

API_KEY = "xxx"
SECRET_KEY = "xxx"
## 下面请求的url需要根据模型进行替换
def get_response(content):
    if len(content) > 1500:
        content = content[:1500]
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + get_access_token()
    
    question = """你是一位经验丰富的新闻工作者。请为以下新闻进行实体关系提取，并尽量简洁地表达关系。

具体的新闻内容：
%s
要求：
1. 提取的实体应为现实中存在的具体事物，如公司、人物、地点等，确保实体与新闻内容紧密相关。
2. 实体之间的关系应简洁明了，如“父子”、“拥有”、“位于”等，避免使用抽象概念“是”等。
3. 输出结果应包括实体名称和关系，如“马云创建了一家著名的互联网公司阿里巴巴。”输出马云,阿里巴巴,创建。
4. 对于小明这一学生身份，请勿输出“小明,学生,是”等表述。
5. 要求返回为多行，每一行的格式为 Entity1,Entity2,Relationship 即Entity1与Entity2的关系为Relationship
6. 不要出现重复的实体关系,即多行拥有相同的Entity1与Entity2
7. 并且返回的行数不要超过10行,即保留你认为最为重要的几条实体关系。
8. 请千万不要千万不要添加多余信息：比如行开头的序号，还有“以下是根据新闻内容提取的实体关系：”之类的。
一个返回结果的示例如下：
小明,小红,同学
小张,小李,同事""" % (content)
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": question
            },
        ],
        "disable_search": False,
        "enable_citation": False
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    # 解析JSON响应
    response_json = json.loads(response.text)

    # 获取"result"字段的值
    try:
        result = response_json["result"]
    except:
        print(response_json)
    return result

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

if __name__ == '__main__':
    content = "林奥是我的儿子"
    response = get_response(content)
    print(response)
