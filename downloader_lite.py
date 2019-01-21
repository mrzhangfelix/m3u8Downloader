#coding: utf-8

import requests
import urllib.parse
import os
import time
import sys

_dir=''
_videoName=''
def get_session( pool_connections, pool_maxsize, max_retries):
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_maxsize, max_retries=max_retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def show_progress(percent):
    bar_length=50
    hashes = '#' * int(percent * bar_length)
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rPercent: [%s] %.2f%%"%(hashes + spaces, percent*100))
    sys.stdout.flush()

def start( m3u8_url, dir, videoName):
    global _dir
    _dir=dir
    if dir and not os.path.isdir(dir):
        os.makedirs(dir)
    global _videoName
    _videoName=videoName
    r = session.get(m3u8_url, timeout=10)
    if r.ok:
        body = r.content.decode()
        if body:
            ts_list=[]
            body_list=body.split('\n')
            for n in body_list:
                if n and not n.startswith("#"):
                    ts_list.append(urllib.parse.urljoin(m3u8_url, n.strip()))
            if ts_list:
                ts_total = len(ts_list)
                print('ts的总数量为：'+str(ts_total)+'个')
                # 下载ts文件
                print('开始下载文件')
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                res=download(ts_list)
                print('')
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                if res:
                    # 整合ts文件
                    print('\n开始整合文件')
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    merge_file(ts_list)
                    print('')
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                else:
                    print('下载失败')
    else:
        print(r.status_code)

def get_real_url( m3u8_url):
    r = session.get(m3u8_url, timeout=10)
    if r.ok:
        body = r.content.decode()
        if body:
            ts_url=''
            body_list=body.split('\n')
            for n in body_list:
                if n and not n.startswith("#"):
                    ts_url=urllib.parse.urljoin(m3u8_url, n.strip())
            if ts_url!='':
                print('真实地址为'+ts_url)
                return ts_url
    else:
        print(r.status_code)

def download(ts_list):
    # begin用于断点续传，设置起始位置;
    ts_total=len(ts_list)
    for i in range(0,ts_total) :
        url = ts_list[i]
        index = i
        retry = 3
        percent = i/ts_total
        show_progress(percent)
        while retry:
            try:
                r = session.get(url, timeout=20)
                if r.ok:
                    file_name = url.split('/')[-1].split('?')[0]
                    # print(file_name)
                    with open(os.path.join(_dir, file_name), 'wb') as f:
                        f.write(r.content)
                    break
            except Exception as e:
                print(e)
                retry -= 1
        if retry == 0 :
            print('[FAIL]%s' % url)
            # 失败的节点，用于标注下一次断点续传
            print(index)
            return False
    return True

# 将TS文件整合在一起
def merge_file(ts_list):
    index = 0
    outfile = ''
    ts_total = len(ts_list)
    while index < ts_total:
        file_name = ts_list[index].split('/')[-1].split('?')[0]
        # print(file_name)
        percent = index / ts_total
        show_progress(percent)
        infile = open(os.path.join(_dir, file_name), 'rb')
        if not outfile:
            global _videoName
            if _videoName=='':
                _videoName=file_name.split('.')[0]+'_all'
            outfile = open(os.path.join(_dir, _videoName+'.'+file_name.split('.')[-1]), 'wb')
        outfile.write(infile.read())
        infile.close()
        # 删除临时ts文件
        os.remove(os.path.join(_dir, file_name))
        index += 1
    if outfile:
        outfile.close()

def main():
    url='https://bobo.okokbo.com/20171122/twzzAPDq/index.m3u8'
    real_url=get_real_url(url)
    # dir='D:/felix/download/8/2'
    # videoName='8-2'
    # start(real_url,dir,videoName)

if __name__ == '__main__':
    session = get_session(50, 50, 3)
    main()
