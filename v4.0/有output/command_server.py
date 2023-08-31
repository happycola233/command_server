# -*- coding: utf-8 -*-

'''
如果使用pyinstaller打包时使用-w或--windowed或--noconsole参数，即Do not provide a console window for standard i/o.
请找到文件：{Python安装目录}\Lib\http\server.py（通常是%LOCALAPPDATA%\Programs\Python\Python???\Lib\http\server.py）
替换文件中的所有“sys.stderr.write”为“print”
否则在无控制台的情况下，程序会出现“AttributeError: 'NoneType' object has no attribute 'write'”错误
'''

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer # 导入 HTTP 服务器相关模块
from base64 import b64decode # 导入 Base64 解码模块
from functools import partial # 导入部分函数应用模块
from urllib.parse import unquote # 导入 URL 解码模块
import subprocess # 导入子进程模块
import argparse # 导入命令行参数解析模块
import socket # 获取 IPv4 地址
import traceback # 获取详细的报错信息

# 定义一个处理 HTTP 请求的处理程序类
class AuthHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.require_auth = kwargs.pop("require_auth", False) # 是否需要密码验证
        self.username = kwargs.pop("username", None) # 用户名
        self.password = kwargs.pop("password", None) # 密码
        super().__init__(*args, **kwargs)
    
    def do_AUTHHEAD(self):
        self.send_response(401) # 发送“401 未授权”的响应
        self.send_header("WWW-Authenticate", 'Basic realm="Command Server"') # 发送包含 Basic 认证领域的标头
        self.send_header("Content-type", "text/html")
        self.end_headers()
    
    def do_GET(self):
        if self.require_auth:
            auth_header = self.headers.get("Authorization") # 获取请求头部中的 Authorization 标头
            if auth_header is None or "Basic" not in auth_header:
                self.do_AUTHHEAD() # 如果没有 Authorization 标头或不是 Basic 认证，则发送未授权的响应
                self.wfile.write(b"Unauthorized") # 发送未授权的响应
                return
            else:
                encoded_credentials = auth_header.split(" ")[1] # 获取认证信息
                decoded_credentials = b64decode(encoded_credentials).decode("utf-8") # Base64 解码认证信息
                username, password = decoded_credentials.split(":") # 提取用户名和密码
                if username == self.username and password == self.password:
                    self.process_command() # 验证通过，执行命令
                else:
                    self.do_AUTHHEAD() # 验证失败，发送未授权的响应
                    self.wfile.write(b"Unauthorized") # 返回未授权消息
        else:
            self.process_command() # 不需要密码验证，直接执行命令
    
    def process_command(self):
        command_input = unquote(self.path[1:]) # 获取命令，并解码 URL 中的特殊字符
        try:
            command_output = subprocess.check_output(command_input, shell=True, stderr=subprocess.STDOUT, universal_newlines=True) # 执行命令并获取结果
            self.send_response(200) # 发送成功响应
            self.send_header("Content-type", "text/html; charset=utf-8") # 设置响应的 Content-Type 为 HTML
            self.end_headers()
            response_content = generate_html(command_input, command_output)
            self.wfile.write(response_content.encode("utf-8")) # 返回命令执行结果
        except subprocess.CalledProcessError as e:
            command_output = e.output
            self.send_response(500) # 发送服务器内部错误的响应
            self.send_header("Content-type", "text/html; charset=utf-8") # 设置响应的 Content-Type 为 HTML
            self.end_headers()
            response_content = generate_html(command_input, command_output)
            self.wfile.write(response_content.encode("utf-8")) # 返回错误消息
        except:
            command_output = traceback.format_exc()
            self.send_response(500) # 发送服务器内部错误的响应
            self.send_header("Content-type", "text/html; charset=utf-8") # 设置响应的 Content-Type 为 HTML
            self.end_headers()
            response_content = generate_html(command_input, command_output)
            self.wfile.write(response_content.encode("utf-8")) # 返回错误消息

