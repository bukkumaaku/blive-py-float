import asyncio
import http.cookiejar as cookielib
import http.cookies
import os
import sys
import threading
import time
import urllib.parse

import aiohttp
import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QCursor, QIcon, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QTextEdit, QFrame

import src.login as slogin
import src.varlist as bv
from src.bdmapi import getDanmu

# 直播间ID的取值看直播间URL
bv.room_id = 7777


class Worker(QThread):
    signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            time.sleep(0.1)
            # 获取锁
            bv.mutex.lock()
            try:
                # 在这里访问你的数据
                if len(bv.messageData) > 0:
                    self.signal.emit(bv.messageData.pop(0))
            finally:
                # 释放锁
                bv.mutex.unlock()


# 创建窗口
class MainWindow(QMainWindow):
    ix = 100
    iy = 100
    isR = True

    def startMove(self, event):
        wx = self.pos().x()
        wy = self.pos().y()
        # 获取鼠标的位置
        x = QCursor.pos().x()
        y = QCursor.pos().y()
        if self.isR:
            self.isR = False
            self.ix = x - wx
            self.iy = y - wy
        self.move(x - self.ix, y - self.iy)

    def closeWindow(self, event):
        os._exit(0)

    def stopMove(self, event):
        self.isR = True
        self.ix = 0
        self.iy = 0

    def sendMessage(self):
        postData = {
            "color": "16777215",
            "fontsize": "25",
            "mode": "1",
            "msg": self.input.text(),
            "rnd": str(int(time.time())),
            "roomid": bv.room_id,
            "csrf_token": bv.csrf,
            "csrf": bv.csrf,
            "bubble": "0",
        }
        sendUrl = "https://api.live.bilibili.com/msg/send"
        session = requests.session()
        session.cookies = cookielib.LWPCookieJar(filename=bv.cookiePath)
        session.cookies.load(ignore_discard=True)
        request = session.post(sendUrl, data=postData)
        print(request.text)
        self.input.clear()

    def addLabel(self):
        self.label = QFrame(self)
        self.label.setGeometry(50, 7, 150, 5)
        self.label.setStyleSheet("background-color:rgba(255,255,255,0.4);")
        self.label.mouseReleaseEvent = self.stopMove
        self.label.mouseDoubleClickEvent = self.closeWindow
        self.label.mouseMoveEvent = self.startMove

    def addInput(self):
        self.input = QLineEdit(self)
        self.input.setGeometry(5, 455, 240, 20)
        self.input.setStyleSheet("background-color: rgba(255,255,255,0.5);color:#000000;border-radius:4px;")
        self.input.returnPressed.connect(self.sendMessage)
        self.input.setPlaceholderText('此处输入回复……')

    def addMessageView(self):
        self.messageView = QWebEngineView(self)
        self.messageView.setGeometry(5, 18, 240, 435)
        with open("src/main.html", "r") as f:
            content = f.read()
        self.messageView.setHtml(content)
        self.messageView.setStyleSheet("background-color: rgba(255,255,255,0);")

    def addShowView(self):
        self.showView = QTextEdit(self)
        self.showView.setGeometry(
            5, 475, 240, 25
        )  # Adjust the position and size as needed
        self.showView.setReadOnly(True)  # Make it read-only
        self.showView.setHtml("<span style='color:#54AEFF'>高能用户数:获取中 在线数:获取中</span>")
        self.showView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.showView.setStyleSheet("background-color: rgba(255,255,255,0);")

    def sm(self, m):
        self.messageView.page().runJavaScript(
            f"addMessage('<span style=\"font-size:0.8rem;line-height:1rem;margin:3px 0px 2px 0px;\">{urllib.parse.quote(m)}</span>')")
        # self.messageView.append(f"<div style='margin-bottom:3px;margin-top:3px;'>{str(m)}</div>")
        # self.messageView.ensureCursorVisible()

    def addFrame(self):
        self.baseFrame = QFrame(self)
        self.baseFrame.setGeometry(0, 0, 250, 500)
        self.baseFrame.setStyleSheet(
            "background-color: rgba(30, 30, 30, 0.7);color:#ffffff;border:1px solid #777777;border-radius:5px;")

    def __init__(self):
        super().__init__()
        self.baseFrame = None
        self.label = None
        self.input = None
        self.messageView = None
        self.showView = None
        self.worker = Worker()
        self.worker.signal.connect(self.update)
        self.worker.start()
        self.addFrame()
        self.addLabel()
        self.addInput()
        self.addMessageView()
        self.addShowView()

        self.setFixedSize(250, 500)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("color:#ffffff;border-radius:10px;background-color:transparent;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    @pyqtSlot(str)
    def update(self, data):
        self.sm(data)
        self.showView.setHtml(
            "<span style='color:#54AEFF'>高能用户数:"
            + bv.highRankCount
            + " 在线数:"
            + bv.onlineCount
            + "</span>"
        )


def init_session():
    cookie_jar = http.cookiejar.LWPCookieJar(bv.cookiePath)
    cookie_jar.load()
    cookies = requests.utils.dict_from_cookiejar(cookie_jar)
    bv.csrf = cookies["bili_jct"]
    bv.session = aiohttp.ClientSession()
    bv.session.cookie_jar.update_cookies(cookies)


def run_in_new_thread(loop1, coro):
    asyncio.set_event_loop(loop1)
    loop.run_until_complete(coro)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        bv.room_id = sys.argv[1]
    # 初始化登陆
    slogin.checkLogin()
    # 创建一个新的事件循环
    loop = asyncio.new_event_loop()
    # 创建一个新的线程来运行事件循环
    t = threading.Thread(target=run_in_new_thread, args=(loop, getDanmu()))
    t.start()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(QPixmap("src/s.ico")))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
