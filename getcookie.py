import requests
import browsercookie
from http import cookiejar
import re

mycookiejar = browsercookie.firefox() # 读取firefox浏览器中的cookies，创建一个cookiejar对象
filename = 'fakecookie.txt'
fakecookies = mycookiejar
#(?<=A).*?(?=B)
#A='<Cookie\s'
#B=' for .zhihu.com/>,'
getzhihurule=re.compile('<Cookie (_xsrf|_zap|capsion_ticket|d_c0|z_c0)=(.*?)(?=(.zhihu.com))') #[_zap|d_c0|z_c0|tgw_l7_route]
#fakecookies = cookiejar.LWPCookieJar(filename=filename)
gettgw=re.compile('(tgw_l7_route=)(.*?)(www.zhihu.com)') #(?!.*(公司|合伙))(.*)
#print(mycookiejar)
with open('fakecookie.txt', 'wt') as f:
    f.write(str(mycookiejar))
#设置cookie保存的文件
with open('fakecookie.txt', 'rt') as f:
    textcontent=f.read()
print(textcontent)
matchobj = re.findall(getzhihurule, textcontent)
tgwobj=re.findall(gettgw,textcontent)
#print(matchobj)
#nextrule=re.compile(r'tgw_l7_route=(.*?)(?= for www.zhihu.com)')
#nexttgw=re.search(nextrule,str(tgwobj))
with open('fakecookie.txt', 'wt') as tricookie:
    tricookie.write(str(matchobj))
with open('fakecookie.txt','at') as tgw:
    tgw.write('\n'+str(tgwobj)+'\n')
#print('\n'+str(nexttgw))


# nextrule=re.compile(r'(?<==).*?(?=for\s.zhihu.com/>,)')
# nextmatch=re.findall(nextrule, nextcontent)
# print(nextmatch)
# with open('fakecookie.txt', 'wt') as f:
#     f.write(str(nextmatch))
# with open('fakecookie.txt', 'rt') as f:
#     nexuscontent=f.read()
# nexusrule=re.compile(r'(=).*?(?=\s\')')
# nexusmatch=re.findall(nexusrule, nexuscontent)
# print(nexusmatch)
#cookie_obj = LWPCookieJar(filename=filename)
url = 'https://www.zhihu.com/settings/account'
#url = 'https://www.zhihu.com/settings/profile'
headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
}
#response = requests.get(url, headers=headers, cookies=mycookiejar)  # 发送GET请求时，附带cookiejar对象
#fakecookies.save(filename, ignore_discard=True, ignore_expires=True)
#print(response.status_code)
#print(response.text)