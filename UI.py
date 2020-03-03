#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import threading
import time
import urllib

from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QAction, QProgressBar,
                             QTextEdit, QGridLayout, QApplication)

import m3u8download

# 用于判断线程是否结束。
_exitFlag = 0
# 用于计数文件已经下载的个数
_count = 0

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
        m3u8download._queueLock.acquire()
        if not m3u8download._workQueue.empty():
            data = q.get()
            m3u8download._queueLock.release()
            # print ("%s 使用了 %s" % (threadName, data) + '\n', end='')
            url = data
            retry = 3
            while retry:
                try:
                    r = m3u8download.session.get(url, timeout=20)
                    if r.ok:
                        file_name = url.split('/')[-1].split('?')[0]
                        # print(file_name)
                        with open(os.path.join(m3u8download._dir, file_name), 'wb') as f:
                            f.write(r.content)
                        m3u8download._queueLock.acquire()
                        global _count
                        _count = _count+1
                        proval = int(_count / m3u8download._ts_total * 100)
                        if(proval != ex.pbar.value()):
                            ex.pbar.setValue(proval)
                        m3u8download.show_progress(_count/m3u8download._ts_total)
                        m3u8download._queueLock.release()
                        break
                except Exception as e:
                    print(e)
                    retry -= 1
            if retry == 0 :
                print('[FAIL]%s' % url)
        else:
            m3u8download._queueLock.release()

def download(ts_list):
    threads = []
    threadID=1
    # 创建新线程
    for tName in m3u8download._threadList:
        thread = downloadThread(threadID, tName, m3u8download._workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1
    ts_list_tem=ts_list.copy()
    m3u8download.fillQueue(ts_list_tem)
    # 等待队列清空
    while not m3u8download._workQueue.empty():
        if m3u8download._workQueue.full():
            pass
        else :
            m3u8download.fillQueue(ts_list_tem)
    # 通知线程是时候退出
    global _exitFlag
    _exitFlag = 1
    # 等待所有线程完成
    for t in threads:
        t.join()
    return True


def start( m3u8_url, dir, videoName):
    if dir and not os.path.isdir(dir):
        os.makedirs(dir)
    m3u8download._dir=dir
    m3u8download._videoName=videoName
    ex.info.setText('开始获取文件资源')
    r = m3u8download.session.get(m3u8_url, timeout=10)
    if r.ok:
        body = r.content.decode()
        if body:
            ts_list=[]
            body_list=body.split('\n')
            for n in body_list:
                if n and not n.startswith("#"):
                    ts_list.append(urllib.parse.urljoin(m3u8_url, n.strip()))
            if ts_list:
                m3u8download._ts_total = len(ts_list)
                print('ts的总数量为：'+str(m3u8download._ts_total)+'个')
                # 下载ts文件
                print('开始下载文件')
                ex.info.setText('开始下载文件'+'ts的总数量为：'+str(len(ts_list))+'个')
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                res=download(ts_list)
                # res=True
                print('')
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                if res:
                    # 整合ts文件
                    print('\n开始整合文件')
                    ex.info.setText('下载完成'+'，开始整合文件')
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    m3u8download.merge_file(ts_list)
                    print('')
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                else:
                    ex.info.setText('下载失败')
                    print('下载失败')
    else:
        print(r.status_code)

def fun(name,path,url):
    urllist=url.split(';')
    dirlist=path
    for i in range(len(urllist)):
        index = str(i+1)
        url = urllist[i]
        if url == '':
            break
        print("开始下载第"+index+"个视频,url:"+urllist[i])
        ex.process.setText("下载第"+index+"个中")
        dir = dirlist
        videoName = name+index
        #是否需要获取真实的url
        # real_url = m3u8download.get_real_url(url)
        real_url = url
        global _exitFlag
        global _count
        _count = 0
        _exitFlag = 0
        start(real_url,dir,videoName)
    ex.process.setText("完成")
    ex.info.setText("当前没有进行的下载任务")

# UI界面绘制
class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.name = QLabel('name')
        self.path = QLabel('path')
        self.url = QLabel('url(多个url使用‘;’分割)')
        self.info = QLabel('当前没有进行的下载任务')
        self.process = QLabel('process')

        self.nameEdit = QLineEdit("aa")
        self.pathEdit = QLineEdit("D:\\test")
        self.urlEdit = QTextEdit("https://youku.cdn4-okzy.com/20191126/2980_2373c5f5/1000k/hls/index.m3u8")
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.name, 1, 0)
        grid.addWidget(self.nameEdit, 1, 1)

        grid.addWidget(self.path, 2, 0)
        grid.addWidget(self.pathEdit, 2, 1)

        grid.addWidget(self.url, 3, 0)
        grid.addWidget(self.urlEdit, 3, 1, 2, 1)

        grid.addWidget(self.info, 5, 0)

        grid.addWidget(self.process, 6, 0)
        grid.addWidget(self.pbar, 6, 1)

        self.btn = QPushButton('Start', self)
        # self.btn.move(65, 230)
        self.btn.clicked.connect(self.doAction)
        grid.addWidget(self.btn)
        self.setLayout(grid)

        self.setGeometry(300, 300, 900, 300)
        self.setWindowTitle('m3u8download')
        self.show()


    def doAction(self):
        name = self.nameEdit.text()
        path = self.pathEdit.text()
        url = self.urlEdit.toPlainText()
        ex.info.setText('开始下载')
        QApplication.processEvents()
        fun(name,path,url)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
