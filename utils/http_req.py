import time
import traceback
from urllib import parse

import requests

try:
    from utils.avalon import Avalon
except ModuleNotFoundError:
    from avalon import Avalon


# 自定义的HttpRequest模块
class HttpReq:
    def __init__(self, _cookie: str):
        self.cookie = str(_cookie).encode("utf-8")

    def requests(self, _method: str, _url: str, _data: dict = None, _param: dict = None,
                 _ex_hea: dict = None):
        url_parse = parse.urlparse(_url)
        data = _data
        param = _param
        hea = {
            "Host": url_parse.netloc,
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip,compress,br,deflate",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://www.nuedc-training.com.cn/index/mall/index"
        }
        if self.cookie:
            hea.update({"cookie": self.cookie})
        retry_n = 0
        while retry_n < 5:
            try:
                if _ex_hea:
                    hea.update(_ex_hea)
                if _method.upper() == 'GET':
                    res = requests.get(_url, data=data, params=param, headers=hea, timeout=(12.05, 72))
                elif _method.upper() == 'POST':
                    res = requests.post(_url, data=data, headers=hea, timeout=(12.05, 54))
                elif _method.upper() == 'PUT':
                    res = requests.put(_url, data=data, headers=hea, timeout=(12.05, 54))
                elif _method.upper() == 'DELETE':
                    res = requests.delete(_url, data=data, headers=hea, timeout=(12.05, 54))
                else:
                    Avalon.error('TypeError')
                    return None
            except requests.exceptions.SSLError:
                Avalon.error("SSL 错误, 2s后重试 -> SSLError: An SSL error occurred.")
                time.sleep(2)
            except requests.exceptions.ConnectTimeout:
                Avalon.error(
                    "建立连接超时, 5s后重试 -> ConnectTimeout: The request timed out while trying to connect to the remote server.")
                time.sleep(5)
            except requests.exceptions.ReadTimeout:
                Avalon.error(
                    "读取数据超时, 3s后重试 -> ReadTimeout: The server did not send any data in the allotted amount of time.")
                time.sleep(3)
            except requests.exceptions.ConnectionError:
                Avalon.error(f"{traceback.format_exc(3)}")
                Avalon.error("建立连接错误, 5s后重试", front="\n")
                time.sleep(5)
            except requests.exceptions.RequestException:
                Avalon.error(f"{traceback.format_exc(3)}")
                Avalon.error("其他网络连接错误, 5s后重试", front="\n")
                time.sleep(5)
            except KeyboardInterrupt:
                Avalon.warning("捕获到 KeyboardInterrupt, 退出", front="\n")
                return None
            else:
                return res
            retry_n += 1
            continue
        Avalon.error("达到最大重试次数, 退出", front="\n")
        return None
