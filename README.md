

# downloader_lite2.py
## 精简版多线程下载

推荐使用这个下载脚本，速度快，能批量下载

## 使用方法

在代码中录入m3u8的url、下载文件保存的地址、保存的文件名

start('url','dir','videoName')

线程数大小更改

threadListSize = 5

#队列大小更改，队列大小应大于线程数的大小

queueSize = 10
