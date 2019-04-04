# -*- coding: utf-8 -*-

__author__ = 'zkqiang'
__zhihu__ = 'https://www.zhihu.com/people/z-kqiang'
__github__ = 'https://github.com/zkqiang/Zhihu-Login'

import base64
import hashlib
import hmac
import json
import re
import time
from http import cookiejar
from urllib.parse import urlencode
import execjs
import requests
from PIL import Image
import utils
import cnn_test_en
import cnn_test_en_cla
import tensorflow as tf
import random
import os
import sys
syspath=sys.path[0]
os.chdir(sys.path[0])
with open('../lastcookiepath.txt','rt',encoding='utf-8') as infosource:
    lines = infosource.readlines()
    orifromtxt= lines[-1]
accsec = json.load(open("../private.json",encoding='utf-8'))
sel = random.randint(0, len(accsec['account']) - 1)
acc = accsec['account'][sel]
sec = accsec['secret'][sel]

loadornot = True
try:
    with open(utils.lastfile, 'rt',encoding='utf-8') as infosource:
        lines = infosource.readlines()
        orifromtxt = lines[-1]
except NameError as ne:
    orifromtxt = 'not exist'
    loadornot = False
except FileNotFoundError as fe:
    orifromtxt = 'not exist'
    loadornot = False