# 定义一个命令服务器类
class CommandServer:
    def __init__(self, host, port, require_auth, username=None, password=None):
        self.server_address = (host, port) # 服务器地址
        self.require_auth = require_auth # 是否需要密码验证
        self.username = username # 用户名
        self.password = password # 密码
    
    def run(self):
        server = ThreadingHTTPServer(self.server_address, partial(AuthHandler, require_auth=self.require_auth, username=self.username, password=self.password)) # 创建多线程 HTTP 服务器
        
        print(f"Command server is running on http://localhost:{self.server_address[1]} (http://{socket.gethostbyname(socket.gethostname())}:{self.server_address[1]})")
        print()
        server.serve_forever() # 启动服务器，开始监听和处理请求

def generate_html(command_input, command_output):
    css_code = """
* {
  font-family: Lato, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  max-width: 100%;
  overflow-wrap: anywhere;
  text-align: justify;
  transition: all 0.5s;
}
html {
  height: 100%;
}
body {
  background: #fff;
  color: #222;
  margin: 0;
  min-height: 100%;
}
header {
  background: #fff;
  box-shadow: 0 0 5px #777;
  position: sticky;
  top: 0;
  z-index: 10;
}
div.header {
  align-items: center;
  font-size: 24px;
  margin: 0 auto;
  padding: 15px 0;
  width: 1200px;
}
div.header  > span.description {
  color: #777;
  font-size: 14px;
}
main {
  animation: 0.5s both zoomInDown;
  font-size: 20px;
  margin: 20px auto;
  padding: 10px;
  width: 1200px;
}
main.loading {
  animation-name: zoomOutUp;
  transform-origin: center bottom;
}
a, strong, label, input[type='submit'] {
  color: #09f;
}
a:hover, input[type='submit']:hover {
  color: #3bf;
}
a {
  text-decoration: underline dotted #333;
  text-decoration-thickness: 2px;
}
div.header a {
  text-decoration: none;
}
a:hover {
  text-decoration-color: #aaa;
}
form {
  margin: 0 0 10px;
  font-size: 20px;
}
input {
  background: inherit;
  border: 1px solid #09f;
  border-radius: 5px;
  box-sizing: content-box;
  color: inherit;
  height: 20px;
}
input:hover {
  background: #fff6;
  border-color: #3bf;
}
input[type='text']:focus {
  background: #fff6;
}
input[type='submit']:active {
  background: #ddd6;
}
pre {
  background: #333;
  border-radius: 10px;
  color: #ddd;
  font-family: consolas, Menlo, monospace, 'PingFang SC', 'Microsoft YaHei';
  font-size: 16px;
  overflow: auto;
  padding: 10px;
}
footer {
  color: #777;
  font-size: 16px;
  margin: 10px 10px 0;
  text-align: center;
}
@media (max-width: 1439px) {
  div.header, main {
    width: 900px;
  }
}
@media (max-width: 959px) {
  div.header {
    text-align: center;
    width: auto;
  }
  div.header > span.description {
    display: none;
  }
  main {
    margin: 10px;
    width: auto;
  }
}
@media (prefers-color-scheme: dark) {
  body {
    color: #ccc;
  }
  body, header {
    background: #222;
  }
  span.description, footer {
    color: #999;
  }
  a, strong, label, input[type='submit'] {
    color: #08e;
  }
  a:hover, input[type='submit']:hover {
    color: #3ae;
  }
  a {
    text-decoration-color: #aaa;
  }
  a:hover {
    text-decoration-color: #ccc;
  }
  input {
    border-color: #08e;
  }
  input:hover, input[type='text']:focus {
    background: #2226;
  }
  input:hover {
    border-color: #3ae;
  }
  input[type='submit']:active {
    background: #0006;
  }
}
@media only print {
  * {
    animation: none !important;
    -webkit-backdrop-filter: none !important;
    backdrop-filter: none !important;
    transition: none;
  }
  html {
    height: initial;
  }
  body, main {
    background: none !important;
  }
  body {
    color: #000;
    min-height: initial;
  }
  main {
    margin: 0;
  }
}

/* From animate.css - https://animate.style */
@keyframes zoomInDown {
  from {
    animation-timing-function: cubic-bezier(0.55, 0.055, 0.675, 0.19);
    opacity: 0;
    transform: scale3d(0.1, 0.1, 0.1) translate3d(0, -1000px, 0);
  }
  60% {
    animation-timing-function: cubic-bezier(0.175, 0.885, 0.32, 1);
    opacity: 1;
    transform: scale3d(0.475, 0.475, 0.475) translate3d(0, 60px, 0);
  }
}
@keyframes zoomOutUp {
  40% {
    animation-timing-function: cubic-bezier(0.55, 0.055, 0.675, 0.19);
    opacity: 1;
    transform: scale3d(0.475, 0.475, 0.475) translate3d(0, 60px, 0);
  }
  to {
    animation-timing-function: cubic-bezier(0.175, 0.885, 0.32, 1);
    opacity: 0;
    transform: scale3d(0.1, 0.1, 0.1) translate3d(0, -2000px, 0);
  }
}
"""
    js_code = """
'use strict';

// From pjax.js - https://github.com/MoOx/pjax
const replacePage = text => {
  const html = new DOMParser().parseFromString(text, 'text/html');
  ['title', 'main'].forEach(s => document.querySelector(s).innerHTML = html.querySelector(s).innerHTML);
};
const load = (url, event) => {
  event.preventDefault();
  loadPage(url);
};
const bindLoad = () => {
  document.querySelectorAll('a').forEach(a => {
    a.onclick = event => load(a.href, event);
    a.onkeyup = event => {
      event.code === 'Enter' && load(a.href, event);
    }
  });
  document.querySelectorAll('form').forEach(form => {
    form.onsubmit = event => load('/' + encodeURIComponent(document.querySelector('input#commandInput').value), event);
  });
};
const loadPage = async url => {
  document.querySelector('main').classList.add('loading');
  document.activeElement?.blur();
  try {
    const resp = await fetch(url);
    const text = await resp.text();
    history.pushState({ text }, '', resp.url);
    replacePage(text);
    bindLoad();
    document.querySelector('main').classList.remove('loading');
  } catch (e) {
    console.error(e);
    document.location.href = url;
  }
};
window.onpopstate = event => {
  document.activeElement?.blur();
  replacePage(event.state.text);
  bindLoad();
};
history.replaceState({ text: document.documentElement.outerHTML }, '');
bindLoad();"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <!-- 防止浏览器自动请求 favicon.ico 图标使程序出现意外的日志，但是在浏览器查看源代码时无效 -->
        <link rel="shortcut icon" href="data:,">
        <title>命令执行详情 - {encode_html(command_input)}</title>
        <style>{css_code}</style>
    </head>
    <body>
        <header>
            <div class="header"><a href="/">Command Server</a> <span class="description">执行控制台命令</span></div>
        </header>
        <main>
            <noscript>本页面需要启用 JavaScript 后才能正常运作。</noscript>
            <form>
              <input type="text" name="commandInput" id="commandInput" placeholder="请输入要执行的命令"> <input type="submit" id="exec" value="执行">
            </form>
            下面是命令执行详情。<br />
            <strong>执行指令：</strong>
            <pre>{encode_html(command_input)}</pre>
            <strong>返回结果：</strong>
            <pre>{encode_html(command_output)}</pre>
        </main>
        <footer>
            本脚本由 <a target="_blank" rel="noopener external nofollow noreferrer" href="https://space.bilibili.com/324042405">肥宅水水呀</a> 与 <a target="_blank" rel="noopener external nofollow noreferrer" href="https://space.bilibili.com/425503913">wuziqian211</a> 共同编写
        </footer>
        <script>{js_code}</script>
    </body>
</html>"""

def encode_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("\n", "<br />")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Command Server")
    parser.add_argument("-port", type=int, default=8001, help="端口号（默认8001）") # 端口号参数
    parser.add_argument("-auth", action="store_true", help="启用密码验证") # 启用密码验证参数
    parser.add_argument("-username", type=str, help="验证的用户名") # 用户名参数
    parser.add_argument("-password", type=str, help="验证的密码") # 密码参数
    return parser.parse_args() # 解析命令行参数

if __name__ == "__main__":
    args = parse_arguments() # 解析命令行参数
    server = CommandServer("0.0.0.0", args.port, args.auth, args.username, args.password) # 创建服务器实例
    server.run() # 运行服务器
