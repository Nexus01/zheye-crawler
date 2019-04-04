from Error import NoFolloweeError
import random
import datetime
import urllib
import requests
import json
import re
import time
from bs4 import BeautifulSoup
import pymongo
import os
import json
from fake_useragent import UserAgent
import sys
import zhihu_login
lightout = False
threshold = 25


def forgeua():
    ua = UserAgent()
    browverrule = re.compile(r'(?<=Chrome/)[0-9]{2}')
    while True:
        theusingua = ua.chrome
        browver = re.search(browverrule, str(theusingua))
        if int(browver.group(0)) > 33:
            break
    print(theusingua)
    return theusingua


def owndelete(thevalue, valuename, *ipport):
    if len(ipport) == 2:
        myclient = pymongo.MongoClient('mongodb://' + ipport[0] + ':' + ipport[1] + '/')
    else:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient['zhihu']  # shujuku
    mycol = mydb[valuename]  # jihe
    myquery = {valuename: thevalue}
    mycol.delete_one(myquery)

def ownremove(thevalue,valuename, *ipport):
    if len(ipport) == 2:
        myclient = pymongo.MongoClient('mongodb://' + ipport[0] + ':' + ipport[1] + '/')
    else:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient['zhihu']  # shujuku
    mycol = mydb[valuename]  # jihe
    myquery = {valuename: thevalue}
    mycol.delete_many(myquery)

def checktime(begintime,endtime):
    timeinrange = False
    # 范围时间
    d_time = datetime.datetime.strptime(str(datetime.datetime.now().date())+str(begintime), '%Y-%m-%d%H:%M')
    d_time1 =  datetime.datetime.strptime(str(datetime.datetime.now().date())+str(endtime), '%Y-%m-%d%H:%M')
    # 当前时间
    n_time = datetime.datetime.now()
    # 判断当前时间是否在范围时间内
    if n_time > d_time and n_time<d_time1:
        timeinrange = True
    return timeinrange

def chooseproxy(proxypath):
    if checktime('22:55','23:05'):
        chosedproxy = None
    else:
        if proxypath == None:
            chosedproxy = None
        else:
            chosedproxy = proxypath[random.randint(0, len(proxypath) - 1)]
    print('The proxy chosed is ' + str(chosedproxy))
    return chosedproxy

def check(urltoken, *ipport):
    if len(ipport) == 2:
        myclient = pymongo.MongoClient('mongodb://' + ipport[0] + ':' + ipport[1] + '/')
    else:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient['zhihu']
    mycol = mydb['CrawledUrl']
    myquery = {'url': urltoken}
    mydoc = mycol.find(myquery)
    checkexist = {}
    for crawlingc in mydoc:
        checkexist.update(crawlingc)
    return checkexist

def checkcrawling(thekey,thevalue,*ipport):
    if len(ipport) == 2:
        myclient = pymongo.MongoClient('mongodb://' + ipport[0] + ':' + ipport[1] + '/')
    else:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient['zhihu']
    mycol = mydb['CrawlingUrl']
    myquery = {thekey: str(thevalue)}
    mydoc = mycol.find(myquery)
    checkc = {}
    for crawlingc in mydoc:
        checkc.update(crawlingc)
    return checkc

def checkcrawling2(thekey,thevalue,thekey2,thevalue2,*ipport):
    if len(ipport) == 2:
        myclient = pymongo.MongoClient('mongodb://' + ipport[0] + ':' + ipport[1] + '/')
    else:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient['zhihu']
    mycol = mydb['CrawlingUrl']
    myquery = {thekey: str(thevalue),thekey2:str(thevalue2)}
    mydoc = mycol.find(myquery)
    checkc = {}
    for crawlingc in mydoc:
        checkc.update(crawlingc)
    return checkc

def pickyu(ip, port):
    # 获取url的id
    myclient = pymongo.MongoClient('mongodb://' + ip + ':' + port + '/')  # 远程服务器的IP和端口
    mydb = myclient["zhihu"]  # shujuku
    mycol = mydb["NewUrl"]  # jihe
    betheone = (mycol.find_one())['url']
    return betheone
    # list = []
    # for y in mycol.find({}, {"_id": 0, "NewUrl": 1}):
    #     list.append(y)
    # return list


