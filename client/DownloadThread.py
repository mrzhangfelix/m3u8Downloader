# 下载单个数据的线程
import os
import threading

from PyQt5.QtCore import QThread, pyqtSignal

from client import constant, sessionUtil, util


class DownloadThread(QThread):
    # 传递当前进度的百分比
    signalpercent = pyqtSignal(int)

    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        super().__init__()

    def __del__(self):
        self.wait()

    def run(self):
        self.download_data(self.q)

    # 下载数据，写入临时文件
    def download_data(self, q):
        while not constant._exitFlag:
            constant._queueLock.acquire()
            if not constant._workQueue.empty():
                data = q.get()
                constant._queueLock.release()
                url = data
                retry = 3
                while retry:
                    try:
                        r = sessionutil.session.get(url, timeout=20)
                        if r.ok:
                            file_name = url.split('/')[-1].split('?')[0]
                            with open(os.path.join(constant._dir, file_name), 'wb') as f:
                                f.write(r.content)
                            # 访问公共资源_count,需要获取线程锁
                            constant._queueLock.acquire()
                            constant._count = constant._count + 1
                            percent = int(constant._count / constant._ts_total * 100)
                            if percent != constant._percent:
                                constant._percent = percent
                                self.signalpercent.emit(percent)
                            util.show_progress(percent)
                            constant._queueLock.release()
                            break
                    except Exception as e:
                        print(e)
                        retry -= 1
                if retry == 0:
                    print('[FAIL]%s' % url)
            else:
                constant._queueLock.release()
