import asyncio
import http.cookiejar as cookielib
import http.cookies
import os
import sys
import threading
import time

import aiohttp
import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QCursor, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QLineEdit, QTextEdit

import src.login as slogin
import src.varlist as bv
from src.bdmapi import getDanmu

# 直播间ID的取值看直播间URL
bv.room_id = 13233348


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
            'color': '16777215',
            'fontsize': '25',
            'mode': '1',
            'msg': self.input.text(),
            'rnd': str(int(time.time())),
            'roomid': bv.room_id,
            'csrf_token': bv.csrf,
            'csrf': bv.csrf,
            'bubble': '0'
        }
        sendUrl = 'https://api.live.bilibili.com/msg/send'
        session = requests.session()
        session.cookies = cookielib.LWPCookieJar(filename=bv.cookiePath)
        session.cookies.load(ignore_discard=True)
        request = session.post(sendUrl, data=postData)
        print(request.text)
        self.input.clear()

    def addLabel(self):
        self.label = QLabel("", self)
        self.label.setStyleSheet(" background-color: rgba(255,255,255,0.4);")
        self.label.move(35, 5)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.mouseReleaseEvent = self.stopMove
        self.label.mouseDoubleClickEvent = self.closeWindow
        self.label.mouseMoveEvent = self.startMove
        self.label.setFixedSize(180, 8)

    def addInput(self):
        self.input = QLineEdit(self)
        self.input.setGeometry(5, 455, 240, 20)
        self.input.setStyleSheet("""
                            background-color: rgba(255,255,255,0.5);
                            color:#000000;
                        """)
        self.input.returnPressed.connect(self.sendMessage)

    def addMessageView(self):
        self.messageView = QTextEdit(self)
        self.messageView.setGeometry(5, 18, 240, 435)  # Adjust the position and size as needed
        self.messageView.setReadOnly(True)  # Make it read-only
        self.messageView.setHtml("")

    def addShowView(self):
        self.showView = QTextEdit(self)
        self.showView.setGeometry(5, 475, 240, 25)  # Adjust the position and size as needed
        self.showView.setReadOnly(True)  # Make it read-only
        self.showView.setHtml("<span style='color:#54AEFF'>高能用户数:获取中 在线数:获取中</span>")
        self.showView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def sm(self, m):
        self.messageView.append(str(m))
        self.messageView.ensureCursorVisible()

    def __init__(self):
        super().__init__()
        self.label = None
        self.input = None
        self.messageView = None
        self.showView = None
        self.worker = Worker()
        self.worker.signal.connect(self.update)
        self.worker.start()

        self.addLabel()
        self.addInput()
        self.addMessageView()
        self.addShowView()
        # 创建一个QLabel对象

        # 调整label的大小以适应文本
        self.setFixedSize(250, 500)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 90);color:#ffffff;")

    @pyqtSlot(str)
    def update(self, data):
        # Update the widget with the number
        self.sm(data)
        self.showView.setHtml(
            "<span style='color:#54AEFF'>高能用户数:" + bv.highRankCount + " 在线数:" + bv.onlineCount + "</span>")


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


if __name__ == '__main__':
    if len(sys.argv) > 1:
        bv.room_id = sys.argv[1]
    # 初始化登陆
    slogin.checkLogin()
    # 创建一个新的事件循环
    loop = asyncio.new_event_loop()
    # 创建一个新的线程来运行事件循环
    t = threading.Thread(target=run_in_new_thread, args=(loop, getDanmu()))
    t.start()

    app = QApplication([])
    app.setWindowIcon(QIcon(QPixmap("src/s.ico")))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