def Savedb(thekey, thevalue, keyname, valuename, *ipport):
    if len(ipport) == 2:
        myclient = pymongo.MongoClient('mongodb://' + ipport[0] + ':' + ipport[1] + '/')
    else:
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")  # 远程服务器的IP和端口
    mydb = myclient['zhihu']  # shujuku
    mycol = mydb[valuename]  # jihe
    setvalue = {valuename: thevalue}
    mycol.update_one({keyname: thekey}, {'$set': setvalue}, upsert=True)
    # db.NewUrl.updateOne({'NewUrl': 'luosheng'}, {'$set': {'url': 'luosheng'}}, upsert=true)
    return

def CrawlingNum(thekey, thevalue, keyname, valuename, ip, port):
    myclient = pymongo.MongoClient('mongodb://' + ip + ':' + port + '/')
    mydb = myclient['zhihu']  # shujuku
    mycol = mydb['CrawlingUrl']  # jihe
    setvalue = {valuename: thevalue}
    mycol.update_one({keyname: thekey}, {'$set': setvalue}, upsert=True)
    # db.NewUrl.updateOne({'NewUrl': 'luosheng'}, {'$set': {'url': 'luosheng'}}, upsert=true)
    return


def gettopics(url, fakeua, fullproxies, needcookies):
    global originua
    headers = {
        'Host': 'www.zhihu.com'
        #'User-Agent': forgeua()
    }
    realproxy = chooseproxy(fullproxies)
    while True:
        try:
            if fakeua:
                headers['User-Agent'] = forgeua()
            else:
                headers['User-Agent'] = originua
            resp = requests.get(
                'https://www.zhihu.com/api/v4/members/' + url + '/following-topic-contributions?include=data[*].topic.introduction&offset=0&limit=100',
                headers=headers, proxies=realproxy, cookies=needcookies)
            break
        except requests.exceptions.ConnectionError:
            realproxy = None
            continue
    print(str(resp.headers['content-type']))
    valtopics = json.loads(resp.content)
    totals = valtopics['paging']
    # print(totals)
    info = re.compile(r'\'totals\': (.*?),')
    totals = re.findall(info, str(totals))
    totals = str(totals).strip('[\']')
    totals = int(totals)
    # print(valtopics)
    topic_list = []
    num_list = []
    offset = 0
    while totals > 0:
        # headers['User-Agent'] = forgeua()
        # realproxy = chooseproxy(fullproxies)
        time.sleep(random.randint(5, 10))
        while True:
            try:
                if fakeua:
                    headers['User-Agent'] = forgeua()
                else:
                    headers['User-Agent'] = originua
                resp = requests.get(
                    'https://www.zhihu.com/api/v4/members/' + url + '/following-topic-contributions?include=data[*].topic.introduction&offset=' + str(
                        offset) + '&limit=100', headers=headers, proxies=realproxy, cookies = needcookies)
                break
            except requests.exceptions.ConnectionError:
                realproxy = None
                continue
        valapitopics = json.loads(resp.content)
        data = valapitopics['data']
        # print(data)
        info1 = re.compile(r'\'name\': \'(.*?)\'')
        info2 = re.compile(r'\'contributions_count\': (.*?)}')
        topic = re.findall(info1, str(data))
        num = re.findall(info2, str(data))
        for i in topic:
            topic_list.append(i)
        for i in num:
            num_list.append(i)
        offset += 20
        totals -= 20

    print(topic_list)
    print(num_list)
    topics = dict(map(lambda x, y: [x, y], topic_list, num_list))
    Savedb(url, topics, 'url', 'topics')


