import os
import sys
import re
#from fake_useragent import UserAgent
from mock_useragent import MockUserAgent
import requests
import time
import random
import brotli
import json
def forgeua():
    ua = MockUserAgent()
    browverrule = re.compile(r'(?<=Chrome/)[0-9]{2}')
    while True:
        theusingua = ua.random_chrome
        browver = re.search(browverrule, str(theusingua))
        try:
            if int(browver.group(0)) > 33:
                break
        except AttributeError:
            continue
    print(theusingua)
    return theusingua

if __name__ == "__main__":
    originurl = 'www.zhihu.com'
    wwwheaders = {
        # 'Accept': '*/*',
        'Accept-Encoding': 'gzip,deflate,br',
        # 'Accept-Language': 'en-US,en;q=0.5', #'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        # 'Connection': 'keep-alive',
        # 'Content-Length': '26',
        # 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Host': originurl,
        # 'Referer':url,
        # 'TE':'Trailers',
        'User-Agent': forgeua()
        # 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36 Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10'#forgeua(),
        # 'X-Requested-With': 'XMLHttpRequest',
        # 'X-Xsrftoken': dictcookie['_xsrf']
    }
    with open('../private.json', 'rt+', encoding='utf-8') as readurl:
        all = json.load(readurl)
        print(all)
    try:
        targetname = all['target_name']
    except KeyError:
        with open('../private.json', 'wt+', encoding='utf-8') as addurl:
            addurl.writelines((json.dumps(({**all, **{'target_name': None}}), ensure_ascii=False, indent=1)))
    with open('../private.json', 'rt+', encoding='utf-8') as readurl:
        all = json.load(readurl)
        print(all)
    # try:
    #     searchobjlist = all['target_url']
    # except KeyError:
    if True:
        allsearchobj = all['target_name']
        #print(allsearchobj)
        allfollowersurl=[]
        if type(allsearchobj) is list:
            for searchobj in allsearchobj:
                print(searchobj)
                resp0 = requests.get('https://www.zhihu.com/search?type=content&q='+searchobj, headers=wwwheaders)
                #print(resp0.headers)
                print(str(resp0.headers['content-type']))
                charsetrule =re.compile(r'(?<=charset=)[0-9A-Za-z\-_]+')
                resp0charset = re.search(charsetrule, str(resp0.headers['content-type']))
                print(resp0charset.group(0))
                data0 = brotli.decompress(resp0.content)
                resp0deco=data0.decode(resp0charset.group(0))
                rule = re.compile(r'/topic/[0-9]+')
                respsearch=re.search(rule, resp0deco)
                try:
                    print(respsearch.group())
                except AttributeError:
                    break
                time.sleep(random.randint(1, 5))
                topicurl = 'https://'+originurl+str(respsearch.group())
                followersurl = topicurl+'/followers'
                print(followersurl)
                time.sleep(random.randint(1, 5))
                resp1 = requests.get(topicurl, headers=wwwheaders)
                resp1charset = re.search(charsetrule, str(resp1.headers['content-type']))
                print(resp1charset.group(0))
                allfollowersurl.append(followersurl)
            if respsearch is None:
                print('the topic url your search is not exist, please modify it then restart the program')
            else:
                with open('../private.json', 'wt+', encoding='utf-8') as addurl:
                    addurl.writelines((json.dumps(({**all, **{'target_url': allfollowersurl}}), ensure_ascii=False, indent=1)))
        #print(resp1.headers['Content-Encoding'])


    # time.sleep(random.randint(1, 5))
    # data1 = brotli.decompress(resp1.content)
    # resp1deco = data1.decode(resp1charset.group(0))
    # print(resp1deco)
    #print(resp1deco)
    #print(resp1.content.decode('utf-8'))