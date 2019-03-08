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
import random
import datetime
import utils
import requests
import json
import re
import time
from bs4 import BeautifulSoup
import Conndb

# 加载设置
val = json.load(open("setting.json"))

# 初始化随机数种子
random.seed(datetime.datetime.now())

# 保存Cookies
session=requests.session()




print(session)


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
    myself_soup = utils.get_links(session, val['account_url'])
    with open('../temp.txt', 'rt', encoding='utf-8') as temp:
        with open('../accoutpage.txt', 'wt',encoding='utf-8') as accoutp:
            accoutp.truncate()
            accoutp.write(temp.read())
    print(myself_soup)
    myidrule = re.compile(r'(?<=people","id":")[0-9a-z]+')
    myid = re.search(myidrule, str(myself_soup))
    my_id = myid.group(0)
    print("\n\nmy_id is "+my_id)
    return "https://www.zhihu.com/people/" + my_id

def get_mainpage_url():
    mainpage_url = val['mainpage_url']
    return mainpage_url
def get_entrance_url(index):
    entrance_url = val['univer_url'][index]
    return entrance_url

def get_followees(user_url,session):
    """
    获取一个用户的关注列表，如果关注人数很多，网站只会显示部分，其余的部分会AJAX动态刷新。我们只抓取初始的那部分。
    """
    user_followees_url = user_url + "/following"
    print(user_followees_url)
    followees_list = []
    followees_soup = utils.get_links(session, user_followees_url)
    temp=open("../following.txt", 'w', encoding='utf-8')
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
        crawl(one, session)
    except NoFolloweeError:
        next_random_url = conn.srandmember("UrlSet", 1)[0].decode("utf-8")
        crawl(next_random_url, session)

def crawlmainpage(url,session):
    print("entering crawl mainpage")
    mainpage_soup=utils.get_links(session,url)
    #print(mainpage_soup)
    #print('\n')
    mainpage_soup_str = str(mainpage_soup)
    with open('../mainpage.txt', 'wt', encoding='utf-8') as main:
        main.write(mainpage_soup_str)
    firstrule=re.compile(r'https:\\u002F\\u002Fapi.zhihu.com\\u002Fquestions\\u002F[0-9]+')
    firstmatch=re.findall(firstrule, mainpage_soup_str)


def crawlentpage(url, session):
    print("entering crawl entpage\n")
    myrule = re.compile(r'<a class=\"zu-top-nav-userinfo\" href=\"\/people\/(.*?)\">')
    followerrule = re.compile(r'<a class=\"zg-link author-link\" href=\"\/people\/(.*?)\">')
    nextfollowerrule=re.compile(r'<a class=\"zg-link author-link\" href=\"\\/people\\/(.*?)\">')
    ppidrule = re.compile(r'(?<=id="pp-)[0-9a-z]+')
    entpage_soup = utils.get_links(session, url)
    entpage_soup_str = str(entpage_soup)

    mymatch = re.findall(myrule, entpage_soup_str)

    followermatch = re.findall(followerrule, entpage_soup_str)
    ppidmatch=re.findall(ppidrule, entpage_soup_str)
    cirnum = 0
    while cirnum < len(followermatch):
        try:
            Conndb.connectdb(utils.prival['mongodbnet']['host'], utils.prival['mongodbnet']['port'], val['dbnamenet'], val['colnamenet'],followermatch[cirnum],ppidmatch[cirnum])
        except OSError as ee:
            print("{0}".format(ee))
        cirnum = cirnum+1
    print('\nmy Domainhack is' + str(mymatch)+'\n')
    print('\nthe followers\' Domainhacks are' + str(followermatch)+'\n')
    print('while their ppid are ' + str(ppidmatch) + '\n')
    if len(followermatch) < 20:
        return
    lastonerule=re.compile(r'(?<=mi-)[0-9]+')
    allstart = re.findall(lastonerule, entpage_soup_str)
    try:
        truestart = allstart[len(allstart) - 1]
        lasttruestart = truestart
    except IndexError as ie:
        print("{0}".format(ie))
        return
    print('\nthe truestart is: '+truestart)
    time.sleep(random.randint(5, 10))
    postnum = 0
    while postnum >= 0: #utils.prival['flippagenum']:
        offsetnum = 40+postnum*20
        startnum = truestart
        print('offsetnum= '+str(offsetnum)+' startnum= '+str(startnum))
        params = {"offset": str(offsetnum), "start": str(startnum)}
        #params = 'offset='+str(offsetnum)+'&start='+startnum
        nextentpage_soup = utils.mypost(session, url, params)
        nextentpage_soup_str=str(nextentpage_soup)
        nextfollowermatch=re.findall(nextfollowerrule,nextentpage_soup_str)
        ppidmatch = re.findall(ppidrule, entpage_soup_str)
        cirnum = 0
        while cirnum < len(nextfollowermatch):
            try:
                Conndb.connectdb(utils.prival['mongodbnet']['host'], utils.prival['mongodbnet']['port'], val['dbnamenet'], val['colnamenet'], nextfollowermatch[cirnum], ppidmatch[cirnum])
            except OSError as ee:
                print("{0}".format(ee))
            cirnum = cirnum + 1
        print('\nthe followers\' Domainhacks are' + str(nextfollowermatch) + '\n')
        print('while their ppid are '+str(ppidmatch)+'\n')
        if len(nextfollowermatch) < 20:
            return
        postnum = postnum+1
        lastonerule = re.compile(r'(?<=mi-)[0-9]+')
        wholestart = re.findall(lastonerule, nextentpage_soup_str)
        if len(wholestart) > 0:
            truestart = wholestart[len(wholestart)-1]
            if truestart == lasttruestart:
                return
            lasttruestart = truestart
            print('\nthe truestart is: ' + truestart)
        else:
            print('not found next start')
            return
        time.sleep(random.randint(5, 10))
def main_from_me(session):
    my_url = get_my_url(session)
    crawl(my_url,session)

def main_from_enter(session):
    """
    主程序，以自己的主页为起点，开始抓取。
    """
    entrance_url=get_entrance_url(utils.univerindex)
    crawlentpage(entrance_url,session)
def main_from_one(session,start_url):
    """
    以给定的主页为起点，开始抓取。如果程序因为某些原因中断的话，可以记录下最后一个URL，下一次再运行的时候可以从此处继续。
    """
    crawl(start_url,session)

if __name__ == "__main__":
    load_cookies=True
    whether, session = zhihu_login.ZhihuAccount().login('en', load_cookies)
    print('login '+str(whether) + ' '+str(session))
    #main_from_me(session)
    main_from_enter(session)
    print(str(utils.theusingua))
    print('the proxy which was chosed is '+str(utils.chooseproxy))
    print('the first chosed is '+str(val['univer_name'][utils.univerindex])+' : '+str(val['univer_url'][utils.univerindex]))
    print('flipping '+str(utils.prival['flippagenum'])+' pages')