def getfollowing(url, fakeua, fullproxies, needcookies, *ipport):
    global originua
    if len(ipport) == 2:
        remoteip = ipport[0]
        remoteport = ipport[1]
    else:
        remoteip = '127.1'
        remoteport = '27017'
    headers = {
        'Host': 'www.zhihu.com',
        #'User-Agent': forgeua(),
        'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, * / *;q = 0.8',
        'Accept - Language': 'en - US, en;q = 0.5',
        'Upgrade - Insecure - Requests': '1',
        'Cache - Control': 'max - age = 0'
    }
    realproxy = chooseproxy(fullproxies)
    user_following_url = "https://www.zhihu.com/people/" + url + "/following"
    print(user_following_url)

    while True:
        try:
            if fakeua:
                headers['User-Agent'] = forgeua()
            else:
                headers['User-Agent'] = originua
            response = requests.get(user_following_url, headers=headers, proxies=realproxy, cookies=needcookies)
            break
        except requests.exceptions.ConnectionError:
            realproxy = None
            continue
    # print(response.t(thekey,thevalue,*ipport)ext)
    next = response.text.replace(r'\u002F', r'/')
    # print(next)
    if 'ProfileMainPrivacy-mainContentText' not in next:
        if 'ProfileLockStatus-title' not in next:
            url_list_number = re.compile(r'Button PaginationButton Button--plain">([0-9]+)</button>')
            # info = re.findall(follower_url,next)
            # print(url_list_number)
            number_info = re.findall(url_list_number, next)
            print(number_info)
            try:
                number_info = number_info[-1]
            except IndexError as index:
                print(index)
                number_info = 1
            # print(number_info)
            # print(next)
            try:
                number_info = int(number_info)
            except ValueError:
                number_info = 1
            print(str(number_info))
            if number_info > threshold:
                Savedb(url, url, 'url', 'NextUrl', remoteip, remoteport)
                ownremove(url, 'CrawlingUrl', remoteip, remoteport)
                return False
            # print(info)
            CrawlingNum(url, 'following', 'url', 'pagetype', netip, netport)
            try:
                nowpage = checkcrawling('url', url, netip, netport)['pagenum']
                url_number = int(nowpage)
            except KeyError:
                url_number = 1
            while url_number <= number_info:
                print('following page: '+str(url_number))
                CrawlingNum(url, str(url_number), 'url', 'pagenum', netip, netport)
                if lightout:
                    if checktime('22:30', '23:59'):
                        sys.exit(0)
                user_following_url = "https://www.zhihu.com/people/" + url + "/following?page=" + str(url_number)
                # headers['User-Agent'] = forgeua()
                time.sleep(random.randint(5, 10))
                while True:
                    try:
                        if fakeua:
                            headers['User-Agent'] = forgeua()
                        else:
                            headers['User-Agent'] = originua
                        response = requests.get(user_following_url, headers=headers, proxies=realproxy, cookies=needcookies )
                        break
                    except requests.exceptions.ConnectionError:
                        realproxy = None
                        continue
                next = response.text.replace(r'\u002F', r'/')
                # print(next)
                following_url = re.compile(r'\"urlToken\":\"([0-9a-zA-Z\-_]+)\",\"id\":\"')
                info = re.findall(following_url, next)
                # del info[0]
                newurl_id_list = []
                for i in info:
                    if i:
                        mydoc = check(i, remoteip, remoteport)  # 要改
                        if not mydoc:
                            # user_following_url = "https://www.zhihu.com/people/" + i
                            # headers['User-Agent'] = forgeua()
                            # time.sleep(random.randint(1, 5))
                            # response = requests.get(user_following_url, headers=headers)
                            # next = response.text.replace(r'\u002F', r'/')
                            # if 'ProfileMainPrivacy-mainContentText' not in next:
                            # if 'ProfileLockStatus-title' not in next:
                            # following_url = re.compile(r'\",\"urlToken\":\"(.*?)\",\"name\":\"')
                            # token_info = re.findall(following_url, next)
                            # i = token_info
                            i = str(i).strip('[\']')
                            #print(i)
                            while True:
                                try:
                                    Savedb(i, i, 'url', 'NewUrl', remoteip, remoteport)
                                    break
                                except pymongo.errors.NetworkTimeout or pymongo.errors.ServerSelectionTimeoutError:
                                    continue
                            # newurl_id_list.append(i)
                            # else:
                            # Savedb(i, i, 'url', 'CancelUrl', remoteip, remoteport)
                            # else:
                            # Savedb(i, i, 'url', 'PrivacyUrl', remoteip, remoteport)

                    # for url in newurl_id_list:
                    # Savedb(url, url, 'url', 'NewUrl', remoteip, remoteport)  # 要改

                url_number = url_number + 1
            return True

        else:
            Savedb(url, url, 'url', 'CancelUrl', remoteip, remoteport)
            return False
    else:
        Savedb(url, url, 'url', 'PrivacyUrl', remoteip, remoteport)
        return False


