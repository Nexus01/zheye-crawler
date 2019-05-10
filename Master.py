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
import os
import sys
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
import pymongo
import os
import sys
import brotli
syspath = sys.path[0]
os.chdir(sys.path[0])
# 加载设置
val = json.load(open("setting.json", encoding='utf-8'))
valprivate = json.load(open('../private.json', encoding='utf-8'))
# 初始化随机数种子
random.seed(datetime.datetime.now())

# 保存Cookies
session = requests.session()




print(session)

def insertdomainid(client, dbname, colname, domain, id, fromwhere):
    #远程服务器的IP和端口
    mydb = client[dbname] #database
    mycol = mydb[colname] #collection
    setvalue = {'ppid': id, 'fromwhere': fromwhere}
    #result = mycol.find_one({'ppid': id})
    # if result:
    #     mycol.update({'ppid': id},{'domain': domain, 'ppid': id, "fromwhere": fromwhere})#更新数据
    # else:
    #     mycol.insert_one(mylist)
    mycol.update_one({'url': domain}, {'$set': setvalue}, upsert=True)
    return

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
    # with open('../temp.txt', 'rt', encoding='utf-8') as temp:
    #     with open('../accoutpage.txt', 'wt',encoding='utf-8') as accoutp:
    #         accoutp.truncate()
    #         accoutp.write(temp.read())
    print(myself_soup)
    myidrule = re.compile(r'(?<=people","id":")[0-9a-z]+')
    myid = re.search(myidrule, str(myself_soup))
    try:
        my_id = myid.group(0)
    except AttributeError as ae:
        return False
    print("\n\nmy_id is "+my_id)
    return "https://www.zhihu.com/people/" + my_id

def get_mainpage_url():
    mainpage_url = val['mainpage_url']
    return mainpage_url
def get_entrance_url(index):
    try:
        entrance_url = valprivate['target_url'][index]
    except KeyError:
        entrance_url = val['target_url'][index]
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
    mainpage_soup = utils.get_links(session, url)
    #print(mainpage_soup)
    #print('\n')
    mainpage_soup_str = str(mainpage_soup)
    with open('../mainpage.txt', 'wt', encoding='utf-8') as main:
        main.write(mainpage_soup_str)
    firstrule = re.compile(r'https:\\u002F\\u002Fapi.zhihu.com\\u002Fquestions\\u002F[0-9]+')
    firstmatch = re.findall(firstrule, mainpage_soup_str)


def crawlentpage(url, session , fromwhere):
    print("entering crawl entpage\n")
    myrule = re.compile(r'<a class=\"zu-top-nav-userinfo\" href=\"\/people\/(.*?)\">')
    followerrule = re.compile(r'<a class=\"zg-link author-link\" href=\"\/people\/(.*?)\">')
    nextfollowerrule = re.compile(r'<a class=\"zg-link author-link\" href=\"\\/people\\/(.*?)\">')
    ppidrule = re.compile(r'(?<=id="pp-)[0-9a-z]+')
    entpage_soup = utils.get_links(session, url)
    entpage_soup_str = str(entpage_soup)

    mymatch = re.findall(myrule, entpage_soup_str)

    followermatch = re.findall(followerrule, entpage_soup_str)
    ppidmatch=re.findall(ppidrule, entpage_soup_str)
    cirnum = 0
    ip = utils.prival['mongodbnet']['host']
    port = utils.prival['mongodbnet']['port']
    remoteclient = pymongo.MongoClient(str(ip) + ":" + str(port))
    while cirnum < len(followermatch):
        try:
            insertdomainid(remoteclient, val['dbnamenet'], val['colnamenet'], followermatch[cirnum], ppidmatch[cirnum], fromwhere)
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
        print('offsetnum='+str(offsetnum)+' startnum='+str(startnum))
        params = {"offset": str(offsetnum), "start": str(startnum)}
        #params = 'offset='+str(offsetnum)+'&start='+startnum
        #whether, session = zhihu_login.ZhihuAccount(zhihu_login.acc, zhihu_login.sec).login('en', load_cookies)
        nextentpage_soup = utils.mypost(session, url, params)
        try:
            nextentpage_soup_str = str(nextentpage_soup.prettify().encode('latin-1').decode('unicode_escape'))
            if '\"errcode\": 1991832' in nextentpage_soup_str:
                print(nextentpage_soup_str)
                print('please change your account whose status is normal')
        except UnicodeEncodeError:
            nextentpage_soup_str = str(nextentpage_soup)
        nextfollowermatch=re.findall(nextfollowerrule, nextentpage_soup_str)
        ppidmatch = re.findall(ppidrule, nextentpage_soup_str)
        cirnum = 0
        while cirnum < len(nextfollowermatch):
            try:
                insertdomainid(remoteclient, val['dbnamenet'], val['colnamenet'], nextfollowermatch[cirnum], ppidmatch[cirnum], fromwhere)#,val['univer_name'][num_url])
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
                print('flipping ' + str(postnum) + ' pages')
                return
            lasttruestart = truestart
            print('\nthe truestart is: ' + truestart)
        else:
            print('not found next start')
            print('flipping ' + str(postnum) + ' pages')
            return
        time.sleep(random.randint(10, 15))
def main_from_me(session):
    my_url = get_my_url(session)
    #if my_url == False:
        #restart_program()
        #utils.theusingua = utils.ua.random
        #main_from_me(session)
    crawl(my_url,session)

def main_from_enter(session, num, fromwhere):

    entrance_url = get_entrance_url(num)
    crawlentpage(entrance_url, session, fromwhere)
def main_from_one(session,start_url):
    """
    以给定的主页为起点，开始抓取。如果程序因为某些原因中断的话，可以记录下最后一个URL，下一次再运行的时候可以从此处继续。
    """
    crawl(start_url,session)

def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)

if __name__ == "__main__":
    isold = input('Would you like to use the last login cookies? (yes/no)Default=yes\n')
    if 'n' in isold:
        load_cookies = False
        whether, session = zhihu_login.ZhihuAccount('', '').login('en', load_cookies)
    else:
        load_cookies = True
        whether, session = zhihu_login.ZhihuAccount('', '').login('en', load_cookies)
    print('login ' + str(whether) + ' ' + str(session))
    #main_from_me(session)
    try:
        targetname = valprivate['target_name']
    except KeyError:
        targetname = val['target_name']
    num_url = 0
    while num_url < utils.targetindex:
        main_from_enter(session, num_url, targetname[num_url])
        print(str(utils.theusingua))
        print('the proxy which was chosed is '+str(utils.chooseproxy))
        try:
            print('the chosed is '+str(valprivate['target_name'][num_url])+' : '+str(valprivate['target_url'][num_url]))
        except KeyError:
            print('the chosed is '+str(val['target_name'][num_url])+' : '+str(val['target_url'][num_url]))
        num_url = num_url + 1
