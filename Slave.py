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
import base64
from PIL import Image
import cnn_test_en
import cnn_test_en_cla
import tensorflow as tf
# onlyapi = False
# lightout = False
# threshold = 10000


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
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient['zhihu']
    mycol = mydb[valuename]
    myquery = {'url': thevalue}
    mycol.delete_one(myquery)

def ownremove(thevalue,valuename, *ipport):
    if len(ipport) == 2:
        myclient = pymongo.MongoClient('mongodb://' + ipport[0] + ':' + ipport[1] + '/')
    else:
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient['zhihu']  # shujuku
    mycol = mydb[valuename]  # jihe
    myquery = {'url': thevalue}
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

def check(urltoken, urlcol, *ipport):
    if len(ipport) == 2:
        myclient = pymongo.MongoClient('mongodb://' + ipport[0] + ':' + ipport[1] + '/')
    else:
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient['zhihu']
    mycol = mydb[urlcol]
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
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
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
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient['zhihu']
    mycol = mydb['CrawlingUrl']
    myquery = {thekey: str(thevalue), thekey2: str(thevalue2)}
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



def Savedb(thekey, thevalue, keyname, colname, *ipport):
    if len(ipport) == 2:
        myclient = pymongo.MongoClient('mongodb://' + ipport[0] + ':' + ipport[1] + '/')
    else:
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')  # 远程服务器的IP和端口
    mydb = myclient['zhihu']  # shujuku
    mycol = mydb[colname]  # jihe
    setvalue = {keyname: thevalue}
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

def file_name(file_dir):
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.gif':
                L.append(os.path.join(root, file))
    return L

