# coding: utf-8

import urllib.parse
import sys

from client import sessionUtil


# 展示进度条
def show_progress(percent):
    bar_length = 50
    hashes = '#' * int(percent / 100 * bar_length)
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rPercent: [%s] %.2f%%" % (hashes + spaces, percent))
    sys.stdout.flush()


# 用于获取最新队列
def get_real_url(m3u8_url):
    r = sessionUtil.session.get(m3u8_url, timeout=10)
    if r.ok:
        body = r.content.decode()
        if body:
            ts_url = ''
            body_list = body.split('\n')
            for n in body_list:
                if n and not n.startswith("#"):
                    ts_url = urllib.parse.urljoin(m3u8_url, n.strip())
            if ts_url != '':
                print('真实地址为' + ts_url)
                return ts_url
    else:
        print(r.status_code)
