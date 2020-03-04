# 用于计数文件已经下载的个数
import queue
import threading

_count = 0

# 用于判断线程是否结束。
_exitFlag = 0

# 下载数据线程的总数
threadListSize = 48
# 队列的大小，用于存放线程的队列
queueSize = 96

# 当前下载ts文件的总数
_ts_total = 0

# 当前任务的进度
_percent=0

# 下载的目录
_dir = ''

# 下载的文件名
_videoName = ''

# 线程队列锁
_queueLock = threading.Lock()

# 工作队列
_workQueue = queue.Queue(queueSize)
# 线程列表
_threadList = []

for i in range(threadListSize):
    _threadList.append("Thread-" + str(i))
