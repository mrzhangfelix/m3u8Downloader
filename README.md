# downloader.py

m3u8下载器，支持断点续传

使用方法：

打开m3u8.json

在m3u8list中录入m3u8的url、下载文件保存的地址、保存的文件名

单个视频的下载配置格式如下：
    
    {
      "url": "https://youku.com-www-163.com/20180626/14134_e099ef16/1000k/hls/index.m3u8",
      "dir":"C:/felix/download/shameless/session5/Episode3",
      "videoName":"无耻之徒第五季第三集"
    }
    
可支持多个视频列表配置


# downloader_lite.py 
为精简版下载器

不支持断点续传，下载速度有所提升

使用方法

在代码中录入m3u8的url、下载文件保存的地址、保存的文件名

run('url','dir','videoName')

# downloader_lite2.py
精简版的多线程下载

下载速度较于精简版大幅度提升

使用方法

在代码中录入m3u8的url、下载文件保存的地址、保存的文件名

run('url','dir','videoName')

线程数大小更改

threadListSize = 5

#队列大小更改，队列大小应大于线程数的大小

queueSize = 10
