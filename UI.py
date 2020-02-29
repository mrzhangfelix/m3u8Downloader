#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QAction, QProgressBar,
                             QTextEdit, QGridLayout, QApplication)
from PyQt5.QtCore import QBasicTimer

import m3u8download


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.name = QLabel('name')
        self.path = QLabel('path')
        self.url = QLabel('url')
        self.process = QLabel('process')

        self.nameEdit = QLineEdit()
        self.pathEdit = QLineEdit()
        self.urlEdit = QTextEdit()
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)

        self.timer = QBasicTimer()

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.name, 1, 0)
        grid.addWidget(self.nameEdit, 1, 1)

        grid.addWidget(self.path, 2, 0)
        grid.addWidget(self.pathEdit, 2, 1)

        grid.addWidget(self.url, 3, 0)
        grid.addWidget(self.urlEdit, 3, 1, 2, 1)

        grid.addWidget(self.process, 6, 0)
        grid.addWidget(self.pbar, 6, 1)

        self.btn = QPushButton('Start', self)
        # self.btn.move(65, 230)
        self.btn.clicked.connect(self.doAction)
        grid.addWidget(self.btn)
        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('m3u8download')
        self.show()

    def timerEvent(self, e):
        index,process=m3u8download.getprocess
        if index == -1:
            self.timer.stop()
            return
        self.pbar.setValue(process)


    def doAction(self):
        name = self.nameEdit.text()
        path = self.pathEdit.text()
        url = self.urlEdit.toPlainText()
        m3u8download.fun(name,path,url)
        self.timer.start(500, self)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