print('loadornot is ' + str(loadornot))
class ZhihuAccount(object):

    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password

        self.login_data = {
            'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
            'grant_type': 'password',
            'source': 'com.zhihu.web',
            'username': '',
            'password': '',
            'lang': 'en',
            'ref_source': 'homepage',
            'utm_source': ''
        }
        self.session = requests.session()
        self.session.headers = {
            'accept-encoding': 'gzip, deflate, br',
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/'
        }
        self.session.headers['User-Agent'] = utils.COMMON_headers['User-Agent']
        print('the user-agent is ' + utils.COMMON_headers['User-Agent'])
        print('the cookie.txt selected is '+str(orifromtxt))
        self.session.cookies = cookiejar.LWPCookieJar(filename=orifromtxt)

    def login(self, captcha_lang: str = 'en', load_cookies: bool = True):
        """
        模拟登录知乎
        :param captcha_lang: 验证码类型 'en' or 'cn'
        :param load_cookies: 是否读取上次保存的 Cookies
        :return: bool
        """
        if load_cookies and self.load_cookies():
            print('读取 Cookies 文件')
            if self.check_login():
                print('登录成功')
                with open(utils.lastfile, 'wt',encoding='utf-8') as tempname:
                    tempname.writelines(utils.cookiepath)
                personinfo = utils.get_links(self.session,utils.val['apime_url'])
                if personinfo is not str:
                    try:
                        print(personinfo.text)
                    except AttributeError as ae:
                        print('AttributeError: \'str\' object has no attribute \'text\'')
                else:
                    print(personinfo)
                return True,self.session
            print('Cookies 已过期')

        self._check_user_pass()
        self.login_data.update({
            'username': self.username,
            'password': self.password,
            'lang': captcha_lang
        })

        timestamp = int(time.time()*1000)
        self.login_data.update({
            'captcha': self._get_captcha(self.login_data['lang']),
            'timestamp': timestamp,
            'signature': self._get_signature(timestamp)
        })

        headers = self.session.headers.copy()
        headers.update({
            'content-type': 'application/x-www-form-urlencoded',
            'x-zse-83': '3_1.1',
            'x-xsrftoken': self._get_xsrf()
        })
        data = self._encrypt(self.login_data)
        login_api = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        resp = self.session.post(login_api, data=data, headers=headers)
        while True:
            if 'error' in resp.text:
                print(json.loads(resp.text)['error'])
                print('i am here' + resp.text)
                self.login_data.update({
                                 'captcha': self._get_captcha(self.login_data['lang'])})
                data = self._encrypt(self.login_data)
                resp = self.session.post(login_api, data=data, headers=headers)
            else:
                break
        if self.check_login():
            print('登录成功')
            with open(utils.lastfile, 'wt',encoding='utf-8') as tempname:
                tempname.writelines(utils.cookiepath)
            personinfo = utils.get_links(self.session, utils.val['apime_url'])
            print(personinfo)
            return True,self.session
        print('登录失败')
        return False

    def load_cookies(self):
        """
        读取 Cookies 文件加载到 Session
        :return: bool
        """
        try:
            self.session.cookies.load(ignore_discard=True)
            return True
        except FileNotFoundError:
            return False

    def check_login(self):
        """
        检查登录状态，访问登录页面出现跳转则是已登录，
        如登录成功保存当前 Cookies
        :return: bool
        """
        login_url = 'https://www.zhihu.com/signup'
        resp = self.session.get(login_url, allow_redirects=False)
        if resp.status_code == 302:
            self.session.cookies.save(utils.cookiepath)
            return True
        return False

    def _get_xsrf(self):
        """
        从登录页面获取 xsrf
        :return: str
        """
        self.session.get('https://www.zhihu.com/', allow_redirects=False)
        for c in self.session.cookies:
            if c.name == '_xsrf':
                return c.value
        raise AssertionError('获取 xsrf 失败')

    def _get_captcha(self, lang: str):
        """
        请求验证码的 API 接口，无论是否需要验证码都需要请求一次
        如果需要验证码会返回图片的 base64 编码
        根据 lang 参数匹配验证码，需要人工输入
        :param lang: 返回验证码的语言(en/cn)
        :return: 验证码的 POST 参数
        """
        if lang == 'cn':
            api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=cn'
        else:
            api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
        resp = self.session.get(api)
        show_captcha = re.search(r'true', resp.text)

        if show_captcha:
            g = tf.Graph()
            if lang == 'cn':
                with g.as_default():
                    print('entering chinese captcha\n')  # cnntest_cn = cnn_test_cn.CnnTest('result/cn1')
            else:
                with g.as_default():
                    cnntest_cla = cnn_test_en_cla.CnnTest('../result/en_cla')
            try_num = 0
            put_resp = self.session.put(api)
            json_data = json.loads(put_resp.text)
            img_base64 = json_data['img_base64'].replace(r'\n', '')
            with open('../captcha.jpg', 'wb') as f:
                f.write(base64.b64decode(img_base64))
            img = Image.open('../captcha.jpg')
            if lang == 'cn':
                import matplotlib.pyplot as plt
                #plt.imshow(img)
                print('点击所有倒立的汉字，按回车提交')
                points = plt.ginput(7)
                capt = json.dumps({'img_size': [200, 44],
                                   'input_points': [[i[0]/2, i[1]/2] for i in points]})
            else:
                #img.show()
                #capt = input('请输入图片里的验证码：')
                type = cnntest_cla.cnn_test_single(img)
                if type == 0:
                    g1 = tf.Graph()
                    with g1.as_default():
                        cnntest_en = cnn_test_en.CnnTest('../result/en1')
                else:
                    g1 = tf.Graph()
                    with g1.as_default():
                        cnntest_en = cnn_test_en.CnnTest('../result/en2')
                capt = cnntest_en.cnn_test_single(img)
            print('Recognized Captcha, ' + str(try_num + 1) + '(times) : ' + capt)

            time.sleep(random.randint(5, 10))
            # 这里必须先把参数 POST 验证码接口
            self.session.post(api, data={'input_text': capt})
            print('resp.status_code is ' + str(resp.status_code) + ' ' + capt)
            return capt
        return ''

    def _get_signature(self, timestamp: int or str):
        """
        通过 Hmac 算法计算返回签名
        实际是几个固定字符串加时间戳
        :param timestamp: 时间戳
        :return: 签名
        """
        ha = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        grant_type = self.login_data['grant_type']
        client_id = self.login_data['client_id']
        source = self.login_data['source']
        ha.update(bytes((grant_type + client_id + source + str(timestamp)), 'utf-8'))
        return ha.hexdigest()

    def _check_user_pass(self):
        """
        检查用户名和密码是否已输入，若无则手动输入
        """
        if not self.username:
            self.username = input('请输入手机号：')
        if self.username.isdigit() and '+86' not in self.username:
            self.username = '+86' + self.username

        if not self.password:
            self.password = input('请输入密码：')
    @staticmethod
    def _encrypt(form_data: dict):
        with open('./encrypt.js') as f:
            js = execjs.compile(f.read())
            return js.call('Q', urlencode(form_data))


if __name__ == '__main__':
    account = ZhihuAccount(acc, sec)
    print(acc +' ' +sec)
    account.login(captcha_lang='en', load_cookies= loadornot)