def getfollowers(url, fakeua, fullproxies, needcookies, *ipport):
    global originua
    if len(ipport) == 2:
        remoteip = ipport[0]
        remoteport = ipport[1]
    else:
        remoteip = '127.1'
        remoteport = '27017'
    headers = {
        'Host': 'www.zhihu.com',
        #'User-Agent': forgeua(),
        'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, * / *;q = 0.8',
        'Accept - Language': 'en - US, en;q = 0.5',
        # 'Accept - Encoding': 'gzip, deflate, br',
        'Connection': 'keep - alive',
        'Upgrade - Insecure - Requests': '1',
        'Cache - Control': 'max - age = 0'
    }
    realproxy = chooseproxy(fullproxies)
    user_followers_url = "https://www.zhihu.com/people/" + url + "/followers"
    print(user_followers_url)
    while True:
        try:
            if fakeua:
                headers['User-Agent'] = forgeua()
            else:
                headers['User-Agent'] = originua
            response = requests.get(user_followers_url, headers=headers, proxies=realproxy, cookies=needcookies)
            break
        except requests.exceptions.ConnectionError:
            realproxy = None
            continue
    # print(response.text)
    next = response.text.replace(r'\u002F', r'/')
    # print(next)
    if 'ProfileMainPrivacy-mainContentText' not in next:
        if 'ProfileLockStatus-title' not in next:
            # follower_url = re.compile(r'\"url\":\"http://www.zhihu.com/people/(.*?)\"')
            # url_list_number = re.compile(r'Button--plain\">(.*?)</button><button type=\"button\" class="Button PaginationButton PaginationButton-next Button--plain\">')
            url_list_number = re.compile(r'Button PaginationButton Button--plain">([0-9]+)</button>')
            # info = re.findall(follower_url,next)
            number_info = re.findall(url_list_number, next)
            print(number_info)
            try:
                number_info = number_info[-1]
            except IndexError:
                number_info = 1
            # print(number_info)
            # print(next)
            try:
                number_info = int(number_info)
            except ValueError:
                number_info = 1
            print(str(number_info))
            if number_info > threshold:
                Savedb(url, url, 'url', 'NextUrl', remoteip, remoteport)
                ownremove(url, 'CrawlingUrl', remoteip, remoteport)
                return
            # print(info)
            CrawlingNum(url, 'followers', 'url', 'pagetype', netip, netport)
            try:
                nowpage = checkcrawling('url', url, netip, netport)['pagenum']
                url_number = int(nowpage)
            except KeyError:
                url_number = 1
            while url_number <= number_info:
                print('followers page: '+str(url_number))
                CrawlingNum(url, str(url_number) , 'url', 'pagenum', netip, netport)
                if lightout:
                    if checktime('22:30', '23:59'):
                        sys.exit(0)
                user_followers_url = "https://www.zhihu.com/people/" + url + "/followers?page=" + str(url_number)
                # headers['User-Agent'] = forgeua()
                time.sleep(random.randint(5, 10))
                while True:
                    try:
                        if fakeua:
                            headers['User-Agent'] = forgeua()
                        else:
                            headers['User-Agent'] = originua
                        response = requests.get(user_followers_url, headers=headers, proxies=realproxy, cookies=needcookies)
                        break
                    except requests.exceptions.ConnectionError:
                        realproxy = None
                        continue
                next = response.text.replace(r'\u002F', r'/')
                # print(next)
                followers_url = re.compile(r'\"urlToken\":\"([0-9a-zA-Z\-_]+)\",\"id\":\"')
                info = re.findall(followers_url, next)
                # del info[0]
                newurl_id_list = []
                for i in info:
                    if i:
                        mydoc = check(i, remoteip, remoteport)  # 要改
                        if not mydoc:
                            # user_followers_url = "https://www.zhihu.com/people/" + i
                            # headers['User-Agent'] = forgeua()
                            # response = requests.get(user_followers_url, headers=headers, proxies=realproxy)
                            # next = response.text.replace(r'\u002F', r'/')
                            # if 'ProfileMainPrivacy-mainContentText' not in next:
                            # if 'ProfileLockStatus-title' not in next:
                            # followers_url = re.compile(r'\",\"urlToken\":\"(.*?)\",\"name\":\"')
                            # token_info = re.findall(followers_url, next)
                            # i = token_info
                            i = str(i).strip('[\']')
                            #print(i)
                            while True:
                                try:
                                    Savedb(i, i, 'url', 'NewUrl', remoteip, remoteport)
                                    break
                                except pymongo.errors.NetworkTimeout or pymongo.errors.ServerSelectionTimeoutError:
                                    continue
                url_number = url_number + 1

            Savedb(url, url, 'url', 'CrawledUrl', remoteip, remoteport)  # 要改
            owndelete(url, 'CrawlingUrl', remoteip, remoteport)  # 要改
            if lightout:
                if checktime('22:30', '23:59'):
                    sys.exit(0)

        else:
            Savedb(url, url, 'url', 'CancelUrl', remoteip, remoteport)
            owndelete(url, 'CrawlingUrl', remoteip, remoteport)
    else:
        Savedb(url, url, 'url', 'PrivacyUrl', remoteip, remoteport)
        owndelete(url, 'CrawlingUrl', remoteip, remoteport)
        # SavePrivacyUrl(url,url)


