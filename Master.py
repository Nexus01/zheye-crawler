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

# 加载设置
val = json.load(open("setting.json"))

# 初始化随机数种子
random.seed(datetime.datetime.now())
#requests.
# 保存Cookies
session=requests.session()
#session = zhihu_login.ZhihuAccount(captcha_lang='en').session.cookies
#session = open("cookies.txt", "r").read()



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
    #print(str(session))
    myself_soup = utils.get_links(
       session, "https://www.zhihu.com/settings/account")
    """     my_url = myself_soup.find(
        "div", {"id": "js-url-preview", "class": "url-preview"}) """
    #thehref=re.compile(r"([\s\S]*?("https://www.zhihu.com/people/")[\s\S]*?)\")
    temp=open("temp.txt",'r+')
    accountpage = open("accountpage.txt", "w")
    accountpage = open("accountpage.txt", "r+")
    accountpage.truncate()
    accountpage.write(temp.read())
    temp.close()
    accountpage.close()
    #thehref=re.compile(r"^zhihu\.com\/people\/([/\w \.-]*)*/?$")
    thehref = re.compile(r"zhihu\.com\/people\/*")
    #thehref="zhihu.com/people/ryzendog"
    #print(myself_soup)
    #tempsoup=open("temp.txt","w")
    #tempsoup.writelines(str(utils.html.text))
    #tempsoup.close()


    #my_url = myself_soup.find(
        #"a",{"href":"zhihu.com/people/ryzendog","type":"button","class":"Button Menu-item AppHeaderProfileMenu-item Button--plain"})
    my_url = myself_soup.find(
        text=thehref)
        #text="zhihu.com/people/ryzendog")
        #"div",{"href":"zhihu.com/people/ryzendog"})
    """     if my_url is None:
        return    
    else:  """
    print("\n\nmy_url is "+my_url)
    return "https://www." + my_url


def get_followees(user_url,session):
    """
    获取一个用户的关注列表，如果关注人数很多，网站只会显示部分，其余的部分会AJAX动态刷新。我们只抓取初始的那部分。
    """
    user_followees_url = user_url + "/following"
    print(user_followees_url)
    followees_list = []
    followees_soup = utils.get_links(session, user_followees_url)
    temp=open("following.txt",'w')
    temp.write(str(followees_soup.prettify()))
    temp.close()
    for i in followees_soup.find_all("a", {"class": "UserLink-link","data-za-detail-view-element_name":"User"}):
        print("this is i "+i.get('href'))
        #followinghref = re.compile("\/\/www\.zhihu\.com\/people\/excited-vczh")
        #followee_url = i.find(href=followinghref)
        followee_url = "http:"+i.get('href')
        #followee_url=i.get('href').replace("//","")
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


def main_from_me():
    """
    主程序，以自己的主页为起点，开始抓取。
    """
    #print(val['account'],val['secret'])
    account = input('Please input your account\n>  ')
    secret = input("input your secret\n>  ")
    load_cookies=True
    whether,session=zhihu_login.ZhihuAccount(captcha_lang='en').login(val['account'],val['secret'],load_cookies)
    print(str(session))
    my_url = get_my_url(session)
    crawl(my_url,session)


def main_from_one(start_url):
    """
    主程序，以给定的主页为起点，开始抓取。如果程序因为某些原因中断的话，可以记录下最后一个URL，下一次再运行的时候可以从此处继续。
    """
    account = input('Please input your account\n>  ')
    secret = input("input your secret\n>  ")
    load_cookies=True
    whether,session=zhihu_login.ZhihuAccount(captcha_lang='en').login(val['account'],val['secret'], load_cookies)
    crawl(start_url)

if __name__ == "__main__":
    main_from_me()
