import os
import time
import urllib

from PyQt5.QtCore import QThread, pyqtSignal

from client import constant, sessionutil, util
from client.DownloadThread import DownloadThread


# 执行后台功能的线程，保证和不影响前台UI的显示
class WorkThread(QThread):
    # 括号里填写信号传递的参数
    signalprocess = pyqtSignal(str)
    signalinfo = pyqtSignal(str)
    signalpercent = pyqtSignal(int)

    def __init__(self, name, path, url):
        self.name = name
        self.path = path
        self.url = url
        super().__init__()

    def __del__(self):
        self.wait()

    def run(self):
        # 进行任务操作
        self.fun(self.name, self.path, self.url)

    def fun(self, name, path, url):
        urllist = url.split(';')
        dirlist = path
        for i in range(len(urllist)):
            index = str(i + 1)
            url = urllist[i]
            if url == '' or 'm3u8' not in url:
                break
            print("开始下载第" + index + "个视频,url:" + urllist[i])
            self.signalprocess.emit("下载第" + index + "个中")
            dir = dirlist
            videoName = name + index
            # 是否需要获取真实的url
            # real_url = m3u8download.get_real_url(url)
            real_url = url
            constant._count = 0
            constant._exitFlag = 0
            self.startwork(real_url, dir, videoName)
        self.signalprocess.emit("完成")
        self.signalinfo.emit("当前没有进行的下载任务")

    def startwork(self, m3u8_url, dir, videoName):
        if dir and not os.path.isdir(dir):
            os.makedirs(dir)
        constant._dir = dir
        constant._videoName = videoName
        self.signalinfo.emit('开始获取文件资源')
        r = sessionutil.session.get(m3u8_url, timeout=10)
        if r.ok:
            body = r.content.decode()
            if body:
                ts_list = []
                body_list = body.split('\n')
                for n in body_list:
                    if n and not n.startswith("#"):
                        ts_list.append(urllib.parse.urljoin(m3u8_url, n.strip()))
                if ts_list:
                    constant._ts_total = len(ts_list)
                    print('ts的总数量为：' + str(constant._ts_total) + '个')
                    # 下载ts文件
                    print('开始下载文件')
                    self.signalinfo.emit('开始下载文件' + 'ts的总数量为：' + str(len(ts_list)) + '个')
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    res = self.download(ts_list)
                    # res=True
                    print('')
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    if res:
                        # 整合ts文件
                        print('\n开始整合文件')
                        self.signalinfo.emit('下载完成' + '，开始整合文件')
                        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                        self.merge_file(ts_list)
                        print('')
                        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    else:
                        self.signalinfo.emit('下载失败')
                        print('下载失败')
        else:
            print(r.status_code)

    # 调用下载数据线程，下载ts_list中的所有链接
    def download(self, ts_list):
        threads = []
        threadID = 1
        # 创建新线程
        for tName in constant._threadList:
            thread = DownloadThread(threadID, tName, constant._workQueue)
            thread.signalpercent.connect(self.callbackpercent)
            thread.start()
            threads.append(thread)
            threadID += 1
        ts_list_tem = ts_list.copy()
        self.fillQueue(ts_list_tem)
        # 等待队列清空
        while not constant._workQueue.empty():
            if constant._workQueue.full():
                pass
            else:
                self.fillQueue(ts_list_tem)
        # 通知线程是时候退出
        constant._exitFlag = 1
        # 等待所有线程完成
        for t in threads:
            t.wait()
        return True

    # 填充线程队列
    def fillQueue(self, nameList):
        constant._queueLock.acquire()
        for word in nameList:
            constant._workQueue.put(word)
            nameList.remove(word)
            if constant._workQueue.full():
                break
        constant._queueLock.release()

    # 将TS文件整合在一起
    def merge_file(self, ts_list):
        index = 0
        outfile = ''
        while index < constant._ts_total:
            file_name = ts_list[index].split('/')[-1].split('?')[0]
            percent = (index + 1) / constant._ts_total
            util.show_progress(percent * 100)
            file_path = os.path.join(constant._dir, file_name)
            if os.path.exists(file_path):
                infile = open(file_path, 'rb')
                if not outfile:
                    if constant._videoName == '':
                        constant._videoName = '未命名'
                    outfile = open(os.path.join(constant._dir, constant._videoName + '.mp4'), 'wb')
                outfile.write(infile.read())
                infile.close()
                # 删除临时ts文件
                os.remove(os.path.join(constant._dir, file_name))
            index += 1
        if outfile:
            outfile.close()

    # 获取当前进度百分比的回调
    def callbackpercent(self, percent):
        self.signalpercent.emit(percent)
