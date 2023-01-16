from firstMainWin import *
from predicet import *
from camera_examine import *
import os


def main():
    app = QApplication(sys.argv)
    main = Ui_MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
