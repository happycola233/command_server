# HTTP 远程执行控制台命令

这是一个简单的命令执行服务器脚本，通过 HTTP 请求接收命令，并执行该命令返回结果。

## 功能

- 提供基于 HTTP 的命令执行功能。
- 可选择是否启用密码验证。
- 支持基本认证，需要提供用户名和密码进行验证。
- 执行命令并返回执行结果。
- 提供简单的命令执行结果展示页面。

## 用法

```shell
用法: command_server.py [-h] [-port PORT] [-auth] [-username USERNAME] [-password PASSWORD]
Command Server

options:
  -h, --help          show this help message and exit
  -port PORT          端口号（默认8001）
  -auth               启用密码验证
  -username USERNAME  验证的用户名
  -password PASSWORD  验证的密码
```

## 参与贡献
非常感谢用户“[wuziqian211](https://space.bilibili.com/425503913)”的大力支持
