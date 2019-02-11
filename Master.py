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

from Error import NoFolloweeError
import zhihu_login
import redis
import random
import datetime
import utils
import requests
import json
import re
from retrying import retry

# 加载设置
val = json.load(open("setting.json"))

# 初始化随机数种子
random.seed(datetime.datetime.now())

# 保存Cookies
session=requests.session()




print(session)
# 连接至Redis
conn = redis.Redis(host=val['redis']['host'], port=val['redis']['port'])


def put_into_queue(info_list):
    """
    构造一个set，负责去重。info_list内的内容如果不在集合内，就压入任务队列，否则舍去。
    """
    for info in info_list:
        flag = conn.sadd("UrlSet", info)
        if flag:
            conn.rpush("UrlQueue", info)


def get_next_url(url_list):
    """
    从url_list内随机抽取出一个url返回。
    """
    next_index = random.randint(0, len(url_list) - 1)
    next_url = url_list[next_index]
    return next_url


def get_my_url(session):
    """
    获取自己的主页作为起始也页面返回。
    """
    myself_soup = utils.get_links(
       session, "https://www.zhihu.com/settings/account")
    temp=open("temp.txt",'r+')
    accountpage = open("accountpage.txt", "w",encoding='utf-8')
    accountpage = open("accountpage.txt", "r+",encoding='utf-8')
    accountpage.truncate()
    accountpage.write(temp.read())
    temp.close()
    accountpage.close()

    thehref = re.compile(r"zhihu\.com\/people\/*")

    my_url = myself_soup.find(
        text=thehref)

    print("\n\nmy_url is "+my_url)
    return "https://www." + my_url

def get_mainpage_url():
    mainpage_url='https://www.zhihu.com/'
    return  mainpage_url
def get_entrance_url():
    entrance_url = 'https://www.zhihu.com/topic/19588914/followers'
    return entrance_url

def get_followees(user_url,session):
    """
    获取一个用户的关注列表，如果关注人数很多，网站只会显示部分，其余的部分会AJAX动态刷新。我们只抓取初始的那部分。
    """
    user_followees_url = user_url + "/following"
    print(user_followees_url)
    followees_list = []
    followees_soup = utils.get_links(session, user_followees_url)
    temp=open("following.txt",'w',encoding='utf-8')
    temp.write(str(followees_soup.prettify()))
    temp.close()
    for i in followees_soup.find_all("a", {"class": "UserLink-link","data-za-detail-view-element_name":"User"}):
        print("this is i "+i.get('href'))

        followee_url = "http:"+i.get('href')
#remove lots of unvaild varieties
        if followee_url not in followees_list:
            followees_list.append(followee_url)
    if followees_list:
        return followees_list
    raise NoFolloweeError


def crawl(url,session):
    """
    广度优先，执行抓取，如果抛出NoFolloweeError错误，就从UrlSet中随机选一个网址进行抓取。
    """
    print("entering crawl")
    followees = get_followees(url,session)
    print(str(followees))
    one = get_next_url(followees)
    try:
        test_list = get_followees(one,session)
        put_into_queue(followees)
        print(one)
        crawl(one,session)
    except NoFolloweeError:
        next_random_url = conn.srandmember("UrlSet", 1)[0].decode("utf-8")
        crawl(next_random_url,session)

def crawlmainpage(url,session):
    print("entering crawl mainpage")
    mainpage_soup=utils.get_links(session,url)
    #print(mainpage_soup)
    #print('\n')
    mainpage_soup_str = str(mainpage_soup)
    #encode_type = chardet.detect(mainpage_soup_str)
    #mainpage_soup_str = mainpage_soup_str.decode(encode_type['encoding'])  # 进行相应解码，赋给原标识符（变量）
    #mainpage_soup_str = str(mainpage_soup).replace(r'\u002F',r'/')
#https:\u002F\u002Fwww.zhihu.com\u002Fquestion\u002F
    #print(mainpage_soup_str)
    firstrule=re.compile(r'https:\\u002F\\u002Fapi.zhihu.com\\u002Fquestions\\u002F[0-9]+')
    firstmatch=re.findall(firstrule,mainpage_soup_str)
    print('\n'+str(firstmatch).replace('\\\\u002F','/'))
    #return firstmatch


def crawlentpage(url, session):
    print("entering crawl entpage\n")
    entpage_soup = utils.get_links(session, url)
    entpage_soup_str = str(entpage_soup)
    with open('enterpage.txt','wt',encoding='utf-8') as ent:
        ent.write(entpage_soup_str)
    #print(entpage_soup_str+'\n')
    nextrule = re.compile(r'\/people\/*')
    #nextmatch = re.findall(nextrule, entpage_soup_str)
    nextmatch=entpage_soup.find(text=nextrule)
    print('\n' + str(nextmatch).replace('\\\\u002F', '/'))

#@retry
def main_from_me():
    """
    主程序，以自己的主页为起点，开始抓取。
    """
    #print(val['account'],val['secret'])
    #account = input('Please input your account\n>  ')
    #secret = input("input your secret\n>  ")
    load_cookies=True
    attempts = 0
    trytime  = 5
    success = False
    while attempts < trytime and not success:
        try:
            whether,session = zhihu_login.ZhihuAccount().login(val['account'], val['secret'],load_cookies)  # remove captcha_lang='cn' in the argument
            success = True
        except:
            attempts += 1
            if attempts == trytime:
                break
    #whether,session=zhihu_login.ZhihuAccount().login(val['account'],val['secret'],load_cookies) #remove captcha_lang='cn' in the argument
    print(str(attempts) + '\n')
    print(str(success)+'\n')
    print(str(session))
    #my_url = get_my_url(session)
    #crawl(my_url,session)
    mainpage_url=get_mainpage_url()
    entrance_url=get_entrance_url()
    crawlmainpage(mainpage_url,session)
    crawlentpage(entrance_url,session)


    print('UserAgent is '+str(utils.trueheadnum)+'\n')

#@retry
def main_from_one(start_url):
    """
    主程序，以给定的主页为起点，开始抓取。如果程序因为某些原因中断的话，可以记录下最后一个URL，下一次再运行的时候可以从此处继续。
    """
    #account = input('Please input your account\n>  ')
    #secret = input("input your secret\n>  ")
    load_cookies=True
    whether,session=zhihu_login.ZhihuAccount().login(val['account'],val['secret'], load_cookies) #remove captcha_lang='cn' in the argument as well
    crawl(start_url)

if __name__ == "__main__":
    main_from_me()
