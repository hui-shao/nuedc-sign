import os
import sys
import time
import traceback
from typing import Any, MutableMapping

import toml

from utils.avalon import Avalon
from utils.http_req import HttpReq
from utils.pushplus_tool import PushPlus
from utils.tgpush_tool import TgPushTool

PUSH_CHANNEL = "TG"  # 可选项: "TG", "PUSHPLUS"


class NuedcSign:
    def __init__(self):
        self.config = self.read_config()
        if not self.config:
            exit(0)
        self.user = self.config["user"]
        self.push_plus_token = self.config["push_plus"]["push_plus_token"]
        self.tg_bot_token = self.config["tg_push"]["tg_bot_token"]
        self.tg_chat_id = self.config["tg_push"]["tg_chat_id"]
        self.tg_push = TgPushTool(self.tg_bot_token, self.tg_chat_id)
        self.debug = self.config["common"]["debug"]
        self.r = HttpReq(self.user["cookie"])

    def run(self):
        Avalon.info("Start Running...")
        url = "https://www.nuedc-training.com.cn/index/mall/sign"
        retry_n = 0
        while 1:
            if self.debug:
                Avalon.debug_info(f"Current Retry N = {retry_n}")
            if retry_n >= 3:
                Avalon.error("达到最大重试次数, 退出")
                self.uni_push("电子设计竞赛网签到异常", "达到最大重试次数, 退出")
                break
            res = self.r.requests("get", url)
            res_dict = res.json()
            if self.debug:
                Avalon.debug_info(f"Response: {res_dict}")
            if res_dict["status"] == 0:
                Avalon.info("签到成功-今天已经签到过啦")
                self.uni_push("签到成功-电子设计竞赛网",
                              f"已经签到过啦\n\n当前已连续签到: {res_dict['data']['sign_count']} 天", )
                break
            elif res_dict["status"] == 1:
                Avalon.info("签到成功-今天首次签到")
                self.uni_push("签到成功-电子设计竞赛网",
                              f"今天签到成功\n\n当前已连续签到: {res_dict['data']['sign_count']} 天", )
                break
            elif res_dict["status"] == 2:
                Avalon.warning("签到失败 需要登陆")
                self.uni_push("签到异常-电子设计竞赛网",
                              f"需要登陆\n\n返回信息:\n\n code: {res_dict['status']}")
                break
            else:
                Avalon.warning("签到可能失败 未定义返回码")
                Avalon.warning(f"code: {res_dict['status']} info: {res_dict['info']}")
                if retry_n == 2:
                    self.uni_push("签到异常-电子设计竞赛网",
                                  f"返回信息:\n\n code: {res_dict['status']}\n\ninfo: {res_dict['info']}")
                    break
                else:
                    Avalon.warning("重试中....")
                    retry_n += 1
                    time.sleep(3)
                    continue
        Avalon.info("Finished.")

    def uni_push(self, title: str, content: str):
        if PUSH_CHANNEL == "TG":
            if not self.tg_bot_token or not self.tg_chat_id:
                Avalon.warning("TG Bot Token 或 Chat ID 未配置，跳过 TG 推送")
                return
            self.tg_push.send_tgmsg(f"{title}\n\n{content}")
        elif PUSH_CHANNEL == "PUSHPLUS":
            push_plus_token = sign.push_plus_token
            if not push_plus_token:
                Avalon.warning("Push Plus Token 未配置，跳过 Push Plus 推送")
                return
            PushPlus.send(push_plus_token, title, content)
        else:
            Avalon.error(f"未知的推送渠道: {PUSH_CHANNEL}, 无法推送消息")

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
