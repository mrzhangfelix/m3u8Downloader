#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QAction, QProgressBar,
                             QTextEdit, QGridLayout, QApplication)



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
        self.reviewEdit = QTextEdit()
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.name, 1, 0)
        grid.addWidget(self.nameEdit, 1, 1)

        grid.addWidget(self.path, 2, 0)
        grid.addWidget(self.pathEdit, 2, 1)

        grid.addWidget(self.url, 3, 0)
        grid.addWidget(self.reviewEdit, 3, 1, 2, 1)

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

    def doAction(self):
         name = self.nameEdit.text()
         path = self.nameEdit.text()
         url = self.nameEdit.text()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
