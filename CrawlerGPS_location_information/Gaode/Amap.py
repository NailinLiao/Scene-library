from PyQt5.QtWidgets import QWidget, QPushButton, QMessageBox, QFileDialog, QApplication
from PyQt5.QtCore import QDir, QFileInfo
import os

from main_controler import Crawl_controller


class Traffic_crawl(QWidget):

    def __init__(self, parent=None):

        super(Traffic_crawl, self).__init__(parent)

        self.all_gps_path = []
        self.key_file = ''
        self.save_path = ''

        self.openButton = QPushButton("打开gps文件夹", self)
        self.openButton.clicked.connect(self.open)
        self.openButton.move(50, 50)

        self.open_property_Button = QPushButton("打开key文件", self)
        self.open_property_Button.clicked.connect(self.open_key)
        self.open_property_Button.move(50, 100)

        self.start_Button = QPushButton("开始爬取", self)
        self.start_Button.clicked.connect(self.data_process)
        self.start_Button.move(50, 150)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('交通数据爬取工具')
        self.show()

    def open(self):
        '''
        打开gps文件夹，获取gps文件路径，并创建Infor文件夹
        :return:
        '''
        dir_name = QFileDialog.getExistingDirectory(self, '选择gps文件夹', 'C:/')

        dir = QFileInfo(dir_name).absoluteFilePath()
        dir_base = os.path.basename(dir)

        self.all_gps_path = self.get_files(path=dir)

        for path in self.all_gps_path:
            print(path)

        dir_parent = QFileInfo(dir_name).absolutePath()

        self.save_path = f'{dir_parent}/{dir_base}_Infor'

        if not os.path.exists(self.save_path):

            os.mkdir(self.save_path)

    def get_files(self, path, rule='gps.xlsx'):

        all_path = []

        dirs = QDir(path).entryInfoList(QDir.Files | QDir.Hidden | QDir.NoSymLinks)

        for file_name in dirs:

            file_name = QFileInfo(file_name).absoluteFilePath()

            if file_name.endswith(rule):  # 判断是否是"gps.xlsx"结尾

                all_path.append(file_name)

        return all_path

    def open_key(self):

        self.key_file, _ = QFileDialog.getOpenFileName(self, "选择key文件", filter='*.xlsx')
        print(self.key_file)

    def data_process(self):

        if not self.all_gps_path:
            QMessageBox.information(self, "提示", "gps文件夹为空")

        elif not self.key_file:

            QMessageBox.information(self, "提示", "key文件未载入")

        else:

            for gps_file in self.all_gps_path:

                stop_flag = Crawl_controller(gps_file, self.key_file).process(self.save_path)

                if stop_flag:
                    QMessageBox.information(self, "提示", "今日次数已用尽")
                    break

            QMessageBox.information(self, "提示", "解析完成")


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    player = Traffic_crawl()

    sys.exit(app.exec_())