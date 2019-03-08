import browsercookie
import re
import utils
import random
import time

def standardize(time):
    if time < 10:
        realtime = '0'+str(time)
    else:
        realtime = str(time)
    return realtime



def sixtycal(subtime,dayofmonth,month,day,hour,minute,second):#(elative,superior,base,low,subtime):
    if second-subtime < 0:
        resecond = second + 60 -subtime
        if minute -1 < 0:
            realminute = minute + 60 -1
            if hour -1 < 0:
                realhour = hour + 24 -1
                if day -1 < 0:
                    realday = day + dayofmonth[month-1] -1
                    if month -1 < 0:
                        realmonth = month + 12 -1
    else:
        resecond = second -subtime
    return resecond

def judgeleapyear(year):
    daynumofmonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                daynumofmonth[1] = 29
        else:
            daynumofmonth[1] = 29
    return daynumofmonth

mycookiejar = browsercookie.firefox() # 读取firefox浏览器中的cookies，创建一个cookiejar对象
filename = '../fakecookie.txt'
tempfile='../tempcookie.txt'
lastfile='../lastcookiepath.txt'
fakecookies = mycookiejar
getzhihurule=re.compile(r'<Cookie (_xsrf|_zap|capsion_ticket|d_c0|z_c0|q_c1|tst)=(.*?)(?=(.zhihu.com))') #[_zap|d_c0|z_c0|tgw_l7_route]
gettgw=re.compile('(tgw_l7_route=)(.*?)(?<= for www.zhihu.com)')
with open(filename, 'wt') as f:
    f.write(str(mycookiejar))
#设置cookie保存的文件
with open(filename, 'rt') as f:
    textcontent=f.read()
matchobj = re.findall(getzhihurule, textcontent)
tgwobj=re.search(gettgw,textcontent)
savetgw=tgwobj
tgwnum=0
while(True):
    try:
        tgwobj = re.search(gettgw,str(tgwobj.group(2)))
        tgwnum = tgwnum+1
    except AttributeError:
        break
i = 0
tgwobj = savetgw
print('tgwnum: '+str(tgwnum)+'\n')
while i < tgwnum-1:
    tgwobj = re.search(gettgw, str(tgwobj.group(2)))
    i = i+1
_zaprule=re.compile(r'(_zap=)(.*?)(?= for .zhihu.com)')
_zapobj=re.search(_zaprule,textcontent)
#print(_zapobj.group(2))
capsion_ticketrule=re.compile(r'(capsion_ticket=)(.*?)(?=" for .zhihu.com)')
capsion_ticketobj=re.search(capsion_ticketrule,textcontent)
#print(capsion_ticketobj.group(2))
d_c0rule=re.compile(r'(d_c0=)(.*?)(?=" for .zhihu.com)')
d_c0obj=re.search(d_c0rule,textcontent)
#print(d_c0obj.group(2))
z_c0rule=re.compile(r'(z_c0=)(.*?)(?=" for .zhihu.com)')
z_c0obj=re.search(z_c0rule,textcontent)
#print(z_c0obj.group(2))

#print(tgwobj.group(2))
nexttgwobj=re.sub(r' for www.zhihu.com',"", str(tgwobj.group(2)))
#print(nexttgwobj)
neednum = str(utils.nowTime)
fakeyear = random.randint(2018, 2020)
daynumofmonth = judgeleapyear(fakeyear)
fakemonth = random.randint(1, 12)

fakeday = random.randint(1, daynumofmonth[random.randint(0, 11)])
fakehour = random.randint(0, 23)
fakeminute = random.randint(0, 59)
fakesecond = random.randint(0, 59)
realfakemonth = standardize(fakemonth)
realfakeday = standardize(fakeday)
realfakehour = standardize(fakehour)
realfakeminute = standardize(fakeminute)
realfakesecond = standardize(fakesecond)
nextyear = fakeyear+1
kagashi = fakeyear+1
realsecond = standardize(sixtycal(random.randint(0, 10), daynumofmonth, fakemonth, fakeday, fakehour, fakeminute, fakesecond))
cookiepath='../owncookies/cookies'+str(neednum)+'.txt'
with open(lastfile, 'wt') as tempname:
    tempname.writelines(cookiepath)
with open(cookiepath, 'wt') as tricookie:
    tricookie.write('#LWP-Cookies-2.0'+'\n')
    tricookie.write('Set-Cookie3: _zap="' + _zapobj.group(2) + '"; path="/"; domain=".zhihu.com"; path_spec; domain_dot; expires="'+str(int(fakeyear)+2)+'-'+standardize(fakemonth-1)+'-'+realfakeday+' '+realfakehour+':'+realfakeminute+':'+realsecond+'Z"; version=0' + '\n')
    tricookie.write('Set-Cookie3: capsion_ticket="\\' + capsion_ticketobj.group(2) + '\\""; path="/"; domain=".zhihu.com"; path_spec; expires="'+str(fakeyear)+'-'+realfakemonth+'-'+realfakeday+' '+realfakehour+':'+realfakeminute+':'+realfakesecond+'Z"; httponly=None; version=0' + '\n')
    tricookie.write('Set-Cookie3: d_c0="\\' + d_c0obj.group(2) + '\\""; path="/"; domain=".zhihu.com"; path_spec; expires="'+str(int(fakeyear)+3)+'-'+standardize(fakemonth-1)+'-'+realfakeday+' '+realfakehour+':'+realfakeminute+':'+realsecond+'Z"; version=0' + '\n')
    tricookie.write('Set-Cookie3: z_c0="\\' + z_c0obj.group(2) + '\\""; path="/"; domain=".zhihu.com"; path_spec; expires="'+str(int(fakeyear)+1)+'-'+standardize(int((fakemonth-2)/2))+'-'+standardize(int(realfakeday)-1)+' '+realfakehour+':'+realfakeminute+':'+realsecond+'Z"; httponly=None; version=0' + '\n')
with open(cookiepath, 'at') as tgw:
    tgw.write(str('Set-Cookie3: tgw_l7_route='+str(nexttgwobj)+'; path="/"; domain="www.zhihu.com"; path_spec; expires="'+str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))+'Z"; version=0'+'\n'))
with open(cookiepath, 'rt') as allcookie:
    tgwlen=len(allcookie.readlines())
    tgwloca=int(tgwlen)-1
with open(cookiepath, 'rt') as allcookie:
    tgwroute=allcookie.readlines()[tgwloca]


