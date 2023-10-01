from typing import *

import aiohttp
from PyQt6.QtCore import QMutex

room_id = 0
session: Optional[aiohttp.ClientSession] = None
mutex = QMutex()
messageData = []
csrf = ""
onlineCount = "获取中"
highRankCount = "获取中"
cookiePath = "cookies.txt"
headers1 = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    'Referer': "https://www.bilibili.com/"}
headers2 = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    'Host': 'passport.bilibili.com',
    'Referer': "https://passport.bilibili.com/login"}
