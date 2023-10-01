import http.cookiejar as cookielib
import http.cookies

import aiohttp
import requests

import bdm.blivedm as blivedm
import bdm.blivedm.models.web as web_models
import src.varlist as bv


async def getDanmu():
    init_session()
    try:
        await run_single_client()
    finally:
        await bv.session.close()


def init_session():
    cookie_jar = http.cookiejar.LWPCookieJar(bv.cookiePath)
    cookie_jar.load()
    cookies = requests.utils.dict_from_cookiejar(cookie_jar)
    bv.csrf = cookies["bili_jct"]
    bv.session = aiohttp.ClientSession()
    bv.session.cookie_jar.update_cookies(cookies)


async def run_single_client():
    client = blivedm.BLiveClient(bv.room_id, session=bv.session)
    handler = MyHandler()
    client.set_handler(handler)

    client.start()
    try:
        await client.join()
    finally:
        await client.stop_and_close()


class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()

    def setMessage(self, m):
        bv.mutex.lock()
        try:
            # 在这里访问你的数据
            bv.messageData.append(m)
        finally:
            # 释放锁
            bv.mutex.unlock()

    #
    # # 入场消息回调
    def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
        if command["data"]["msg_type"] == 1:
            uname = command["data"].get("uname", "默认用户名")
            data = str(uname + "进入了直播间")
            self.setMessage("<span style='color:#999999'>" + data + "</span>")
        else:
            uname = command["data"].get("uname", "默认用户名")
            data = str(uname + "关注了直播间")
            self.setMessage("<span style='color:#f2c55c'>" + data + "</span>")

    def __like_info_v3_click_callback(self, client: blivedm.BLiveClient, command: dict):
        uname = command["data"].get("uname", "默认用户名")
        data = str(uname + "点赞了直播间")
        self.setMessage("<span style='color:#F58198'>" + data + "</span>")

    def __online_rank_count_callback(self, client: blivedm.BLiveClient, command: dict):
        bv.highRankCount = str(command["data"]["count"])
        if "online_count" in command["data"]:
            bv.onlineCount = str(command["data"]["online_count"])

    _CMD_CALLBACK_DICT["INTERACT_WORD"] = __interact_word_callback
    _CMD_CALLBACK_DICT["LIKE_INFO_V3_CLICK"] = __like_info_v3_click_callback
    _CMD_CALLBACK_DICT["ONLINE_RANK_COUNT"] = __online_rank_count_callback
    """def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
        print(f'[{client.room_id}] 心跳')"""

    def _on_danmaku(
        self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage
    ):
        prefixData = ""
        if message.medal_name:
            mcolor = str(hex(message.mcolor)).replace("0x", "")
            ulevel_color = str(hex(message.ulevel_color)).replace("0x", "")
            if len(mcolor) < 6:
                mcolor = "0" + mcolor
            if len(ulevel_color) < 6:
                ulevel_color = "0" + ulevel_color
            prefixData = (
                "<span style='display:block;color:#ffffff;background-color:#"
                + mcolor
                + "'>"
                + str(message.medal_name)
                + "</span><span style='display:block;color:#ffffff;background-color:#"
                + ulevel_color
                + "'>"
                + str(message.medal_level)
                + "</span>"
            )
        data = f"{prefixData} {message.uname}：{message.msg}"
        self.setMessage(data)

    def _on_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
        global window
        if message.coin_type == "gold":
            metal = "金"
        else:
            metal = "银"

        data = (
            f'<span style="color:red">{message.uname} 赠送{message.gift_name}x{message.num}'
            f" （{metal}瓜子x{message.total_coin}）</span>"
        )
        self.setMessage(data)

    def _on_buy_guard(
        self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage
    ):
        data = f"[{client.room_id}] {message.username} 购买{message.gift_name}"
        self.setMessage(data)

    def _on_super_chat(
        self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage
    ):
        data = f"[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}"
        self.setMessage(data)
