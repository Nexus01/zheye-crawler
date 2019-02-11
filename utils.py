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
from requests import HTTPError, URLRequired
import random
"""
工具包
"""
allheaders = [
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.'},
        {'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'},
        {'User-Agent': 'Mozilla/5.0 (Linux; U; Android 2.2; en-gb; GT-P1000 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'},
        {'User-Agent': 'Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0'},
        {'User-Agent': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'},
        {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'},
        {'User-Agent': 'Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A101a Safari/419.3'}
    ]
# 设置文件在setting.json
# 注意：代理设置的格式为 ip:port ，例如： "123.123.123.123:8080"
# 如果不想使用代理，请将proxy的值设为"No"
# 请使用HTTP代理，其他格式的代理将无法被识别
trueheadnum=random.randint(0,len(allheaders)-1)
def get_links(session, url, proxy = None):
    """
    Receive a url, and return a BeautifulSoup object
    """

    try:
        html = session.get(url, proxies = proxy, headers=allheaders[trueheadnum])
        #print(html.text)
        soup = BeautifulSoup(html.text, 'lxml')
        tempsoup = open("temp.txt", "w",encoding='utf-8')
        tempsoup.writelines(str(soup.prettify()))
        tempsoup.close()
        print("get soup successfully\n")
        #print(soup.prettify())
        return soup
    except URLRequired:
        print("URLRequired")
        return None
    except HTTPError:
        print("HTTPError")


    
