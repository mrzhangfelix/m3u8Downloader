#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QAction, QProgressBar,
                             QTextEdit, QGridLayout, QApplication)
# UI界面绘制
from client.WorkThread import WorkThread


class UI(QWidget):
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
        self.urlEdit = QTextEdit('''
            
        ''')
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
        self.btn.clicked.connect(self.buttonClick)
        grid.addWidget(self.btn)
        self.setLayout(grid)

        self.setGeometry(300, 300, 900, 300)
        self.setWindowTitle('m3u8download')
        self.show()

    # 按钮点击事件
    def buttonClick(self):
        name = self.nameEdit.text()
        path = self.pathEdit.text()
        url = self.urlEdit.toPlainText()
        self.info.setText('开始下载')
        QApplication.processEvents()
        self.thread = WorkThread(name, path, url)
        # 为信号绑定回调函数
        self.thread.signalprocess.connect(self.callbackprocess)
        self.thread.signalinfo.connect(self.callbackinfo)
        self.thread.signalpercent.connect(self.callbackpercent)
        # 启动处理逻辑线程
        self.thread.start()  # 启动线程

    # 改变处理信息的回调函数
    def callbackprocess(self, message):
        self.process.setText(message)

    # 进度信息的回调函数
    def callbackinfo(self, message):
        self.info.setText(message)

    # 进度显示的回调函数
    def callbackpercent(self, percent):
        self.pbar.setValue(percent)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = UI()
    sys.exit(app.exec_())
