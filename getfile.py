import requests
from bs4 import BeautifulSoup
import ast
import time
import random
import json
import os
from http import HTTPStatus
import dashscope
import jieba
from collections import Counter

# 添加大模型key
dashscope.api_key = "自己的key"
model = 'qwen-turbo'
# 设置模型关键词
txt = """
“请帮我提取以下文章的关键内容，并将摘要长度控制在100到200字以内：
[{}]
请注意，摘要需要简洁明了，能够准确反映文章的核心信息和主要观点。
"""


# 利用模型压缩文章
def extractKeyContent(prompt_text=''):
    resp = dashscope.Generation.call(
        model=model,
        prompt=prompt_text
    )
    if resp.status_code == HTTPStatus.OK:
        return resp.output["text"]
    else:
        return []


# def getArticleDirectory(url="https://news.163.com/"):
#
#     res = requests.get(url=url, headers=headers)
#     # if res.status_code == 200:
#     #     # content = res.content
#     #     # encoding = chardet.detect(content[:10])['encoding']
#     #     # text = content.decode(encoding)
#     #     txt = res.text
#     #     # 使用lxml解析器是用C写的原装的快
#     #     soup = BeautifulSoup(txt, 'lxml')
#     #     title = soup.title.string
#     #     print(soup)
#     try:
#         res = requests.get(url=url, headers=headers)
#         res.raise_for_status()
#     except requests.exceptions.RequestException as e:
#         print("Error: %s" % e)
#         return
#     txt = res.text
#     soup = BeautifulSoup(txt, 'lxml')
#     title = soup.title.string
#     # start_comment = soup.find(text=lambda text: isinstance(text, Comment) and '热点排行 开始' in text)
#     # if start_comment:
#     #     # 找到注释后面的div元素
#     #     hot_rank_div = start_comment.find_next_sibling('div')
#     #
#     #     # 在找到的div中提取所有的<a>标签
#     #     if hot_rank_div:
#     #         a_tags = hot_rank_div.find_all('a')
#     #
#     #         # 打印出所有<a>标签的href属性和文本内容
#     #         for a_tag in a_tags:
#     #             print(f"链接: {a_tag['href']}, 标题: {a_tag.get_text()}")
#     # else:
#     #     print("未找到'热点排行 开始'注释。")
#     div = [{"href": div_1.find("a")['href'], "title": div_1.find("a")['title']}
#            for div_1 in soup.find("div", class_="mt35 mod_hot_rank clearfix").find_all("li")]
#     print(div)
#     return div
#     # print(soup)

# 通过url爬取网易的新闻
def getArticle(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://news.163.com/',
        'Sec-Ch-Ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
        'Cookie': 's_n_f_l_n3=51dc51a69ba982ab1718444589868; pver_n_f_l_n3=a; _ntes_origin_from=; _ntes_nuid=dc64733148790a9ae242af1acb2fed04; _antanalysis_s_id=1718444590220; UserProvince=%u5168%u56FD; WM_NI=Rv7DcAuewRaWbeX%2F5Vigyz%2Ba45lZwbN94Kv5nrTaVegTOnW%2FJwT93gIvZtcfLyKGYUtwIauUBMf%2FQUNprgOQrK1Ws%2BqnfWnaqxPToQvxQJtvnaIdxKM1lSnTn5ji2RrTb2U%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eea8e1678388fcd3db3c87868fb3c84e979a9b83cb4a82beaeaec73e868783d6e82af0fea7c3b92a92aaf9a5e24bb7bbb9b3e45da2bb98d0b85eabb9b79baa6bf8eba4bbf66a8ee7fcacf53faeae9c82d56fa58c818fd6258aa99cdab26d8baa9695e26e90a785a8dc5fb8a98782f85f8293aad0d45f8eb0be88ce5bb295ffb8f221b3b2aab8ed6bb3a8a0b5ee5bb6a89fabf77eaebf8785fb418fefa4b4ed60aeeba68ab15ab28caed3d837e2a3; WM_TID=yikVwvlc7ztEBREVBEKWAUbLIGuFdItP; ne_analysis_trace_id=1718444640167; Hm_lvt_f8682ef0d24236cab0e9148c7b64de8a=1718444641; Hm_lpvt_f8682ef0d24236cab0e9148c7b64de8a=1718444641; vinfo_n_f_l_n3=51dc51a69ba982ab.1.0.1718444589867.0.1718444648556'
    }
    try:
        res = requests.get(url=url, headers=headers)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error: %s" % e)
        return

    text = res.text
    soup = BeautifulSoup(text, 'lxml')
    post_body = soup.find('div', class_="post_body")
    content = str()
    if post_body:
        content = post_body.get_text(strip=True, separator="\n")
    return content


def getArticleApi(file_path="data1.json"):

    # 判断dict_news.json是否存在，减少没必要的执行
    if not os.path.exists("dict_news.json"):
        # 可以选择手动添加代理
        proxies = {
            "http": "http://118.163.13.200"
        }
        try:
            res = requests.get(url="http://hot.cigh.cn/netease",  timeout=3)
            res.raise_for_status()
            dict_news = ast.literal_eval(res.text)
        except requests.exceptions.RequestException as e:
            print("Error: %s" % e)
            return

        with open("dict_news.json", 'w', encoding='utf-8') as f:
            json.dump(dict_news, f, ensure_ascii=False, indent=4)
    else:
        with open("dict_news.json", 'r', encoding='utf-8') as f:
            dict_news = json.load(f)

    # 判断data1.json是否存在，减少没必要的执行
    if not os.path.exists(file_path):
        # 读取停顿词
        with open("stop_words.txt", 'r', encoding='utf8') as file:
            stop_data = []
            for line in file:
                stop_data.append(line.strip())
            stop_data = set(stop_data)

        # 拿到带有url的数据
        data = dict_news["data"]
        news = []

        for dic in data:

            text = getArticle(dic["url"])
            if not text:
                continue
            # 增加访问随机性
            time.sleep(random.random() + 0.001)

            # 利用jieba分割文章
            words = jieba.lcut(text)
            # 不知道为什么jieba好不稳定，有时结果包含'\n'、'…'、' '；
            word_freq = Counter(word for word in words if word not in stop_data
                                and word != '\n' and word != '…' and word != ' ')
            keyword = {word: freq for word, freq in word_freq.most_common(20)}

            # 组合起来
            news.append({"title": dic["title"], "content" : text, "url": dic["url"], "keyword":keyword})

        date = {"time": dict_news['updateTime'], "news": news}

        # 保存到本地
        with open('data1.json', 'w', encoding='utf-8') as f:
            json.dump(date, f, ensure_ascii=False, indent=4)
        return date

    return ""


# 压缩content
def ProcessingData(in_file_path="data1.json", out_file_path="data2.json"):

    # 判断data2.json是否存在，减少没必要的执行
    if not os.path.exists(out_file_path):
        # 读取data1.json
        with open(in_file_path, 'r', encoding='utf-8') as f:
            dict_news = json.load(f)
            data = dict_news["news"]

        for dic in data:
            content = dic["content"]
            if not content:
                continue

            # 利用模型压缩文章
            desc = extractKeyContent(txt.format(content))
            # 如果还是太长就在压缩一次
            if len(desc) > 200:
                content = extractKeyContent(txt.format(content))
            if not content:
                continue

            # 组合起来
            dic["content"] = desc

        data = {"time": dict_news['time'], "news": data}
        with open(out_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data
    return ""


# 组合起来方便外部调用
def AddNews():
    getArticleApi()
    ProcessingData()


if __name__ == '__main__':
    AddNews()

