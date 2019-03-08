#    Copyright 2016 WiseDoge

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from bs4 import BeautifulSoup
import requests
from requests import HTTPError, URLRequired
from requests.exceptions import RequestException
import random
from fake_useragent import UserAgent
import datetime
import json
import brotli
nowTime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
ua = UserAgent()
theusingua=ua.random
val = json.load(open("setting.json"))
try:
    prival = json.load(open('../private.json'))
except OSError as err:
    print("OS error: {0}".format(err))
    prival = {
        "flippagenum": random.randint(0, 4),
        "mongodbnet": {
            "host": "localhost",
            "port": 27017
        }
    }
    #prival["flippagenum"] = random.randint(0, 4)
nowproxy = val['proxies']
chooseproxy = nowproxy[random.randint(0, len(nowproxy)-3)]
print('the proxy which was chosed is '+str(chooseproxy)+' ')
univerindex = random.randint(0, len(val['univer_url'])-1)
COMMON_headers = {
            'Host': 'www.zhihu.com',
            'User-Agent': theusingua
        }

"""
工具包
"""

# 设置文件在setting.json
# 注意：代理设置的格式为 ip:port ，例如： "123.123.123.123:8080"
# 如果不想使用代理，请将proxy的值设为"No"
# 请使用HTTP代理，其他格式的代理将无法被识别
#trueheadnum=random.randint(0,len(allheaders)-1)
def get_links(session, url, proxy = chooseproxy):
    """
    Receive a url, and return a BeautifulSoup object
    """

    try:
        getheaders=COMMON_headers
        getheaders['Referer'] = 'https://www.zhihu.com/'
        getheaders['Connection'] = 'keep-alive'
        getheaders['Upgrade-Insecure-Requests'] = '1'
        trueresp=transbr(session, 'get', url, getheaders, chooseproxy)
        #html = session.get(url, proxies=proxy, headers=getheaders)
        #print(html.text)
        soup = BeautifulSoup(trueresp, 'lxml')
        with open('../temp.txt', 'wt', encoding='utf-8') as tempsoup:
            tempsoup.writelines(str(soup.prettify()))
        print("get soup successfully\n")
        #print(soup.prettify())
        return soup
    except URLRequired:
        print("URLRequired")
        return None
    except HTTPError:
        print("HTTPError")


def mypost(session, url, params, proxy=chooseproxy):
    """
    Receive a url, and return a BeautifulSoup object
    """

    extracookie = session.cookies
    dictcookie = requests.utils.dict_from_cookiejar(extracookie)
    print(dictcookie)
    # session.headers=postheaders
    #postheaders['Cookie'] = str(extracookie)
    postheaders = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip,deflate,br',
        'Accept-Language': 'en-US,en;q=0.5', #'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'Content-Length': '26',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Host': 'www.zhihu.com',
        'Referer':url,
        'TE':'Trailers',
        'User-Agent': theusingua,
        'X-Requested-With': 'XMLHttpRequest',
        'X-Xsrftoken': dictcookie['_xsrf']
    }
    try:
        trueresp=transbr(session, 'post', url, postheaders, chooseproxy, params)
        soup = BeautifulSoup(trueresp, 'lxml')
        with open('../temp.txt', 'wt', encoding='utf-8') as tempsoup:
            tempsoup.writelines(str(soup.prettify()))
        print("get soup successfully\n")
        return soup
    except URLRequired:
        print("URLRequired")
        return None
    except HTTPError:
        print("HTTPError")


def transbr(session, method, url, trueheaders, proxy, params=None):
    try:
        if method == 'get':
            response = session.get(url, headers=trueheaders, proxies=proxy)
        elif method == 'post':
            response = session.post(url, data=params, headers=trueheaders, proxies=proxy)
        if response.status_code == 200:
            key = 'Content-Encoding'
            if response.headers is not None:
                print(str(response.headers['content-encoding']))
            if (key in response.headers and response.headers['Content-Encoding'] == 'br'):
                data = brotli.decompress(response.content)
                #print(data)
                if ('\\u' in str(data)) and ('<meta charSet="utf-8"'not in str(data)):
                    print("unicode")
                    datatrue = data.decode('unicode-escape')
                elif ('\\u' not in str(data)) and ('<meta charSet="utf-8"' in str(data)):
                    print('utf-8')
                    datatrue = data.decode('utf-8')
                #print(datatrue)
                print('i am in br')
                return datatrue
            return response.text
        return None
    except RequestException as e:
        return None
