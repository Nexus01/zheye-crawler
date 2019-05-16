# zheye-crawler
a testing crawler of zhihu which have tiny functions<br>

Thank for Zhihu-Login created by zkqiang<br>
Thank for Spider_Hub created by WiseDoge<br>
Thank for Zhihu-captcha-crack-auto-login created by DueToAttitude<br>

If there are some problems about open source License,please communicate with me to correct.<br>

please ensure the structure of the folder you clone this Repositoriy
is like below:<br>
.<br>
├── private.json<br>
├── result<br>
│   ├── en1<br>
│   ├── en2<br>
│   └── en_cla<br>
├── source<br>
│   ├── captcha_data<br>
│   ├── font_type<br>
│   └── readme_img<br>
├── zheye-crawler<br>

>while the content of `private.json` should be like following file:

{<br>
 "user": "unknown",<br>
 "proxy_on": true,<br>
 "proxies": [<br>
  null<br>
 ],<br>
 "flippagenum": 1,<br>
 "mainpage_url": "https://www.zhihu.com",<br>
 "account_url": "https://www.zhihu.com/settings/account",<br>
 "thread_num": 3,<br>
 "sleep": 1,<br>
 "mongodbnet": {<br>
  "host": "127.0.0.1",<br>
  "port": 27017<br>
 },<br>
 "stdlist": [<br>
  "github"<br>
 ],<br>
 "machinenum": 0<br>
 "onlyapi": false,<br>
 "lightout": false,<br>
 "threshold": 10000,<br>
 "target_name": [<br>
  "github"<br>
 ],<br>
 "target_url": [<br>
  "https://www.zhihu.com/topic/19566035/followers"<br>
 ] <br>
}<br>
>> there are some tips you should take care:<br>
"mongodbnet": {<br>
  "host": "the ip or domain where your mongodb has been established",<br>
  "port": the port mongodb used, which default is 27017<br>
 },<br>
 "machinenum": a num the machine in your quene,such as 0,1<br>
 "onlyapi": True is only get the userinfo and not extend the NewUrl, default is false,<br>
 "lightout": if True , the program will shutdown automatically on the schedule set before, default is false,<br>
 "threshold": the max page number of either followering or followers, which default is 10000,<br>
 "target_name": [<br>
  "which topic you want to get the information"<br>
 ],<br>
 "target_url": [<br>
  "the followers page url of target_name, you can run `gaintopicurl.py` to generate it after you fill the target_name"<br>
 ] <br>

the order of the whole project is
>modify the `private.json`
>> `python3 gaintopicurl.py`
>>>`python3 Master.py`
>>>>`python3 Slave.py`
