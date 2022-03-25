from PySide2.QtGui import QTextCursor

from ui.form import Ui_Form

from PySide2.QtCore import QCoreApplication, Qt, QThread, Signal, QMutex
from PySide2.QtWidgets import QApplication, QWidget, QFileDialog
import sys

from spider_new import run as downImg

class Win(QWidget):
    winMutex = QMutex()
    def __init__(self):
        super(Win, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.toolButton.clicked.connect(self.toolbtclick)

        self.ui.pushButton.clicked.connect(self.run)

        # self.ui.textBrowser.sourceChanged.connect(self.printText)

        # self.stdoutbak = sys.stdout
        # self.stderrbak = sys.stderr
        # sys.stdout = self
        # sys.stderr = self

        # 重定向 stdout, stderr
    def textOut(self, info:str):
        # self.winMutex.lock()
        # s = s.rstrip('\r\n')
        self.ui.textBrowser.insertPlainText(info+'\n')
        # self.stdoutbak.write(info)
        # self.winMutex.unlock()

    def printText(self):
        self.ui.textBrowser.moveCursor(QTextCursor.End)

    def toolbtclick(self):
        dirPath = QFileDialog.getExistingDirectory()
        self.ui.lineEdit.setText(dirPath)

    def run(self):
        if len(self.ui.lineEdit.text()) <= 0:
            self.textOut("未设置路径！")
            return

        self.textOut('启动程序..')
        self.ui.pushButton.setEnabled(False)
        self.ui.toolButton.setEnabled(False)
        self.downImgWorker = DownImgWorker()
        self.downImgWorker._signal.connect(self.setBt)
        self.downImgWorker.dirPath = self.ui.lineEdit.text()
        self.downImgWorker.start()

    def setBt(self):
        self.ui.pushButton.setEnabled(True)
        self.ui.toolButton.setEnabled(True)
        self.textOut("完成")

class DownImgWorker(QThread):

    _signal = Signal()
    dirPath = ''
    def __init__(self):
        super().__init__()

    def run(self) -> None:
        downImg(self.dirPath)
        self._signal.emit()


if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling) #高分屏支持
    app = QApplication([])

    # bot = Bot()
    # bot.start()

    w = Win()
    w.show()

    app.exec_()