def get_content(url, fakeua , fullproxies,needcookies, *ipport):
    global originua
    if len(ipport) == 2:
        remoteip = ipport[0]
        remoteport = ipport[1]
    else:
        remoteip = '127.1'
        remoteport = '27017'
    # api网页爬取
    headers = {
        'Host': 'api.zhihu.com'
        #'User-Agent': forgeua()
    }
    realproxy = chooseproxy(fullproxies)
    while True:
        try:
            if fakeua:
                headers['User-Agent'] = forgeua()
            else:
                headers['User-Agent'] = originua
            resp = requests.get('https://api.zhihu.com/people/' + url, headers=headers, proxies=realproxy, cookies=needcookies)
            break
        except requests.exceptions.ConnectionError:
            realproxy = None
            continue
    print(str(resp.headers['content-type']))
    valapi = json.loads(resp.content)
    # print(val)
    locabool = False
    busibool = False
    employbool = False
    edubool = False

    try:
        loca = valapi['location']
        busi = valapi['business']
        edu = valapi['education']
        employ = valapi['employment']

        info = re.compile(r'\'name\': \'(.*?)\'')
        location = re.findall(info, str(loca))
        business = re.findall(info, str(busi))
        education = re.findall(info, str(edu))
        employment = re.findall(info, str(employ))
        if education:
            education = education
        else:
            education = 'unknown'

        if employment:
            employment = employment
        else:
            employment = 'unknown'

        if business:
            business = business
        else:
            business = 'unknown'

        if stdlist[0] in str(location).strip('[\']'):
            locabool = True
            location = str(location).replace('\'', '')
            location = str(location).strip('[]')
            print('location: ' + location)
        if stdlist[0] in str(business).strip('[\']'):
            busibool = True
            business = str(business).replace('\'', '')
            business = str(business).strip('[]')
            print('business: ' + business)
        if stdlist[0] in str(employment).strip('[\']'):
            employbool = True
            employment = str(employment).replace('\'', '')
            employment = str(employment).strip('[\']')
            print('employment: ' + employment)
        for schkey in stdlist:
            if schkey in str(education).strip('[\']'):
                edubool = True
                education = str(education).replace('\'', '')
                education = str(education).strip('[\']')
                print('education: ' + education)
                break
        if locabool or busibool or employbool or edubool:
            id = valapi['id']
            name = valapi['name']
            headline = valapi['headline']
            gender = valapi['gender']
            description = valapi['description']
            numoffollower = valapi['follower_count']
            numoffollowing = valapi['following_count']
            numofanswer = valapi['answer_count']
            numofquestion = valapi['question_count']
            numofarticles = valapi['articles_count']
            favorite_count = valapi['favorite_count']
            favorited_count = valapi['favorited_count']
            voteup_count =valapi['voteup_count']
            thanked_count = valapi['thanked_count']
            print('this one is chosed')
            if gender == 1:
                gender = '男'
            if gender == 0:
                gender = '女'
            if gender == -1:
                gender = 'unknown'

            headline = str(headline).replace('\'', '')
            headline = str(headline).strip('[\']')
            business = str(business).replace('\'', '')
            business = str(business).strip('[\']')
            description = str(description).replace('\'', '')
            description = str(description).strip('[\']')
            numoffollower = str(numoffollower).replace('\'', '')
            numoffollower = str(numoffollower).strip('[\']')
            try:
                numoffollower = int(numoffollower)
            except ValueError:
                numoffollower = 0
            numoffollowing = str(numoffollowing).replace('\'', '')
            numoffollowing = str(numoffollowing).strip('[\']')
            try:
                numoffollowing = int(numoffollowing)
            except ValueError:
                numoffollowing = 0
            numofanswer = str(numofanswer).replace('\'', '')
            numofanswer = str(numofanswer).replace('\'', '')
            try:
                numofanswer = int(numofanswer)
            except ValueError:
                numofanswer = 0
            numofquestion = str(numofquestion).replace('\'', '')
            numofquestion = str(numofquestion).replace('\'', '')
            try:
                numofquestion = int(numofquestion)
            except ValueError:
                numofquestion = 0
            numofarticles = str(numofarticles).replace('\'', '')
            numofarticles = str(numofarticles).replace('\'', '')
            try:
                numofarticles = int(numofarticles)
            except ValueError:
                numofarticles = 0
            Savedb(url, id, 'url', 'id')
            Savedb(url, name, 'url', 'name')
            Savedb(url, gender, 'url', 'gender')
            Savedb(url, headline, 'url', 'headline')
            Savedb(url, description, 'url', 'description')
            Savedb(url, location, 'url', 'location')
            Savedb(url, education, 'url', 'education')
            Savedb(url, employment, 'url', 'employment')
            Savedb(url, business, 'url', 'business')
            Savedb(url, numoffollower, 'url', 'numoffollower')
            Savedb(url, numoffollowing, 'url', 'numoffollowing')
            Savedb(url, numofanswer, 'url', 'numofanswer')
            Savedb(url, numofquestion, 'url', 'numofquestion')
            Savedb(url, numofarticles, 'url', 'numofarticles')
            Savedb(url, favorite_count, 'url', 'favorite_count')
            Savedb(url, favorited_count, 'url', 'favorited_count')
            Savedb(url, voteup_count, 'url', 'voteup_count')
            Savedb(url, thanked_count, 'url', 'thanked_count')
            gettopics(url, fakeua ,allproxies ,needcookies)
        else:
            print('not be chosed')
        judge = True
    except KeyError:
        try:
            unhuman = valapi['error']['code']
            if unhuman == 40352:
                print('trigger safety verify')
                Savedb(url, url, 'url', 'NextUrl', remoteip, remoteport)
                whether, session = zhihu_login.ZhihuAccount(zhihu_login.acc, zhihu_login.sec).login('en', True)
                print('login '+str(whether))
                return session.cookies
        except BaseException:
                pass
        print('here')
        Savedb(url, url, 'url', 'CancelUrl', remoteip, remoteport)
        judge = False
    return judge

    # www网页爬取