def gettopics(url, fakeua, fullproxies, needcookies, *ipport):
    global originua
    if len(ipport) == 2:
        remoteip = ipport[0]
        remoteport = ipport[1]
    else:
        remoteip = '127.1'
        remoteport = '27017'
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
                'https://www.zhihu.com/api/v4/members/' + url + '/following-topic-contributions?include=data[*].topic.introduction&offset=0&limit=20',
                headers=headers, proxies=realproxy, cookies=needcookies)
            if '安全验证' in resp.content.decode('utf-8'):
                hackcapt(headers['User-Agent'], realproxy)
                print('hack successfully')
                resp = requests.get('https://www.zhihu.com/api/v4/members/' + url + '/following-topic-contributions?include=data[*].topic.introduction&offset=0&limit=20', headers=headers, proxies=realproxy, cookies=needcookies)
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
        while True:
            try:
                if fakeua:
                    headers['User-Agent'] = forgeua()
                else:
                    headers['User-Agent'] = originua
                resp = requests.get(
                    'https://www.zhihu.com/api/v4/members/' + url + '/following-topic-contributions?include=data[*].topic.introduction&offset=' + str(
                        offset) + '&limit=20', headers=headers, proxies=realproxy, cookies = needcookies)
                if '安全验证' in resp.content.decode('utf-8'):
                    hackcapt(headers['User-Agent'], realproxy)
                    print('hack successfully')
                    resp = requests.get('https://www.zhihu.com/api/v4/members/' + url + '/following-topic-contributions?include=data[*].topic.introduction&offset=' + str(
                        offset) + '&limit=20', headers=headers, proxies=realproxy, cookies=needcookies)
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
    setvalue = {'topics': topics}
    myclient = pymongo.MongoClient('mongodb://' + remoteip + ':' + remoteport + '/')  # 远程服务器的IP和端口
    mydb = myclient['zhihu']
    mycol = mydb['userinfo']
    mycol.update_one({'url': url}, {'$set': setvalue}, upsert=True)
    #Savedb(url, topics, 'topics', 'userinfo')


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
            if '安全验证' in response.content.decode('utf-8'):
                hackcapt(headers['User-Agent'], realproxy)
                print('hack successfully')
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
                time.sleep(random.randint(1, 5))
                while True:
                    try:
                        if fakeua:
                            headers['User-Agent'] = forgeua()
                        else:
                            headers['User-Agent'] = originua
                        response = requests.get(user_following_url, headers=headers, proxies=realproxy, cookies=needcookies )
                        if '安全验证' in response.content.decode('utf-8'):
                            hackcapt(headers['User-Agent'], realproxy)
                            print('hack successfully')
                            response = requests.get(user_following_url, headers=headers, proxies=realproxy,
                                                    cookies=needcookies)
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
                        mydoc1 = check(i, 'CrawledUrl', remoteip, remoteport)
                        mydoc2 = check(i, 'NextUrl', remoteip, remoteport)
                        mydoc3 = check(i, 'PrivacyUrl', remoteip, remoteport)
                        mydoc4 = check(i, 'CancelUrl', remoteip, remoteport)
                        if not (mydoc1 or mydoc2 or mydoc3 or mydoc4):
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
                    # Savedb(url, url, 'url', 'NewUrl', remoteip, remoteport)

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
            if '安全验证' in response.content.decode('utf-8'):
                hackcapt(headers['User-Agent'], realproxy)
                print('hack successfully')
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
                time.sleep(random.randint(1, 5))
                while True:
                    try:
                        if fakeua:
                            headers['User-Agent'] = forgeua()
                        else:
                            headers['User-Agent'] = originua
                        response = requests.get(user_followers_url, headers=headers, proxies=realproxy, cookies=needcookies)
                        if '安全验证' in response.content.decode('utf-8'):
                            hackcapt(headers['User-Agent'], realproxy)
                            print('hack successfully')
                            response = requests.get(user_followers_url, headers=headers, proxies=realproxy, cookies=needcookies)
                        break
                    except requests.exceptions.ConnectionError:
                        realproxy = None
                        continue
                next = response.text.replace(r'\u002F', r'/')
                # print(next)
                followers_url = re.compile(r'\"urlToken\":\"([0-9a-zA-Z\-_]+)\",\"id\":\"')
                info = re.findall(followers_url, next)
                for i in info:
                    if i:
                        mydoc1 = check(i, 'CrawledUrl', remoteip, remoteport)
                        mydoc2 = check(i, 'NextUrl', remoteip, remoteport)
                        mydoc3 = check(i, 'PrivacyUrl', remoteip, remoteport)
                        mydoc4 = check(i, 'CancelUrl', remoteip, remoteport)
                        if not (mydoc1 or mydoc2 or mydoc3 or mydoc4):
                            i = str(i).strip('[\']')
                            #print(i)
                            while True:
                                try:
                                    Savedb(i, i, 'url', 'NewUrl', remoteip, remoteport)
                                    break
                                except pymongo.errors.NetworkTimeout or pymongo.errors.ServerSelectionTimeoutError:
                                    continue
                url_number = url_number + 1

            Savedb(url, url, 'url', 'CrawledUrl', remoteip, remoteport)
            owndelete(url, 'CrawlingUrl', remoteip, remoteport)
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

