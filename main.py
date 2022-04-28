import os
import sys
import time
import traceback
from typing import Any, MutableMapping

import toml

from utils.avalon import Avalon
from utils.http_req import HttpReq
from utils.pushplus_tool import PushPlus


class NuedcSign:
    def __init__(self):
        self.config = self.read_config()
        if not self.config:
            exit(0)
        self.user = self.config["user"]
        self.push_token = self.config["push"]["push_token"]
        self.debug = self.config["common"]["debug"]
        self.r = HttpReq(self.user["cookie"])

    def run(self):
        Avalon.info("Start Running...")
        url = "https://www.nuedc-training.com.cn/index/mall/sign"
        retry_n = 0
        while 1:
            if retry_n >= 3:
                Avalon.error("达到最大重试次数, 退出")
                PushPlus.send(self.push_token, "电子设计竞赛网签到异常", "达到最大重试次数, 退出", "markdown")
                break
            res = self.r.requests("get", url)
            res_dict = res.json()
            if res_dict["status"] == 0:
                PushPlus.send(self.push_token, "签到成功-电子设计竞赛网", f"返回信息:\n\n 连续签到: {res_dict['data']['sign_count']} 天",
                              "markdown")
                break
            elif res_dict["status"] == 2:
                PushPlus.send(self.push_token, "签到异常-电子设计竞赛网",
                              f"需要登陆\n\n返回信息:\n\n code: {res_dict['status']}", "markdown")
                break
            else:
                Avalon.error("未知异常")
                time.sleep(3)
                if retry_n == 2:
                    PushPlus.send(self.push_token, "签到异常-电子设计竞赛网",
                                  f"返回信息:\n\n code: {res_dict['status']}\n\ninfo: {res_dict['info']}", "markdown")
                    break
                else:
                    retry_n += 1
                    continue
        Avalon.info("Finished.")

    @staticmethod
    def read_config() -> MutableMapping[str, Any]:
        Avalon.info("读取配置文件中...")
        config_file = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = toml.load(f)
        except IOError:
            Avalon.error(f"无法加载 {config_file}, 请检查文件是否存在, 文件名是否正确")
            return {}
        except toml.TomlDecodeError:
            Avalon.error(f"载入 {config_file}错误, 请检查配置文件内容是否规范无误")
            Avalon.error(traceback.format_exc(3))
            return {}
        except Exception:
            Avalon.error(f"无法加载 {config_file}, 其他错误\n")
            Avalon.error(traceback.format_exc(3))
            return {}
        else:
            Avalon.info("配置文件读取成功")
            return config


if __name__ == '__main__':
    try:
        os.chdir(sys.path[0])
        sign = NuedcSign()
        sign.run()
    except KeyboardInterrupt:
        Avalon.warning("捕获 KeyboardInterrupt, 退出")
    except Exception:
        Avalon.error(f"其他错误: {traceback.format_exc(3)}")
