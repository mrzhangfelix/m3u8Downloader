#coding: utf-8

import requests
import urllib.parse
import os
import sys
import queue
import threading

threadListSize = 48
queueSize = 96
_ts_total = 0
_dir=''
_videoName=''
_queueLock = threading.Lock()
_workQueue = queue.Queue(queueSize)
_threadList=[]

for i in range(threadListSize):
    _threadList.append("Thread-"+str(i))
# threadList = ["Thread-1", "Thread-2", "Thread-3"]

def get_session( pool_connections, pool_maxsize, max_retries):
    '''构造session'''
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_maxsize, max_retries=max_retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
session = get_session(50, 50, 3)

# 填充队列
def fillQueue(nameList):
    _queueLock.acquire()
    for word in nameList:
        _workQueue.put(word)
        nameList.remove(word)
        if _workQueue.full():
            break
    _queueLock.release()

# 展示进度条
def show_progress(percent):
    bar_length=50
    hashes = '#' * int(percent * bar_length)
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rPercent: [%s] %.2f%%"%(hashes + spaces, percent*100))
    sys.stdout.flush()

# 将TS文件整合在一起
def merge_file(ts_list):
    index = 0
    outfile = ''
    while index < _ts_total:
        file_name = ts_list[index].split('/')[-1].split('?')[0]
        # print(file_name)
        percent = (index + 1) / _ts_total
        show_progress(percent)
        file_path=os.path.join(_dir, file_name)
        if os.path.exists(file_path):
            infile = open(file_path, 'rb')
            if not outfile:
                global _videoName
                if _videoName=='':
                    _videoName=file_name.split('.')[0]+'_all'
                outfile = open(os.path.join(_dir, _videoName+'.mp4'), 'wb')
            outfile.write(infile.read())
            infile.close()
            # 删除临时ts文件
            os.remove(os.path.join(_dir, file_name))
        index += 1
    if outfile:
        outfile.close()

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

