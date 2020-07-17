import hashlib

import requests
from bs4 import BeautifulSoup
import common.libs.dm
import os
from config.base_setting import UPLOAD

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/73.0.3683.86 Safari/537.36'}
# username = "2017211001000329"
#
# password ="990617.zxz"
root_path = UPLOAD['prefix_path']
import time
# 获得图片后缀
# file_suffix = os.path.splitext(img_url)[1]
# 拼接图片名（包含路径）

filename=''
def download_code(s,uid):
    #向登录界面发送请求
    url = 'https://jwxt.ecjtu.edu.cn/login.jsp'
    r = s.get(url,headers=headers)

    #解析获取验证码图片链接
    file_path = root_path + uid
    if not os.path.exists(file_path):
        # 创建路径
        os.makedirs(file_path)
    global filename
    filename="code{}.png".format(time.strftime("%H%M%S"))
    filename = '{}{}{}'.format(file_path, os.sep, filename)
    soup = BeautifulSoup(r.text,'lxml')
    img_src = soup.find('img',id='logCode')['src']
    img_url = ' https://jwxt.ecjtu.edu.cn/' + img_src
    # print(img_url)

    #向图片链接发送请求，下载图片
    r_img = s.get(img_url,headers=headers)

    with open(filename,'wb') as fp:
        fp.write(r_img.content)


    #查找form表单所需的两个参数
    __VIEWSTATE = soup.find('input',id='inputUser')['value']
    __VIEWSTATEGENERATOR = soup.find('input',id='inputPassword')['value']

    return __VIEWSTATE,__VIEWSTATEGENERATOR

def login(s,username,password):
    post_url = 'https://jwxt.ecjtu.edu.cn/stuMag/Login_login.action'
    m = hashlib.md5()

    b = password.encode(encoding='utf-8')
    m.update(b)
    password = m.hexdigest()

    global filename
    # print(filename)
    code = common.libs.dm.dama(filename)

    form_data = {'UserName':username,
                'Password': password,
                'code':code
            }

    r = s.post(url=post_url,headers=headers,data=form_data)

    # print(r.text)
    return r.text
    #
    # with open('gushi.html','w',encoding='utf8') as fp:
    #     fp.write(r.text)

def main(username,password,uid):
    #创建会话
    s = requests.Session()

    #下载验证码
    VIEW,VIEWG = download_code(s,uid)

    #进行登录
    return login(s,username,password)


if __name__ == '__main__':
    main()