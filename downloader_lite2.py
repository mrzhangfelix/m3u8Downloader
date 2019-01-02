#coding: utf-8

import requests
import urllib.parse
import os
import time
import sys
import queue
import threading

threadListSize = 8
queueSize = 16

_exitFlag = 0
_ts_total = 0
_count = 0
_dir=''
_videoName=''
_queueLock = threading.Lock()
_workQueue = queue.Queue(queueSize)
_threadList=[]
for i in range(threadListSize):
    _threadList.append("Thread-"+str(i))
# threadList = ["Thread-1", "Thread-2", "Thread-3"]

class downloadThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        # print ("开启线程：" + self.name + '\n', end='')
        download_data(self.q)
        # print ("退出线程：" + self.name + '\n', end='')

# 下载数据
def download_data(q):
    while not _exitFlag:
        _queueLock.acquire()
        if not _workQueue.empty():
            data = q.get()
            _queueLock.release()
            # print ("%s 使用了 %s" % (threadName, data) + '\n', end='')
            url = data
            retry = 3
            while retry:
                try:
                    r = session.get(url, timeout=20)
                    if r.ok:
                        file_name = url.split('/')[-1].split('?')[0]
                        # print(file_name)
                        with open(os.path.join(_dir, file_name), 'wb') as f:
                            f.write(r.content)
                        _queueLock.acquire()
                        global _count
                        _count = _count+1
                        show_progress(_count/_ts_total)
                        _queueLock.release()
                        break
                except Exception as e:
                    print(e)
                    retry -= 1
            if retry == 0 :
                print('[FAIL]%s' % url)
        else:
            _queueLock.release()

# 填充队列
def fillQueue(nameList):
    _queueLock.acquire()
    for word in nameList:
        _workQueue.put(word)
        nameList.remove(word)
        if _workQueue.full():
            break
    _queueLock.release()

# 构造session
def get_session( pool_connections, pool_maxsize, max_retries):
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_maxsize, max_retries=max_retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# 展示进度条
def show_progress(percent):
    bar_length=50
    hashes = '#' * int(percent * bar_length)
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rPercent: [%s] %.2f%%"%(hashes + spaces, percent*100))
    sys.stdout.flush()

def start( m3u8_url, dir, videoName):
    global _dir
    global _videoName
    global _ts_total
    if dir and not os.path.isdir(dir):
        os.makedirs(dir)
    _dir=dir
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
                _ts_total = len(ts_list)
                print('ts的总数量为：'+str(_ts_total)+'个')
                # 下载ts文件
                print('开始下载文件')
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                res=download(ts_list)
                # res=True
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

def download(ts_list):
    threads = []
    threadID=1
    # 创建新线程
    for tName in _threadList:
        thread = downloadThread(threadID, tName, _workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1
    ts_list_tem=ts_list.copy()
    fillQueue(ts_list_tem)
    # 等待队列清空
    while not _workQueue.empty():
        if _workQueue.full():
            pass
        else :
            fillQueue(ts_list_tem)
    # 通知线程是时候退出
    global _exitFlag
    _exitFlag = 1
    # 等待所有线程完成
    for t in threads:
        t.join()
    return True

# 将TS文件整合在一起
def merge_file(ts_list):
    index = 0
    outfile = ''
    global _dir
    while index < _ts_total:
        file_name = ts_list[index].split('/')[-1].split('?')[0]
        # print(file_name)
        percent = index / _ts_total
        show_progress(percent)
        infile = open(os.path.join(_dir, file_name), 'rb')
        if not outfile:
            global _videoName
            if _videoName=='':
                videoName=file_name.split('.')[0]+'_all'
            outfile = open(os.path.join(_dir, _videoName+'.'+file_name.split('.')[-1]), 'wb')
        outfile.write(infile.read())
        infile.close()
        # 删除临时ts文件
        os.remove(os.path.join(_dir, file_name))
        index += 1
    if outfile:
        outfile.close()

def main():
    start('https://youku.com-www-163.com/20180626/14138_b3d91f17/1000k/hls/index.m3u8','C:/felix/download/shameless/session5/Episode7','无耻之徒第五季第七集')

if __name__ == '__main__':
    session = get_session(50, 50, 3)
    main()
