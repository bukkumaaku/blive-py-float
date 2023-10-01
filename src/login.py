# -*- coding: utf-8 -*-
import http.cookiejar as cookielib
import os
import threading
import time

import psutil
import requests
from qrcode import QRCode
import src.varlist as bv
requests.packages.urllib3.disable_warnings()




def showPng(url):
    qr = QRCode()
    qr.add_data(url)
    image = qr.make_image().convert('RGB')
    image.show()


def islogin(session):
    try:
        session.cookies.load(ignore_discard=True)
    except Exception as e:
        print(f"加载cookies时发生错误: {e}，正在重新生成")
        pass
    loginurl = session.get("https://api.bilibili.com/x/web-interface/nav", verify=False, headers=bv.headers1).json()
    if loginurl['code'] == 0:
        print('Cookies值有效，', loginurl['data']['uname'], '，已登录！')
        return session, True
    else:
        print('Cookies值已经失效，请重新扫码登录！')
        return session, False


def checkLogin():
    if not os.path.exists(bv.cookiePath):
        with open(bv.cookiePath, 'w') as f:
            f.write("")
    session = requests.session()
    session.cookies = cookielib.LWPCookieJar(filename=bv.cookiePath)
    session, status = islogin(session)
    if not status:
        getlogin = session.get('https://passport.bilibili.com/qrcode/getLoginUrl', headers=bv.headers1).json()
        loginurl = requests.get(getlogin['data']['url'], headers=bv.headers1).url
        oauthKey = getlogin['data']['oauthKey']
        thread = threading.Thread(target=showPng, args=(loginurl,))
        thread.start()
        tokenUrl = 'https://passport.bilibili.com/qrcode/getLoginInfo'
        while True:
            qrcodeData = session.post(tokenUrl, data={'oauthKey': oauthKey, 'gourl': 'https://www.bilibili.com/'},
                                      headers=bv.headers2).json()
            if '-4' in str(qrcodeData['data']):
                print('二维码未失效，请扫码！')
            elif '-5' in str(qrcodeData['data']):
                print('已扫码，请确认！')
            elif '-2' in str(qrcodeData['data']):
                print('二维码已失效，请重新运行！')
            elif 'True' in str(qrcodeData['status']):
                print('已确认，登入成功！')
                session.get(qrcodeData['data']['url'], headers=bv.headers1)
                for proc in psutil.process_iter():
                    if proc.name() == "Preview":
                        proc.kill()
                break
            else:
                print('其他：', qrcodeData)
                break
            time.sleep(2)
        session.cookies.save()
    return session


if __name__ == '__main__':
    checkLogin()
