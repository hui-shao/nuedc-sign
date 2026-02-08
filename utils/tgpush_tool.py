# -*- coding: UTF-8 -*-
# @Time    : 2025/08/08
# @Author  : Hui-Shao

import logging
import sys
import time
import traceback
from datetime import datetime

import requests


class TgPushTool:
    def __init__(self, bot_token: str, chat_id: str):
        """
        Args:
            bot_token: (str) Telegram Bot Token
            chat_id: (str) Telegram Chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.logger = self._set_logger()

    def send_tgmsg(self, content: str, bot_token: str = None, chat_id: str = None):
        """
        发送 Telegram 消息

        Args:
            content: (str) 消息正文
            bot_token: (str) 临时覆盖 Telegram Bot Token
            chat_id: (str) 临时覆盖 Telegram Chat ID
        """
        token = bot_token if bot_token is not None else self.bot_token
        chat = chat_id if chat_id is not None else self.chat_id
        if not token or not chat:
            self.logger.warning("TG Bot Token 或 Chat ID 未配置，跳过推送")
            return 1
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat,
            "text": content,
            "parse_mode": "Markdown"
        }
        retry_n = 1
        while True:
            if retry_n > 5:
                self.logger.error("TG 推送达到最大重试次数, 退出")
                break
            try:
                res = requests.post(url, data=data, timeout=10)
            except requests.exceptions.SSLError:
                self.logger.error("SSL 错误, 2s后重试 -> SSLError: An SSL error occurred.")
                time.sleep(2)
            except requests.exceptions.ConnectTimeout:
                self.logger.error(
                    "建立连接超时, 5s后重试 -> ConnectTimeout: The request timed out while trying to connect to the remote server.")
                time.sleep(5)
            except requests.exceptions.ReadTimeout:
                self.logger.error(
                    "读取数据超时, 3s后重试 -> ReadTimeout: The server did not send any data in the allotted amount of time.")
                time.sleep(3)
            except requests.exceptions.ConnectionError:
                self.logger.error(f"{traceback.format_exc(3)}")
                self.logger.error("建立连接错误, 5s后重试")
                time.sleep(5)
            except requests.exceptions.RequestException:
                self.logger.error(f"{traceback.format_exc(3)}")
                self.logger.error("其他网络连接错误, 5s后重试")
                time.sleep(5)
            except KeyboardInterrupt:
                self.logger.warning("捕获到 KeyboardInterrupt, 退出")
                return False
            except Exception as e:
                sign = '=' * 60 + '\n'
                print(f'{sign}>>> Time: \t{datetime.now()}\n>>> "Detail": \t{e}')
                print(f'{sign}{traceback.format_exc()}{sign}')
            else:
                if res.status_code == 200:
                    self.logger.info("[TG] 消息推送成功！")
                    return True
                else:
                    self.logger.warning(f"[TG] 消息推送失败，状态码: {res.status_code}，返回: {res.text}")
                    return False
            finally:
                retry_n += 1

    def set_token(self, bot_token: str):
        """设置/更新 Bot Token"""
        self.bot_token = bot_token

    def set_chat_id(self, chat_id: str):
        """设置/更新 Chat ID"""
        self.chat_id = chat_id

    @staticmethod
    def _set_logger() -> logging.Logger:
        _logger = logging.getLogger("TGPush")
        _logger.setLevel(logging.DEBUG)
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setLevel(logging.INFO)
        _format = logging.Formatter('%(name)s:%(levelname)s -> %(message)s')
        sh.setFormatter(_format)
        _logger.addHandler(sh)
        return _logger
