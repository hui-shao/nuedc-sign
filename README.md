# 签到助手(全国大学生电子设计竞赛网)

<p align="left">
<img src="https://img.shields.io/github/license/hui-shao/nuedc-sign?style=flat">
<img src="https://img.shields.io/github/issues/hui-shao/nuedc-sign?style=flat">
<img src="https://img.shields.io/badge/requirement-python3-blue?style=flat">
</p>
用于每日签到领取赫兹币

### 使用方式

1. 安装 python 后，切换到项目目录用下列命令安装依赖。

   ```bash
   pip install -r requirements.txt
   ```

2. 将 `config.toml.example` 复制一份并重命名为 `config.toml`

3. 编辑 `config.toml` 文件，填写从网站上获取的 `cookie`。

4. `push_token` 为 [push_plus](https://www.pushplus.plus/) 的推送 token，可不填。

5. 运行一次试试看。

   ```bash
   python main.py
   ```

### 部署方式

- Crontab

  ```
  15 9 * * * python3 -u "/root/nuedc_sign/main.py" >> /root/nuedc_sign/log.txt 2>&1
  ```

- Github Action

- Etc....

这些都可以，emm，自行解决吧。

