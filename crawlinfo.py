class Crawl(Singleton):
    def __getpagejson(self, urltoken):
        user_following_url = "https://www.zhihu.com/people/" + urltoken + "/following"
        try:
            response = requests.get(user_following_url, headers=headers, proxies=proxy.getproxies())
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                pagejson_text = soup.body.contents[1].attrs['data-state']
                pagejson = json.loads(pagejson_text)
            else:
                pagejson = dict()
        except:
            pagejson = dict()

        return pagejson

    def getinfo(self, urltoken):
        """
        调用__getpagejson函数，获取个人信息json，从中提取出该用户信息和关注用户的列表
        Args:
            urltoken: 用户主页url地址中包含的token，具有唯一性。
        Returns:
            dict: 一个包含用户信息json字符串和关注用户列表的dict
        Raises:
            None.
        """
        pagejson = self.__getpagejson(urltoken)
        # 提取该用户的关注用户列表
        try:
            followinglist = pagejson['people']['followingByUser'][urltoken]['ids']
            # 去出重复元素
            tempset = set(followinglist)
            tempset.remove(None)
            followinglist = list(tempset)
            # 转换为json字符串
            followinglist = json.dumps({'ids': followinglist})
        except:
            followinglist = json.dumps({'ids': list()})

        # 提取该用户的信息，并转换为字符串
        try:
            infojson = json.dumps(pagejson['entities']['users'][urltoken])
        except:
            infojson = ''

        info = {'user_url_token': urltoken,
                'user_data_json': infojson,
                'user_following_list': followinglist
                }
        return info