if __name__ == "__main__":
    global originua
    originua = forgeua()
    syspath=sys.path[0]
    os.chdir(sys.path[0])
    with open('../private.json', 'rt', encoding='utf-8') as valjson:
        val = json.load(valjson)
    machinenum = str(val['machinenum'])
    print(machinenum)
    stdlist = val['stdlist']
    allproxies = val['proxies']
    netip = str(val['mongodbnet']['host'])
    netport = str(val['mongodbnet']['port'])
    thecookies = None
    #thefirst = pickyu(netip,netport)
    #lists = pickyu(netip, netport)
    # print(lists)
    #yu = re.compile(r'\'NewUrl\': \'(.*?)\'')
    try:
        crawlingcheck = checkcrawling('num', machinenum, netip, netport)
    except UnboundLocalError:
        crawlingcheck = False
        print('Not found last crawling : '+str(crawlingcheck))
    print('crawlingcheck is : '+str(crawlingcheck))
    ownremove(None, 'CrawlingUrl', netip, netport)
    try:
        if crawlingcheck:
            # cc = re.compile(r'\'url\': \'(.*?)\'')
            # url_yu = re.findall(cc, str(crawlingcheck))
            url_yu = crawlingcheck['url']
            print(url_yu)
            judge = get_content(url_yu, False, allproxies, None, netip, netport)
            if judge:
                if 'LWPCookieJar' in str(judge):
                    thecookies = judge
                    print('entering login pattern')
                    get_content(url_yu, False, None, thecookies, netip, netport)
                    if checkcrawling2('pagetype', 'followers', 'url', url_yu, netip, netport):
                        getfollowers(url_yu, False, None, thecookies, netip, netport)
                    if checkcrawling2('pagetype', 'following', 'url', url_yu, netip, netport):
                        if getfollowing(url_yu, False, None, thecookies, netip, netport):
                            CrawlingNum(url_yu, 'followers', 'url', 'pagetype', netip, netport)
                            CrawlingNum(url_yu, '1', 'url', 'pagenum', netip, netport)
                            getfollowers(url_yu, False, None, thecookies, netip, netport)
                else:
                    #thecookies = None
                    if checkcrawling2('pagetype', 'followers', 'url', url_yu, netip, netport):
                        getfollowers(url_yu, True, allproxies, None, netip, netport)
                    if checkcrawling2('pagetype', 'following', 'url', url_yu, netip, netport):
                        if getfollowing(url_yu, True, allproxies, None, netip, netport):
                            CrawlingNum(url_yu, 'followers', 'url', 'pagetype', netip, netport)
                            CrawlingNum(url_yu, '1', 'url', 'pagenum', netip, netport)
                            getfollowers(url_yu, True, allproxies, None, netip, netport)
        ownremove(url_yu, 'CrawlingUrl', netip, netport)
    except NameError:
        pass
            # if checkcrawling('pagetype', 'followers', netip, netport):
            #     getfollowers(str(url_yu).strip('[\']'), allproxies, netip, netport)

    # try:
    #     thenew = pickyu(netip,netport)
    # except TypeError:
    #     print('FirstTypeError : the NewUrl is empty')
    #     thenew = None
    #
    thenew = True
    while thenew:
        try:
            thenew = pickyu(netip, netport)
            print(thenew)
        except TypeError:
            print('TypeError  : the NewUrl is empty')
            break
        #print('exit')
    #for list in lists:
        try:
            #url_yu = re.findall(yu, thenew)
            #print(url_yu)
            # print(url_yu)
            Savedb(thenew, thenew, 'url', 'CrawlingUrl', netip, netport)  # 要改
            CrawlingNum(thenew, str(machinenum), 'url', 'num', netip, netport)
            owndelete(thenew, 'NewUrl', netip, netport)
            # url_yu = re.findall(yu, str(list))
            # time.sleep(random.randint(1, 5))

            judge = get_content(thenew, True, allproxies, thecookies, netip, netport)

            if judge:
                if 'LWPCookieJar' in str(judge):
                    thecookies = judge
                    print('entering login pattern')
                    get_content(thenew, False, None, thecookies, netip, netport)
                    if getfollowing(thenew, False, None, thecookies, netip, netport):
                        CrawlingNum(thenew, '1', 'url', 'pagenum', netip, netport)
                        getfollowers(thenew, False, None, thecookies, netip, netport)
                else:
                    if getfollowing(thenew, True, allproxies, None, netip, netport):
                        CrawlingNum(thenew, '1', 'url', 'pagenum', netip, netport)
                        getfollowers(thenew, True, allproxies, None, netip, netport)
            ownremove(thenew, 'CrawlingUrl', netip, netport)
        except urllib.error.HTTPError:
            continue