def hackcapt(usa,hackpro):
    wwwheaders = {
        'Host': 'www.zhihu.com',
        'User-Agent': usa
    }
    apiheaders = {
        'Host': 'api.zhihu.com',
        'User-Agent': usa
    }
    nextheaders = {
        'Host': 'www.zhihu.com',
        'User-Agent': usa,
        'Accept': '*/*',
        'Accept - Language': 'en-US,en;q=0.5',
        'Accept - Encoding': 'gzip,deflate,br',
        'x-requested-with': 'fetch',
        'content-type': 'application/json',
        'Origin': 'https://www.zhihu.com',
        'Content - Length': '18',
        'Connection': 'keep-alive',
        'TE': 'Trailers'
    }
    safeurl = 'https://www.zhihu.com/account/unhuman?type=unhuman&message=系统监测到您的网络环境存在异常，为保证您的正常访问，请输入验证码进行验证。&need_login=true'
    capturl = 'https://www.zhihu.com/api/v4/anticrawl/captcha_appeal'
    guesturl = 'https://www.zhihu.com/api/v3/explore/guest/feeds?limit=1'
    topstoryurl = 'https://www.zhihu.com/api/v3/feed/topstory/hot-list-wx?limit=1'
    apitopurl = 'https://api.zhihu.com/topstory'
    testnum = random.randint(0, 1)
    if testnum == 0:
        testurl = guesturl
    else:
        testurl = topstoryurl
    session = requests.session()
    try_num = 0
    #resp = session.get(testnet, headers=apiheaders)
    #print(resp.content.decode('utf-8'))
    #valapi = json.loads(resp.content, encoding='utf-8')
    while True:
        try:
            resp0 = session.get(apitopurl, headers=apiheaders, proxies=hackpro)
            if 'error' not in str(resp0.content):
                print(json.loads(resp0.content))
                break
            os.chdir(sys.path[0])
            # print(sys.path[0])

            resp1 = session.get(safeurl, headers=wwwheaders, proxies=hackpro)
            time.sleep(random.randint(1, 10))
            nowTime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            imgdir = '../capttemp'
            imgpath = '../capttemp/captcha' + str(nowTime) + '.gif'
            #print(resp1.content.decode('utf-8'))
            # resp1con=json.loads(resp1.content,encoding='utf-8')
            #print(resp1.content.decode('utf-8'))
            resp2 = session.get(capturl, headers=wwwheaders, proxies=hackpro)
            #print(resp2.content)
            resp2con = json.loads(resp2.content)
            #print(resp2con)
            img_base64 = resp2con['img_base64'].replace(r'\n', '')
            #print(img_base64)
            if not os.path.exists(imgdir):
                os.mkdir(imgdir)
            with open(imgpath, 'wb+') as f:
                f.write(base64.b64decode(img_base64))
            print('middle open')
            g = tf.Graph()
            with g.as_default():
                cnntest_cla = cnn_test_en_cla.CnnTest('../result/en_cla')
            try_num = 0
            try:
                img = Image.open(imgpath)
            #img.show()
                type = cnntest_cla.cnn_test_single(img)
                if type == 0:
                    g1 = tf.Graph()
                    with g1.as_default():
                        cnntest_en = cnn_test_en.CnnTest('../result/en1')
                        entype = '1'
                else:
                    g1 = tf.Graph()
                    with g1.as_default():
                        cnntest_en = cnn_test_en.CnnTest('../result/en2')
                        entype = '2'
                capt = cnntest_en.cnn_test_single(img)
                #print('Recognized Captcha, ' + str(try_num + 1) + '(times) : ' + capt)
                # 返回正确与否
                #img.show()
                img.close()
            except IOError:
                continue
            os.remove(imgpath)
            try_num += 1
            print('Recognized Captcha, ' + str(try_num) + '(times) : ' + capt)
            params = json.dumps({"captcha": capt})
            #print(params)
            time.sleep(random.randint(5, 10))
            resp3 = session.post(capturl, headers=nextheaders, data=params.encode("utf-8").decode("latin1"), proxies=hackpro)
            print('resp.status_code is ' + str(resp3.status_code) + ' ' + capt)
            print(resp3.content.decode('utf-8'))
            resp4 = requests.get(testurl, headers=wwwheaders, proxies=hackpro)
            if resp4.status_code == 200:
                if 'error' not in str(resp4.content):
                    print(resp4.content.decode('utf-8'))
                    print('not trigger safety verify\nhave hacked the anticrawl successfully')
                    thefilenamelist = file_name('../source/captcha_data/en' + str(entype))
                    T = []
                    if not os.path.exists('../source/captcha_data'):
                        os.mkdir('../source/captcha_data')
                        os.mkdir('../source/captcha_data/en1')
                        os.mkdir('../source/captcha_data/en2')
                        print('mkdir success')
                    bignumrule = re.compile(r'../source/captcha_data/en' + str(entype) + '/([0-9]+)_[0-9a-zA-Z]{4}.gif')
                    for turn in thefilenamelist:
                        foundname = re.match(bignumrule, turn)
                        T.append(str(foundname.groups()[0]))
                            # print(foundname.groups()[0])
                    try:
                        tmax = T[0]
                    except IndexError:
                        tmax = -1
                    for t in T:
                        # ttemp = t
                        if int(tmax) < int(t):
                            tmax = t
                    print('max is ' + str(tmax))
                    nextnum = int(tmax) + 1
                    print('entype is : en' + str(entype))
                        #        print(type(nextnum))
                    with open('../source/captcha_data/en' + str(entype) + '/' + str(nextnum) + '_' + str(capt) + '.gif', 'wb+') as newmatch:
                            newmatch.write(base64.b64decode(img_base64))
                    print('saveing the matched captcha and content')
                    break
        except BaseException as be:
            print(be)
            continue


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
            try:
                respcon=resp.content.decode('utf-8')
                #print(respcon)
                if '您当前请求存在异常，暂时限制本次访问' in str(respcon):
                    print('您当前请求存在异常，暂时限制本次访问')
                    break
                if '40352' in str(json.loads(respcon)['error']['code']):
                    print('trigger safety verify')
                    hackcapt(headers['User-Agent'], realproxy)
                    print('hack successfully')
                    resp = requests.get('https://api.zhihu.com/people/' + url, headers=headers, proxies=realproxy,
                                        cookies=needcookies)
            except KeyError:
                pass
            break
        except requests.exceptions.ConnectionError:
            realproxy = None
            continue
    print(str(resp.headers['content-type']))
    try:
        valapi = json.loads(resp.content)
    except JSONDecodeError:
        return False
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

        for schkey in stdlist:
            if schkey in str(location).strip('[\']'):
                locabool = True
                location = str(location).replace('\'', '')
                location = str(location).strip('[]')
                print('location: ' + location)
                break
        for schkey in stdlist:
            if schkey in str(business).strip('[\']'):
                busibool = True
                business = str(business).replace('\'', '')
                business = str(business).strip('[]')
                print('business: ' + business)
                break
        for schkey in stdlist:
            if schkey in str(employment).strip('[\']'):
                employbool = True
                employment = str(employment).replace('\'', '')
                employment = str(employment).strip('[\']')
                print('employment: ' + employment)
                break
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

            # Savedb(url, id, 'id', 'userinfo')
            # Savedb(url, name, 'name', 'userinfo')
            # Savedb(url, gender, 'gender', 'userinfo')
            # Savedb(url, headline, 'headline', 'userinfo')
            # Savedb(url, description, 'description', 'userinfo')
            # Savedb(url, location, 'location', 'userinfo')
            # Savedb(url, education, 'education', 'userinfo')
            # Savedb(url, employment, 'employment', 'userinfo')
            # Savedb(url, business, 'business', 'userinfo')
            # Savedb(url, numoffollower, 'numoffollower', 'userinfo')
            # Savedb(url, numoffollowing, 'numoffollowing', 'userinfo')
            # Savedb(url, numofanswer, 'numofanswer', 'userinfo')
            # Savedb(url, numofquestion, 'numofquestion', 'userinfo')
            # Savedb(url, numofarticles, 'numofarticles', 'userinfo')
            # Savedb(url, favorite_count, 'favorite_count', 'userinfo')
            # Savedb(url, favorited_count, 'favorited_count', 'userinfo')
            # Savedb(url, voteup_count,  'voteup_count', 'userinfo')
            # Savedb(url, thanked_count, 'thanked_count', 'userinfo')
            setvalue = {'id': id, 'name': name, 'gender': gender, 'headline': headline, 'description': description,
                        'location': location, 'education': education, 'employment': employment, 'business': business,
                        'numoffollower': numoffollower, 'numoffollowing': numoffollowing, 'numofanswer': numofanswer,
                        'numofquestion': numofquestion, 'numofarticles': numofarticles, 'favorite_count': favorite_count,
                        'favorited_count': favorited_count, 'voteup_count': voteup_count, 'thanked_count': thanked_count}
            myclient = pymongo.MongoClient('mongodb://' + remoteip + ':' + remoteport + '/')
            mydb = myclient['zhihu']
            mycol = mydb['userinfo']
            mycol.update_one({'url': url}, {'$set': setvalue}, upsert=True)
            gettopics(url, fakeua, allproxies, needcookies, remoteip, remoteport)
            judge = 'chosed'
            print('Putting it into SelectUrl')
            Savedb(url, url, 'url', 'SelectUrl', remoteip, remoteport)
        else:
            judge = 'not chosed'
            print('not be chosed')
            Savedb(url, url, 'url', 'CrawledUrl', remoteip, remoteport)
    except KeyError:
        print('Putting it into CancelUrl')
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
    onlyapi = val['onlyapi']
    lightout = val['lightout']
    threshold = val['threshold']
    machinenum = str(val['machinenum'])
    print(machinenum)
    stdlist = val['stdlist']
    allproxies = val['proxies']
    netip = str(val['mongodbnet']['host'])
    netport = str(val['mongodbnet']['port'])
    thecookies = None
    if not onlyapi:
        try:
            crawlingcheck = checkcrawling('num', machinenum, netip, netport)
        except UnboundLocalError:
            crawlingcheck = False
            print('Not found last crawling : '+str(crawlingcheck))
        print('crawlingcheck is : '+str(crawlingcheck))
        ownremove(None, 'CrawlingUrl', netip, netport)

        try:
            if crawlingcheck:
                url_yu = crawlingcheck['url']
                print('crawlingcheck url is '+url_yu)
                judge = get_content(url_yu, False, allproxies, None, netip, netport)
                if judge:
                        # get_content(url_yu, False, None, thecookies, netip, netport)
                        # if checkcrawling2('pagetype', 'followers', 'url', url_yu, netip, netport):
                        #     getfollowers(url_yu, False, None, thecookies, netip, netport)
                        # if checkcrawling2('pagetype', 'following', 'url', url_yu, netip, netport):
                        #     if getfollowing(url_yu, False, None, thecookies, netip, netport):
                        #         CrawlingNum(url_yu, 'followers', 'url', 'pagetype', netip, netport)
                        #         CrawlingNum(url_yu, '1', 'url', 'pagenum', netip, netport)
                        #         getfollowers(url_yu, False, None, thecookies, netip, netport)
                #else:
                    print('entering continue crawling')
                    if checkcrawling2('pagetype', 'followers', 'url', url_yu, netip, netport):
                        print('entering followers')
                        getfollowers(url_yu, True, allproxies, None, netip, netport)
                    if checkcrawling2('pagetype', 'following', 'url', url_yu, netip, netport):
                        print('entering following')
                        if getfollowing(url_yu, True, allproxies, None, netip, netport):
                            CrawlingNum(url_yu, 'followers', 'url', 'pagetype', netip, netport)
                            CrawlingNum(url_yu, '1', 'url', 'pagenum', netip, netport)
                            getfollowers(url_yu, True, allproxies, None, netip, netport)
            ownremove(url_yu, 'CrawlingUrl', netip, netport)
        except NameError:
            pass

    # try:
    #     thenew = pickyu(netip,netport)
    # except TypeError:
    #     print('FirstTypeError : the NewUrl is empty')
    #     thenew = None
    #
    thenew = True
    while thenew:
        #time.sleep(random.randint(1, 3))
        try:
            thenew = pickyu(netip, netport)
            print(thenew)
        except TypeError:
            print('TypeError  : the NewUrl is empty')
            break
        try:
            Savedb(thenew, thenew, 'url', 'CrawlingUrl', netip, netport)
            owndelete(thenew, 'NewUrl', netip, netport)
            if not onlyapi:
                CrawlingNum(thenew, str(machinenum), 'url', 'num', netip, netport)

            judge = get_content(thenew,  True, allproxies, thecookies, netip, netport)
            if not onlyapi:
                if judge and ('not' not in str(judge)):
                    if getfollowing(thenew, True, allproxies, None, netip, netport):
                        CrawlingNum(thenew, '1', 'url', 'pagenum', netip, netport)
                        getfollowers(thenew, True, allproxies, None, netip, netport)
            ownremove(thenew, 'CrawlingUrl', netip, netport)
        except urllib.error.HTTPError:
            continue



